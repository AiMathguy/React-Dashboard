import os
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, classification_report

from ml_model import train_model, prepare_features, load_model, predict

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

engine = create_engine(DATABASE_URL)

# Load engineered features
df = pd.read_sql("SELECT * FROM customer_features", engine)

if df.empty:
    raise RuntimeError("customer_features is empty. Run score_customers.py first.")

# Simulated churn label for demo/training
np.random.seed(42)
df["churn_label"] = (
    (df["days_since_last_login"] > np.random.randint(10, 40, len(df))) |
    (df["login_count_7d"] < np.random.randint(1, 5, len(df))) |
    (df["failed_login_attempts"] > np.random.randint(2, 6, len(df)))
).astype(int)

# Split for evaluation
train_df, test_df = train_test_split(
    df,
    test_size=0.2,
    random_state=42,
    stratify=df["churn_label"]
)

# Train and save model
model = train_model(train_df)

# Evaluate on holdout data
X_test = prepare_features(test_df)
y_test = test_df["churn_label"]
y_prob = predict(model, test_df)
y_pred = (y_prob >= 0.5).astype(int)

auc = roc_auc_score(y_test, y_prob)

print("Model trained successfully.")
print("Rows used for training:", len(train_df))
print("Rows used for testing:", len(test_df))
print("Test ROC-AUC:", round(auc, 4))
print("\nClassification report:\n")
print(classification_report(y_test, y_pred))

# Optional sanity check that saved model loads back
loaded_model = load_model()
if loaded_model is None:
    raise RuntimeError("Model file was not saved correctly.")

print("Saved model loaded successfully.")