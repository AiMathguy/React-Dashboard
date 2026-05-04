import os
import tempfile
import joblib
import logging
import pandas as pd
import numpy as np
import shap
import matplotlib.pyplot as plt
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from lime.lime_tabular import LimeTabularExplainer
import mlflow

# Internal imports
from Backend.dashboard_ui.ml_model import prepare_features

logging.basicConfig(level=logging.INFO)

class ModelExplainer:
    def __init__(self, model_path: str = "xgb_best_model.pkl"):
        load_dotenv()
        self.db_url = os.getenv("DATABASE_URL")
        if not self.db_url:
            raise RuntimeError("DATABASE_URL is not set")
        
        self.engine = create_engine(self.db_url, pool_pre_ping=True)
        self.model = self._load_model(model_path)
        self.X = None
        self.shap_values = None
        self.lime_explainer = None

    def _load_model(self, path: str):
        """Loads the serialized model with error handling."""
        if not Path(path).exists():
            logging.error(f"Model file not found: {path}")
            return None
        return joblib.load(path)

    def load_and_prepare_data(self, table_name: str = "customer_features"):
        """Ingests data from SQL and transforms it for ML."""
        query = text(f"SELECT * FROM {table_name}")
        with self.engine.connect() as conn:
            df = pd.read_sql(query, conn)
        
        if df.empty:
            raise ValueError(f"No data found in table: {table_name}")
            
        self.X = prepare_features(df)
        logging.info(f"Features prepared. Shape: {self.X.shape}")

    def initialize_explainers(self):
        """Initializes SHAP and LIME engines."""
        if self.X is None or self.model is None:
            raise RuntimeError("Load data and model before initializing explainers.")

        # SHAP
        self.explainer_shap = shap.TreeExplainer(self.model)
        self.shap_values = self.explainer_shap(self.X)

        # LIME
        self.lime_explainer = LimeTabularExplainer(
            training_data=np.array(self.X),
            feature_names=list(self.X.columns),
            class_names=["Low Risk", "High Risk"],
            mode="classification"
        )

    def plot_shap_summary(self):
        """Generates global feature importance plot."""
        fig, ax = plt.subplots()
        shap.summary_plot(self.shap_values, self.X, show=False)
        st.pyplot(plt.gcf())
        plt.close(fig)  # Prevent memory leaks

    def plot_local_explanation(self, user_index: int = 0):
        """Combines SHAP waterfall and LIME for a single user."""
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("SHAP Waterfall")
            fig = plt.figure()
            shap.plots.waterfall(self.shap_values[user_index], show=False)
            st.pyplot(fig)
            plt.close(fig)

        with col2:
            st.subheader("LIME Explanation")
            exp = self.lime_explainer.explain_instance(
                self.X.iloc[user_index].values,
                self.model.predict_proba,
                num_features=5
            )
            fig = exp.as_pyplot_figure()
            st.pyplot(fig)
            plt.close(fig)

    def plot_dependency(self, feature_name: str):
        """Plots how a specific feature impacts predictions."""
        fig, ax = plt.subplots()
        shap.dependence_plot(
            feature_name,
            self.shap_values.values,
            self.X,
            show=False,
            ax=ax
        )
        st.pyplot(fig)
        plt.close(fig)
        
    def log_explainability_artifacts(model, model_name, X_train, X_test, y_test):
            model_name = str(model_name).lower()

            if model_name == "xgboost":
                print("Using SHAP TreeExplainer", flush=True)
            elif model_name == "sgd":
                print("Using linear coefficients", flush=True)
            elif model_name in ["svm", "knn"]:
                print("Using permutation importance", flush=True)
            else:
                print("Unknown model type", flush=True)

            X_test_sample = X_test.sample(
                n=min(100, len(X_test)),
                random_state=42,
            )
    
            with tempfile.TemporaryDirectory() as tmpdir:
                mlflow.log_param("explainability_mode", "custom_artifacts")
                mlflow.log_param("explainability_sample_size", len(X_test_sample))

            if model_name == "xgboost":
                explainer = shap.TreeExplainer(model)
                shap_values = explainer(X_test_sample)

                shap.plots.bar(shap_values, show=False)
                bar_path = os.path.join(tmpdir, "shap_bar.png")
                plt.gcf().savefig(bar_path, bbox_inches="tight", dpi=150)
                plt.close()

                shap.plots.beeswarm(shap_values, show=False)
                beeswarm_path = os.path.join(tmpdir, "shap_beeswarm.png")
                plt.gcf().savefig(beeswarm_path, bbox_inches="tight", dpi=150)
                plt.close()

                shap.plots.waterfall(shap_values[0], show=False)
                waterfall_path = os.path.join(tmpdir, "shap_waterfall_first_row.png")
                plt.gcf().savefig(waterfall_path, bbox_inches="tight", dpi=150)
                plt.close()

                shap_df = pd.DataFrame(
                    shap_values.values,
                    columns=X_test_sample.columns,
                )
                shap_csv_path = os.path.join(tmpdir, "shap_values_sample.csv")
                shap_df.to_csv(shap_csv_path, index=False)

                mlflow.log_artifacts(tmpdir, artifact_path="explainability")


# Usage in Streamlit
if __name__ == "__main__":
    explainer_tool = ModelExplainer()
    explainer_tool.load_and_prepare_data()
    explainer_tool.initialize_explainers()
    
    st.title("Fraud HQ: Model Explainability")
    explainer_tool.plot_shap_summary()
    
    user_id_idx = st.number_input("Select User Index", min_value=0, value=0)
    explainer_tool.plot_local_explanation(user_index=user_id_idx)