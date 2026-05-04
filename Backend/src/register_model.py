
# class register_model:
#     def __init__(self, model, X_train, y_train):
#         self.model = model
#         self.X_train = X_train
#         self.y_train = y_train

#     def register(self, output_path, model_name):
#         import mlflow
#         from mlflow import sklearn
#         from mlflow.models import ModelFactory
#         import joblib

#             mlflow.set_tracking_uri("http://localhost:5000")
#             mlflow.set_experiment("churn_prediction")

#             with mlflow.start_run(run_name=model_name) as run:
#                 mlflow.log_params(
#                     {
#                         "model_type": type(self.model).__name__,
#                         "training_samples": len(self.X_train),
#                     }
#                 )
#                 mlflow.sklearn.log_model(self.model, artifact_path=output_path)
            