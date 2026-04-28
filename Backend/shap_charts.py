
import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

def load_table(table_name: str) -> pd.DataFrame:
    query = text(f"SELECT * FROM {table_name}")
    with engine.connect() as conn:
        rows = conn.execute(query).mappings().all()
    return pd.DataFrame(rows)

def load_users_df() -> pd.DataFrame:
    return load_table("users")

def load_activity_df() -> pd.DataFrame:
    return load_table("user_activity_log")

def load_features_df() -> pd.DataFrame:
    return load_table("customer_features")

def load_predictions_df() -> pd.DataFrame:
    return load_table("customer_predictions")


import joblib
import shap
import matplotlib.pyplot as plt
from ml_model import prepare_features

model = joblib.load("xgb_best_model.pkl")
X = prepare_features(ml_df)

explainer = shap.TreeExplainer(model)
shap_values = explainer(X)


plt.figure()
shap.summary_plot(shap_values, X, show=False)
plt.tight_layout()
st.pyplot(plt.gcf())
plt.clf()


user_index = 0

plt.figure()
shap.plots.waterfall(shap_values[user_index], show=False)
st.pyplot(plt.gcf())
plt.clf()

feature_name = "days_since_last_login"

plt.figure()
shap.dependence_plot(
    feature_name,
    shap_values.values,
    X,
    show=False
)
plt.tight_layout()
st.pyplot(plt.gcf())
plt.clf()



from lime.lime_tabular import LimeTabularExplainer
import numpy as np

feature_names = list(X.columns)

lime_explainer = LimeTabularExplainer(
    training_data=np.array(X),
    feature_names=feature_names,
    class_names=["Low Risk", "High Risk"],
    mode="classification"
)

user_index = 0

exp = lime_explainer.explain_instance(
    X.iloc[user_index].values,
    model.predict_proba,
    num_features=5
)

fig = exp.as_pyplot_figure()
st.pyplot(fig)
plt.clf()