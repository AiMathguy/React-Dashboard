import os
import joblib
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.metrics import roc_auc_score
from xgboost import XGBClassifier

from ml_model import FEATURE_COLUMNS

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
MODEL_PATH = "xgb_best_model.pkl"

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")


def load_training_data() -> tuple[pd.DataFrame, pd.Series]:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

    # Use a connection, not the engine directly, to avoid AttributeError
    with engine.connect() as conn:
        df = pd.read_sql("SELECT * FROM customer_features", conn)

    if df.empty:
        raise RuntimeError("customer_features is empty. Run score_customers.py first.")

    df["is_verified"] = df["is_verified"].astype(int)

    # Temporary simulated target for demo
    y = (
        (df["days_since_last_login"] > 20) |
        (df["login_count_7d"] == 0) |
        (df["failed_login_attempts"] >= 3)
    ).astype(int)

    X = df[FEATURE_COLUMNS]

    return X, y


def hyperparameter_tuning(X: pd.DataFrame, y: pd.Series):
    model = XGBClassifier(
        objective="binary:logistic",
        eval_metric="logloss",
        random_state=42
    )

    param_grid = {
        "n_estimators": [300, 200, 100],
        "max_depth": [3, 5, 7],
        "learning_rate": [0.01, 0.1, 0.2],
        "subsample": [0.7, 1.0],
        "colsample_bytree": [0.7, 1.0]
    }

    grid_search = GridSearchCV(
        estimator=model,
        param_grid=param_grid,
        cv=3,
        scoring="roc_auc",
        n_jobs=-1,
        verbose=1
    )

    grid_search.fit(X, y)
    return grid_search


if __name__ == "__main__":
    X, y = load_training_data()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    grid_search = hyperparameter_tuning(X_train, y_train)

    best_model = grid_search.best_estimator_
    preds = best_model.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, preds)

    print("Best params:", grid_search.best_params_)
    print("Best CV score:", grid_search.best_score_)
    print("Test AUC:", auc)

    joblib.dump(best_model, MODEL_PATH)
    print(f"Saved best model to {MODEL_PATH}")