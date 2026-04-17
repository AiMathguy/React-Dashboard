import os
import joblib
import pandas as pd
import shap
from dotenv import load_dotenv
from sqlalchemy import create_engine
from ml_model import prepare_features

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set")

MODEL_PATH = "xgb_best_model.pkl"

# Human-readable labels
FEATURE_LABELS = {
    "login_count_7d": "Low weekly activity",
    "login_count_30d": "Low monthly activity",
    "failed_login_attempts": "Multiple failed logins",
    "days_since_last_login": "Recent inactivity",
    "is_verified": "Account verification status",
}

def load_data() -> pd.DataFrame:
    """Load customer_features table from DB."""
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    # raw_connection() returns a DBAPI2 connection, but may not support context manager
    conn = engine.raw_connection()
    try:
        df = pd.read_sql("SELECT * FROM customer_features", conn)
    finally:
        conn.close()
    return df

def explain_predictions(model, df: pd.DataFrame):
    """Compute SHAP values and return top features per row."""
    X = prepare_features(df)

    explainer = shap.TreeExplainer(model)
    explanation = explainer(X)

    values = explanation.values
    if len(values.shape) == 3:
        # For binary classification, take class 1 (index 1) or class 0 as needed
        values = values[:, :, 0]   # adjust index if necessary

    results = []
    for i in range(len(X)):
        row_shap = values[i]
        pairs = list(zip(X.columns, row_shap))
        pairs.sort(key=lambda x: abs(x[1]), reverse=True)
        top_pairs = pairs[:3]

        results.append({
            "top_features": [
                {
                    "feature": feature,
                    "label": FEATURE_LABELS.get(feature, feature),
                    "impact": float(value),
                }
                for feature, value in top_pairs
            ]
        })
    return results

if __name__ == "__main__":
    print("Loading model...")
    model = joblib.load(MODEL_PATH)
    print("Model loaded.")

    print("Loading customer data...")
    df = load_data()
    print(f"Loaded {len(df)} customers.")

    print("Computing SHAP explanations...")
    results = explain_predictions(model, df)

    # Print results
    for i, res in enumerate(results[:10]):  # first 10 customers
        print(f"\n--- Customer {i+1} ---")
        for feat in res["top_features"]:
            print(f"  {feat['label']}: impact = {feat['impact']:.5f}")