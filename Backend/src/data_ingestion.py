import os
import logging
from pathlib import Path
from typing import Optional
import pandas as pd
from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

class DataIngestor:
    
    def __init__(self, output_dir: str = "backend/data"):
        load_dotenv()

        self.db_url = os.getenv("DATABASE_URL")
        if not self.db_url:
            raise RuntimeError("DATABASE_URL not found in environment.")

        self.engine = create_engine(self.db_url, pool_pre_ping=True)

        self.output_path = Path(output_dir).resolve()
        self.output_path.mkdir(parents=True, exist_ok=True)

        self.tables = inspect(self.engine).get_table_names()

    def list_available_tables(self) -> list[str]:
        return sorted(self.tables)

    def table_exists(self, table_name: str) -> bool:
        return table_name in self.tables

    def load_table(self, table_name: str, limit: Optional[int] = None) -> pd.DataFrame:
        if not self.table_exists(table_name):
            raise ValueError(f"Table not found: {table_name}")

        query = f"SELECT * FROM {table_name}"
        if limit is not None:
            query += f" LIMIT {limit}"

        with self.engine.connect() as conn:
            df = pd.read_sql(query, conn)

        logging.info(f"Loaded {len(df)} rows from {table_name}")
        return df

    def load_customer_features(self, add_churn_labels: bool = True) -> pd.DataFrame:
        df = self.load_table("customer_features")

        if df.empty:
            raise RuntimeError("customer_features table is empty")

        if add_churn_labels:
            required_cols = self.tables

            missing = [col for col in required_cols if col not in df.columns]
            if missing:
                raise KeyError(f"Missing required columns for churn labeling: {missing}")

            conditions = pd.DataFrame({
                "not_verified": df["is_verified"].fillna(0).astype(int) == 0,
                "inactive_60d": df["days_since_last_login"].fillna(999) > 60,
                "no_recent_logins": df["login_count_7d"].fillna(0) == 0,
                "many_failed_logins": df["failed_login_attempts"].fillna(0) >= 3,
                "no_active_subscription": df["has_active_subscription"].fillna(0).astype(int) == 0,
            })

            df["churn_score"] = conditions.sum(axis=1)
            df["churn_label"] = (df["churn_score"] >= 3).astype(int)

            logging.info(
                f"Added churn labels: {df['churn_label'].value_counts().to_dict()}"
            )

        logging.info(f"customer_features columns: {df.columns.tolist()}")
        return df

def export_all(self):
    failed_tables = []

    try:
        available_tables = set(self.list_available_tables())
        logging.info(f"Available tables: {sorted(available_tables)}")

        for table in self.tables:
            if table not in available_tables:
                logging.error(f"Table not found: {table}")
                failed_tables.append(table)
                continue

            try:
                self._export_table(table)
            except Exception as e:
                logging.error(f"Failed to export {table}: {e}")
                failed_tables.append(table)

        master_df = self.build_master_df(
            self.load_table("users"),
            self.load_table("customer_features"),
            self.load_table("churn_predictions"),
        )

        master_path = self.output_path / "master_customer_data.csv"
        master_df.to_csv(master_path, index=False)

        logging.info(f"Exported master_customer_data -> {master_path}")

        if failed_tables:
            raise RuntimeError(f"Export failed for tables: {failed_tables}")

        logging.info("All requested tables exported successfully.")

    finally:
        self.engine.dispose()

    def export_table(self, table_name: str):
        if not self.table_exists(table_name):
            raise ValueError(f"Table not found: {table_name}")
        self._export_table(table_name)

    def _export_table(self, table_name: str):
        file_path = self.output_path / f"{table_name}.csv"
        query = f"SELECT * FROM {table_name}"

        total_rows = 0
        first_chunk = True

        with self.engine.connect() as conn:
            for chunk in pd.read_sql_query(query, conn, chunksize=5000):
                rows = len(chunk)
                total_rows += rows

                chunk.to_csv(
                    file_path,
                    mode="w" if first_chunk else "a",
                    index=False,
                    header=first_chunk,
                )
                first_chunk = False

        if total_rows == 0:
            logging.warning(f"Table {table_name} is empty. No CSV rows written.")
        else:
            logging.info(f"Exported {table_name}: {total_rows} rows -> {file_path}")

    def build_master_df(users, features, preds):
        # normalize IDs
        users["id"] = users["id"].astype(str)
        features["user_id"] = features["user_id"].astype(str)
        preds["user_id"] = preds["user_id"].astype(str)

        df = (
            users.merge(features, left_on="id", right_on="user_id", how="left")
                .merge(preds, left_on="id", right_on="user_id", how="left", suffixes=("", "_pred"))
        )

        # drop duplicate user_id columns from merges
        df.drop(columns=[c for c in df.columns if c == "user_id"], inplace=True)
        df.to_csv(self.output_path / "master_customer_data.csv", index=False)

        return df

    def close(self):
        self.engine.dispose()


if __name__ == "__main__":
    ingestor = DataIngestor()
    ingestor.export_all()