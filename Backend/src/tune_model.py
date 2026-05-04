"""
Churn model tuning pipeline with Optuna + MLflow.
Supports XGBoost, SVM, SGD, and KNN.
"""

import os
import tempfile
from typing import Dict, Any, Tuple
import joblib
import mlflow
import mlflow.sklearn
import optuna
import pandas as pd
import shap
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import roc_auc_score
from sklearn.svm import SVC
from sklearn.linear_model import SGDClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.inspection import permutation_importance
from xgboost import XGBClassifier

from data_ingestion import DataIngestor


FEATURE_COLUMNS = [
    "is_verified",
    "days_since_last_login",
    "login_count_7d",
    "failed_login_attempts",
]




class DataLoader:
    def __init__(self, ingestor: DataIngestor):
        self.ingestor = ingestor

    def load_training_data(self) -> Tuple[pd.DataFrame, pd.Series]:
        df = self.ingestor.load_customer_features(add_churn_labels=True)

        missing_features = [col for col in FEATURE_COLUMNS if col not in df.columns]
        if missing_features:
            raise KeyError(f"Missing feature columns: {missing_features}")

        if "churn_label" not in df.columns:
            raise KeyError("Missing target column: churn_label")

        leakage_cols = {"churn_label", "churn_score"}
        bad_features = leakage_cols.intersection(FEATURE_COLUMNS)
        if bad_features:
            raise ValueError(f"Data leakage: remove these from FEATURE_COLUMNS: {bad_features}")

        df["is_verified"] = df["is_verified"].fillna(0).astype(int)

        X = df[FEATURE_COLUMNS].copy()
        y = df["churn_label"].astype(int)

        if X.empty:
            raise RuntimeError("Training features are empty.")

        if y.empty:
            raise RuntimeError("Target is empty.")

        if y.nunique() < 2:
            raise RuntimeError(
                "Target only has one class. Need both churn and non-churn examples."
            )

        return X, y
    
class ModelFactory:
    SUPPORTED_MODELS = ["xgboost", "svm", "sgd", "knn"]

    @staticmethod
    def create_model(model_name: str, params: Dict[str, Any]) -> Any:
        if model_name == "xgboost":
            return XGBClassifier(
                objective="binary:logistic",
                eval_metric="logloss",
                random_state=42,
                **params,
            )

        if model_name == "svm":
            return SVC(
                probability=True,
                random_state=42,
                **params,
            )

        if model_name == "sgd":
            return SGDClassifier(
                loss="log_loss",
                random_state=42,
                **params,
            )

        if model_name == "knn":
            return KNeighborsClassifier(**params)

        raise ValueError(f"Unsupported model: {model_name}")

    @staticmethod
    def get_param_prefix(model_name: str) -> str:
        prefixes = {
            "svm": "svm_",
            "sgd": "sgd_",
            "knn": "knn_",
            "xgboost": "",
        }
        return prefixes.get(model_name, "")


class TuningOrchestrator:
    def __init__(self, X_train: pd.DataFrame, y_train: pd.Series, n_trials: int = 150):
        self.X_train = X_train
        self.y_train = y_train
        self.n_trials = n_trials
        self.study = None

    def _suggest_params(self, trial: optuna.Trial, model_name: str) -> Dict[str, Any]:
        if model_name == "xgboost":
            return {
                "n_estimators": trial.suggest_int("n_estimators", 100, 300),
                "max_depth": trial.suggest_int("max_depth", 3, 8),
                "learning_rate": trial.suggest_float(
                    "learning_rate", 0.01, 0.3, log=True
                ),
                "subsample": trial.suggest_float("subsample", 0.6, 1.0),
                "colsample_bytree": trial.suggest_float(
                    "colsample_bytree", 0.6, 1.0
                ),
            }

        if model_name == "svm":
            return {
                "C": trial.suggest_float("svm_C", 0.1, 10.0, log=True),
                "kernel": trial.suggest_categorical("svm_kernel", ["linear", "rbf"]),
            }

        if model_name == "sgd":
            return {
                "alpha": trial.suggest_float("sgd_alpha", 1e-5, 1e-1, log=True),
            }

        if model_name == "knn":
            return {
                "n_neighbors": trial.suggest_int("knn_n_neighbors", 3, 15),
                "weights": trial.suggest_categorical(
                    "knn_weights", ["uniform", "distance"]
                ),
            }

        raise ValueError(f"Unknown model: {model_name}")

    def _objective(self, trial: optuna.Trial) -> Tuple[float, float, float]:
        model_name = trial.suggest_categorical(
            "model", ModelFactory.SUPPORTED_MODELS
        )

        params = self._suggest_params(trial, model_name)
        model = ModelFactory.create_model(model_name, params)

        print(f"[Trial {trial.number}] model={model_name} params={params}", flush=True)

        auc = cross_val_score(
            model,
            self.X_train,
            self.y_train,
            cv=3,
            scoring="roc_auc",
            error_score="raise",
        ).mean()

        recall = cross_val_score(
            model,
            self.X_train,
            self.y_train,
            cv=3,
            scoring="recall",
            error_score="raise",
        ).mean()

        precision = cross_val_score(
            model,
            self.X_train,
            self.y_train,
            cv=3,
            scoring="precision",
            error_score="raise",
        ).mean()

        with mlflow.start_run(
            nested=True,
            run_name=f"{model_name}_trial_{trial.number}",
        ):
            mlflow.log_params({"model": model_name, **params})
            mlflow.log_metric("roc_auc", auc)
            mlflow.log_metric("recall", recall)
            mlflow.log_metric("precision", precision)

        print(
            f"[Trial {trial.number}] "
            f"auc={auc:.4f} recall={recall:.4f} precision={precision:.4f}",
            flush=True,
        )

        return auc, recall, precision

    def run_tuning(self) -> optuna.Study:
        self.study = optuna.create_study(
            directions=["maximize", "maximize", "maximize"]
        )

        self.study.optimize(self._objective, n_trials=self.n_trials)

        return self.study


def get_model_score(model, X):
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X)

        if proba.ndim == 2 and proba.shape[1] > 1:
            return proba[:, 1]

        return proba.ravel()

    if hasattr(model, "decision_function"):
        return model.decision_function(X)

    raise ValueError(
        f"{type(model).__name__} does not support predict_proba or decision_function."
    )


# class FinalModelTrainer:
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

        elif model_name == "sgd":
            if hasattr(model, "coef_"):
                coef_df = pd.DataFrame(
                    {
                        "feature": X_test.columns,
                        "coefficient": model.coef_.ravel(),
                    }
                ).sort_values("coefficient", key=abs, ascending=False)

                coef_path = os.path.join(tmpdir, "sgd_coefficients.csv")
                coef_df.to_csv(coef_path, index=False)

                ax = coef_df.plot(
                    kind="barh",
                    x="feature",
                    y="coefficient",
                    legend=False,
                    title="SGD Feature Coefficients",
                )
                fig = ax.get_figure()
                coef_plot_path = os.path.join(tmpdir, "sgd_coefficients.png")
                fig.savefig(coef_plot_path, bbox_inches="tight", dpi=150)
                plt.close(fig)

            mlflow.log_artifacts(tmpdir, artifact_path="explainability")

        elif model_name in ["svm", "knn"]:
            sample_y = y_test.loc[X_test_sample.index]

            result = permutation_importance(
                model,
                X_test_sample,
                sample_y,
                scoring="roc_auc",
                n_repeats=10,
                random_state=42,
            )

            importance_df = pd.DataFrame(
                {
                    "feature": X_test.columns,
                    "importance_mean": result.importances_mean,
                    "importance_std": result.importances_std,
                }
            ).sort_values("importance_mean", ascending=False)

            importance_path = os.path.join(tmpdir, "permutation_importance.csv")
            importance_df.to_csv(importance_path, index=False)

            ax = importance_df.plot(
                kind="barh",
                x="feature",
                y="importance_mean",
                legend=False,
                title=f"{model_name.upper()} Permutation Importance",
            )
            fig = ax.get_figure()
            importance_plot_path = os.path.join(tmpdir, "permutation_importance.png")
            fig.savefig(importance_plot_path, bbox_inches="tight", dpi=150)
            plt.close(fig)

            mlflow.log_artifacts(tmpdir, artifact_path="explainability")

        else:
            mlflow.log_param("explainability_status", "unsupported_model")


def main():
    ingestor = DataIngestor()

    try:
        mlflow.set_experiment("churn_multimodel_tuning")

        loader = DataLoader(ingestor)
        X, y = loader.load_training_data()

        print("Loaded columns:", X.columns.tolist(), flush=True)
        print("Training shape:", X.shape, flush=True)
        print("Target distribution:", y.value_counts().to_dict(), flush=True)

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=42,
            stratify=y,
        )

        with mlflow.start_run(run_name="multi_model_study"):
            tuner = TuningOrchestrator(X_train, y_train, n_trials=150)
            study = tuner.run_tuning()

            if not study.best_trials:
                raise RuntimeError("No successful Optuna trials found.")

            best_trial = max(study.best_trials, key=lambda t: t.values[0])

            mlflow.log_params(
                {
                    k: str(v) if isinstance(v, (list, tuple, dict)) else v
                    for k, v in best_trial.params.items()
                }
            )

            mlflow.log_metric("best_roc_auc", best_trial.values[0])
            mlflow.log_metric("best_recall", best_trial.values[1])
            mlflow.log_metric("best_precision", best_trial.values[2])

            print(f"Best trial AUC: {best_trial.values[0]:.4f}", flush=True)
            print(f"Best parameters: {best_trial.params}", flush=True)

        trainer = FinalModelTrainer(X_train, y_train, best_trial)

        final_model = trainer.train_and_save(
            X_test,
            y_test,
            output_path="best_model",
        )

        y_pred_score = get_model_score(final_model, X_test)
        test_auc = roc_auc_score(y_test, y_pred_score)

        print(f"Test AUC: {test_auc:.4f}", flush=True)

        with mlflow.start_run(run_name="final_test_metrics"):
            mlflow.log_metric("final_test_auc", test_auc)

    finally:
        ingestor.close()


if __name__ == "__main__":
    main()