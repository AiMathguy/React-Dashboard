import os
import joblib
import pandas as pd
from xgboost import XGBClassifier

MODEL_PATH = "churn_model.pkl"

FEATURE_COLUMNS = [
    "login_count_7d",
    "login_count_30d",
    "failed_login_attempts",
    "days_since_last_login",
    "is_verified",
]


def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["is_verified"] = df["is_verified"].astype(int)
    return df[FEATURE_COLUMNS]


def train_model(df: pd.DataFrame):
    X = prepare_features(df)
    y = df["churn_label"]

    params = {
        "objective": "binary:logistic",
        "max_depth": 4,
        "learning_rate": 0.1,
        "n_estimators": 100,
        "alpha": 10,
        "eval_metric": "logloss",
        "random_state": 42,
    }

    model = XGBClassifier(**params)
    model.fit(X, y)

    joblib.dump(model, MODEL_PATH)
    return model


def load_model():
    if not os.path.exists(MODEL_PATH):
        return None
    return joblib.load(MODEL_PATH)


def predict(model, df: pd.DataFrame):
    X = prepare_features(df)
    return model.predict_proba(X)[:, 1]