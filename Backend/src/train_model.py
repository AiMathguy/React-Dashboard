import os
import logging
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, classification_report
from dotenv import load_dotenv
from src.tune_model import FinalModelTrainer
from src.data_ingestion import DataIngestor

# Internal imports
from Backend.dashboard_ui.ml_model import train_model, prepare_features, load_model, predict

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


class ChurnModelManager:
    def __init__(self, db_url: str = None):
        """Initializes the manager and database connection."""
        load_dotenv()
        self.db_url = db_url or os.getenv("DATABASE_URL")
        if not self.db_url:
            raise ValueError("DATABASE_URL must be provided or set in environment variables.")
        
        self.engine = create_engine(self.db_url)
        self.df = None
        self.model = None

    def fetch_data(self, table_name: str = "customer_features"):
        """Loads features from the database with error handling."""
        """Loads customer features using DataIngestor and adds churn labels."""
        try:
            ingestor = DataIngestor()
            self.df = ingestor.load_customer_features(add_churn_labels=True)

            if self.df.empty:
                raise ValueError("customer_features table is empty.")

            logging.info(f"Successfully loaded {len(self.df)} rows from customer_features.")
            logging.info(
                f"Churn distribution: {self.df['churn_label'].value_counts().to_dict()}"
            )

        except Exception as e:
            logging.error(f"Failed to fetch data: {e}")
            raise

        finally:
            try:
                ingestor.close()
            except Exception:
                pass
    def inject_simulated_labels(self):
        """Simulates churn labels for demo/training purposes."""
        if self.df is None:
            raise RuntimeError("Dataframe is empty. Call fetch_data() first.")
        
        np.random.seed(42)
        n = len(self.df)
        conditions = pd.DataFrame({
        "not_verified": self.df["is_verified"] == 0,
        "inactive_60d": self.df["days_since_last_login"] > 60,
        "no_recent_logins": self.df["login_count_7d"] == 0,
        "many_failed_logins": self.df["failed_login_attempts"] >= 3,
        "no_active_subscription": self.df["has_active_subscription"] == 0,
        })

        self.df["churn_score"] = conditions.sum(axis=1)
        self.df["churn_label"] = self.df["churn_score"] >= 3
        self.df["churn_label"] = self.df["churn_label"].astype(int)

        X = self.df[[
            "is_verified",
            "days_since_last_login",
            "login_count_7d",
            "failed_login_attempts",
            "has_active_subscription",
        ]]

        y = self.df["churn_label"]
    def run_training_pipeline(self, test_size: float = 0.2):
        """Executes splitting, training, and evaluation."""
        # 1. Split Data
        train_df, test_df = train_test_split(
            self.df,
            test_size=test_size,
            random_state=42,
            stratify=self.df["churn_label"]
        )

        # 2. Train
        self.model = train_model(train_df)
        logging.info("Model training complete.")

        # 3. Evaluate
        metrics = self._evaluate(test_df)
        return metrics

    def _evaluate(self, test_df: pd.DataFrame):
        """Internal helper to calculate metrics."""
        y_test = test_df["churn_label"]
        y_prob = predict(self.model, test_df)
        y_pred = (y_prob >= 0.5).astype(int)

        auc = roc_auc_score(y_test, y_prob)
        report = classification_report(y_test, y_pred)
        
        return {
            "auc": auc,
            "report": report,
            "train_size": len(self.df) - len(test_df),
            "test_size": len(test_df)
        }

    def verify_persistence(self):
        """Ensures the model can be reloaded from disk."""
        loaded = load_model()
        if loaded is None:
            raise IOError("Model persistence check failed: Model not found on disk.")
        logging.info("Model persistence verified.")
        return True
    


class FinalModelTrainer:
#     def __init__(self, X_train, y_train, best_trial):
#         self.X_train = X_train
#         self.y_train = y_train
#         self.best_params = best_trial.params
#         self.best_value = best_trial.values[0]

#     def _clean_params(self, model_name: str, raw_params: Dict[str, Any]) -> Dict[str, Any]:
#         prefix = ModelFactory.get_param_prefix(model_name)
#         cleaned = {}

#         for key, value in raw_params.items():
#             if key == "model":
#                 continue

#             if prefix and key.startswith(prefix):
#                 cleaned[key[len(prefix):]] = value
#             else:
#                 cleaned[key] = value

#         return cleaned

#     def train_and_save(self, X_test, y_test, output_path="best_model"):
#         model_name = self.best_params["model"]
#         clean_params = self._clean_params(model_name, self.best_params)

#         model = ModelFactory.create_model(model_name, clean_params)
#         model.fit(self.X_train, self.y_train)

#         joblib.dump(model, f"{output_path}.pkl")

#         with mlflow.start_run(run_name="final_model"):
#             mlflow.log_param("final_model_type", model_name)
#             mlflow.log_params(clean_params)

#             model_info = mlflow.sklearn.log_model(
#             sk_model=model,
#             artifact_path=output_path,    # just use this, drop the 'model' positional arg
#             input_example=X_test[:5],    # fixes the signature warning too
#         )
#             eval_data = X_test.copy()
#             eval_data["label"] = y_test.values

#             try:
#                 mlflow.models.evaluate(
#                     model_info.model_uri,
#                     eval_data,
#                     targets="label",
#                     model_type="classifier",
#                     evaluator_config={
#                         "log_explainer": False,
#                     },
#                 )
#             except Exception as e:
#                 print(f"MLflow evaluation skipped because it failed: {e}", flush=True)

#             log_explainability_artifacts(
#                 model=model,
#                 model_name=model_name,
#                 X_train=self.X_train,
#                 X_test=X_test,
#                 y_test=y_test,
#             )

#         return model


if __name__ == "__main__":
    # Execution Block
    try:
        manager = ChurnModelManager()
        manager.fetch_data()
        manager.inject_simulated_labels()
        results = manager.run_training_pipeline()

        print(f"\n--- Results ---")
        print(f"ROC-AUC: {results['auc']:.4f}")
        print(f"Report:\n{results['report']}")
        
        manager.verify_persistence()
    except Exception as e:
        print(f"Pipeline failed: {e}")