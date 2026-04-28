"""
Churn model tuning pipeline with Optuna + MLflow.
Supports XGBoost, Neural Network (Keras), SVM, SGD, and KNN.
"""

import os
import joblib
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import roc_auc_score
from xgboost import XGBClassifier
from sklearn.svm import SVC
from sklearn.linear_model import SGDClassifier
from sklearn.neighbors import KNeighborsClassifier
from tensorflow import keras
import optuna
import mlflow
from typing import Dict, Any, Tuple, Optional

# Assuming this exists – if not, define FEATURE_COLUMNS here.
try:
    from ml_model import FEATURE_COLUMNS
except ImportError:
    FEATURE_COLUMNS = []  # fallback; should be defined

load_dotenv()


class DataLoader:
    """Responsible for loading and preparing data from the database."""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        
    def load_training_data(self) -> Tuple[pd.DataFrame, pd.Series]:
        """Loads customer_features table and creates target column."""
        engine = create_engine(self.database_url, pool_pre_ping=True)
        with engine.connect() as conn:
            df = pd.read_sql("SELECT * FROM customer_features", conn)
        
        if df.empty:
            raise RuntimeError("customer_features table is empty")
        
        df["is_verified"] = df["is_verified"].astype(int)
        # Churn definition: inactive or suspicious
        y = (
            (df["days_since_last_login"] > 20) |
            (df["login_count_7d"] == 0) |
            (df["failed_login_attempts"] >= 3)
        ).astype(int)
        X = df[FEATURE_COLUMNS]
        return X, y


class ModelFactory:
    """Creates model instances with given hyperparameters."""
    
    SUPPORTED_MODELS = ["xgboost", "neural_network", "svm", "sgd", "knn"]
    
    @staticmethod
    def create_model(model_name: str, params: Dict[str, Any], input_dim: Optional[int] = None) -> Any:
        """
        Factory method to create a model.
        
        Args:
            model_name: One of SUPPORTED_MODELS
            params: Hyperparameters (already cleaned of prefixes)
            input_dim: Required for neural network (number of features)
        
        Returns:
            Unfitted model instance (sklearn-like or Keras)
        """
        if model_name == "xgboost":
            return XGBClassifier(
                objective="binary:logistic",
                eval_metric="logloss",
                random_state=42,
                **params
            )
        elif model_name == "svm":
            return SVC(probability=True, random_state=42, **params)
        elif model_name == "sgd":
            return SGDClassifier(random_state=42, **params)
        elif model_name == "knn":
            return KNeighborsClassifier(**params)
        elif model_name == "neural_network":
            if input_dim is None:
                raise ValueError("input_dim required for neural network")
            model = keras.Sequential()
            hidden_layers = params["hidden_layers"]  # list of units
            model.add(keras.layers.Dense(hidden_layers[0], activation="relu", input_shape=(input_dim,)))
            for units in hidden_layers[1:]:
                model.add(keras.layers.Dense(units, activation="relu"))
            model.add(keras.layers.Dense(1, activation="sigmoid"))
            model.compile(
                optimizer=params["optimizer"],
                loss="binary_crossentropy",
                metrics=["AUC"]
            )
            return model
        else:
            raise ValueError(f"Unsupported model: {model_name}")
    
    @staticmethod
    def get_param_prefix(model_name: str) -> str:
        """Returns the prefix used for hyperparameter names in Optuna."""
        prefixes = {
            "svm": "sv_",
            "sgd": "sgd_",
            "knn": "knn_",
            "xgboost": "",      # no prefix
            "neural_network": "nn_"
        }
        return prefixes.get(model_name, "")


class TuningOrchestrator:
    """Handles Optuna hyperparameter tuning for multiple models."""
    
    def __init__(self, X_train: np.ndarray, y_train: np.ndarray, n_trials: int = 150):
        self.X_train = X_train
        self.y_train = y_train
        self.n_trials = n_trials
        self.study = None
        
    def _suggest_params(self, trial: optuna.Trial, model_name: str) -> Dict[str, Any]:
        """Suggest hyperparameters for a given model."""
        if model_name == "xgboost":
            return {
                "n_estimators": trial.suggest_int("n_estimators", 100, 500),
                "max_depth": trial.suggest_int("max_depth", 3, 10),
                "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
                "subsample": trial.suggest_float("subsample", 0.5, 1.0),
                "colsample_bytree": trial.suggest_float("colsample_bytree", 0.4, 1.0),
            }
        elif model_name == "svm":
            return {
                "C": trial.suggest_float("sv_C", 0.1, 10.0, log=True),
                "kernel": trial.suggest_categorical("sv_kernel", ["linear", "rbf"]),
            }
        elif model_name == "sgd":
            return {
                "alpha": trial.suggest_float("sgd_alpha", 1e-5, 1e-1, log=True),
            }
        elif model_name == "knn":
            return {
                "n_neighbors": trial.suggest_int("knn_n_neighbors", 3, 15),
                "weights": trial.suggest_categorical("knn_weights", ["uniform", "distance"]),
            }
        elif model_name == "neural_network":
            return {
                "hidden_layers": trial.suggest_categorical("nn_hidden_layers", [[64, 32], [128, 64], [256, 128, 64]]),
                "optimizer": trial.suggest_categorical("nn_optimizer", ["adam", "sgd"]),
                "epochs": trial.suggest_int("nn_epochs", 10, 50),
                "batch_size": trial.suggest_int("nn_batch_size", 16, 128, log=True),
            }
        else:
            raise ValueError(f"Unknown model: {model_name}")
    
    def _objective(self, trial: optuna.Trial) -> float:
        """Objective function for Optuna: maximize ROC-AUC."""
        # 1. Choose model
        model_name = trial.suggest_categorical("model", ModelFactory.SUPPORTED_MODELS)
        
        # 2. Get hyperparameters
        params = self._suggest_params(trial, model_name)
        
        # 3. Create model
        if model_name == "neural_network":
            # Neural network needs input dim and special handling (no cross_val_score)
            model = ModelFactory.create_model(
                model_name, params, input_dim=self.X_train.shape[1]
            )
            # Use a fixed validation split inside the trial
            X_tr, X_val, y_tr, y_val = train_test_split(
                self.X_train, self.y_train, test_size=0.2, random_state=trial.number
            )
            history = model.fit(
                X_tr, y_tr,
                epochs=params["epochs"],
                batch_size=params["batch_size"],
                verbose=0,
                validation_data=(X_val, y_val)
            )
            auc = history.history['val_auc'][-1] if 'val_auc' in history.history else 0.0
        else:
            model = ModelFactory.create_model(model_name, params)
            auc = cross_val_score(model, self.X_train, self.y_train, cv=3, scoring="roc_auc").mean()
        
        # Log to MLflow as nested run
        with mlflow.start_run(nested=True, run_name=f"{model_name}_trial_{trial.number}"):
            mlflow.log_params({**{"model": model_name}, **params})
            mlflow.log_metric("roc_auc", auc)
        
        return auc
    
    def run_tuning(self) -> optuna.Study:
        """Run the Optuna study and return the study object."""
        self.study = optuna.create_study(direction="maximize")
        self.study.optimize(self._objective, n_trials=self.n_trials)
        return self.study


class FinalModelTrainer:
    """Trains the best model on full training data and saves it."""
    
    def __init__(self, X_train: np.ndarray, y_train: np.ndarray, study: optuna.Study):
        self.X_train = X_train
        self.y_train = y_train
        self.best_params = study.best_params
        self.best_value = study.best_value
        
    def _clean_params(self, model_name: str, raw_params: Dict[str, Any]) -> Dict[str, Any]:
        """Remove model selection key and strip prefixes from parameter names."""
        prefix = ModelFactory.get_param_prefix(model_name)
        cleaned = {}
        for key, value in raw_params.items():
            if key == "model":
                continue
            if prefix and key.startswith(prefix):
                # Remove prefix (e.g., 'sv_C' -> 'C')
                new_key = key[len(prefix):]
                cleaned[new_key] = value
            else:
                cleaned[key] = value
        return cleaned
    
    def train_and_save(self, output_path: str = "best_model"):
        """Train the best model and save to disk (joblib for sklearn, .keras for NN)."""
        best_model_name = self.best_params["model"]
        raw_params = {k: v for k, v in self.best_params.items() if k != "model"}
        cleaned_params = self._clean_params(best_model_name, self.best_params)
        
        print(f"Training final model: {best_model_name}")
        print(f"Hyperparameters: {cleaned_params}")
        
        if best_model_name == "neural_network":
            model = ModelFactory.create_model(
                best_model_name,
                cleaned_params,
                input_dim=self.X_train.shape[1]
            )
            model.fit(
                self.X_train, self.y_train,
                epochs=cleaned_params["epochs"],
                batch_size=cleaned_params["batch_size"],
                verbose=1
            )
            save_path = f"{output_path}.keras"
            model.save(save_path)
            print(f"Keras model saved to {save_path}")
        else:
            model = ModelFactory.create_model(best_model_name, cleaned_params)
            model.fit(self.X_train, self.y_train)
            save_path = f"{output_path}.pkl"
            joblib.dump(model, save_path)
            print(f"Sklearn model saved to {save_path}")
        
        return model


def main():
    # 1. Configuration
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL environment variable not set")
    
    mlflow.set_tracking_uri("http://localhost:5000")
    mlflow.set_experiment("churn_multimodel_tuning")
    
    # 2. Load data
    loader = DataLoader(database_url)
    X, y = loader.load_training_data()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # 3. Run tuning inside a main MLflow run
    with mlflow.start_run(run_name="multi_model_study"):
        tuner = TuningOrchestrator(X_train, y_train, n_trials=150)
        study = tuner.run_tuning()
        
        # Log best results
        mlflow.log_params(study.best_params)
        mlflow.log_metric("best_roc_auc", study.best_value)
        print(f"Best trial AUC: {study.best_value:.4f}")
        print(f"Best parameters: {study.best_params}")
    
    # 4. Train and save final model
    trainer = FinalModelTrainer(X_train, y_train, study)
    final_model = trainer.train_and_save("best_model")
    
    # Optional: evaluate on test set
    if best_model_name != "neural_network":
        y_pred_proba = final_model.predict_proba(X_test)[:, 1]
        test_auc = roc_auc_score(y_test, y_pred_proba)
        print(f"Test AUC: {test_auc:.4f}")


if __name__ == "__main__":
    main()