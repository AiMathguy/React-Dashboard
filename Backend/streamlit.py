import streamlit as st
import numpy as np
import pandas as pd


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


import pandas as pd
from load_sql_data import load_users_df, load_features_df, load_predictions_df

users_df = load_users_df()
features_df = load_features_df()
preds_df = load_predictions_df()

ml_df = (
    users_df.merge(features_df, left_on="id", right_on="user_id", how="inner")
            .merge(preds_df, left_on="id", right_on="user_id", how="left", suffixes=("", "_pred"))
)

print(ml_df.head())


import joblib
import shap
import matplotlib.pyplot as plt
from ml_model import prepare_features

model = joblib.load("xgb_best_model.pkl")
X = prepare_features(ml_df)

explainer = shap.TreeExplainer(model)
shap_values = explainer(X)


import streamlit as st

# 1. Set page to wide mode (optional but recommended for landscape layout)
st.set_page_config(layout="wide")

# 2. Create 4 columns with a small gap between them
col1, col2, col3, col4 = st.columns(4, gap="small")

# 3. Add a KPI metric to each column
with col1:
    st.metric(label="Total Sales", value="$128K", delta="+12%")
with col2:
    st.metric(label="Conversion Rate", value="5.6%", delta="-1.2%")
with col3:
    st.metric(label="Active Users", value="1,234", delta="+5%")
with col4:
    st.metric(label="Avg. Order Value", value="$48", delta="+$2")

col11, col22 = st.columns(2,gap="small")

with col11:
    with st.container(height=300):
        
        map_data = pd.DataFrame(
        np.random.randn(1000, 2) / [2, 2] + [37.76, -12.4],
        columns=['lat', 'lon'])
    
        st.map(map_data,use_container_width=True)

with col22:
    with st.container(height=300):
        chart_data = pd.DataFrame(
        np.random.randn(20, 3),
        columns=['a', 'b', 'c'])

        st.line_chart(chart_data)



import pandas as pd
df = pd.DataFrame({
  'first column': [1, 2, 3, 4],
  'second column': [10, 20, 30, 40]
})
# Main page content

st.sidebar.markdown("# Main page 🎈")