import os
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

import mlflow
import mlflow.sklearn


# 1. Basic configuration
DATA_PATH = os.path.join("data", "salary_data.csv")
EXPERIMENT_NAME = "salary_regression_experiment"
REGISTERED_MODEL_NAME = "SalaryPredictionModel"


def load_data(path=DATA_PATH):
    df = pd.read_csv(path)
    # Drop the index column if present
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])
    return df


def train_test_split_data(df, test_size=0.2, random_state=42):
    X = df[["YearsExperience"]]
    y = df["Salary"]
    return train_test_split(X, y, test_size=test_size, random_state=random_state)


def eval_metrics(y_true, y_pred):
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    r2 = r2_score(y_true, y_pred)
    return rmse, mae, r2


def train_and_log_model(model_name, model, X_train, X_test, y_train, y_test):
    """
    Trains a model, logs parameters, metrics, and the model to MLflow.
    Returns (run_id, rmse).
    """
    with mlflow.start_run(run_name=model_name) as run:
        # Fit model
        model.fit(X_train, y_train)
        preds = model.predict(X_test)

        # Metrics
        rmse, mae, r2 = eval_metrics(y_test, preds)

        # Log parameters (if the model has any)
        if hasattr(model, "get_params"):
            mlflow.log_params(model.get_params())

        # Log metrics
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("mae", mae)
        mlflow.log_metric("r2", r2)

        # Log model
        # Also provide an example input for better MLflow UI experience
        example_input = X_test.head(1)
        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="model",
            input_example=example_input,
            registered_model_name=REGISTERED_MODEL_NAME,  # will create/update registry entry
        )

        run_id = run.info.run_id
        print(f"{model_name} -> run_id={run_id}, RMSE={rmse:.2f}, MAE={mae:.2f}, R2={r2:.4f}")
        return run_id, rmse


def main():
    # 2. Set MLflow experiment
    mlflow.set_experiment(EXPERIMENT_NAME)

    # 3. Load data & split
    df = load_data()
    X_train, X_test, y_train, y_test = train_test_split_data(df)

    # 4. Define models
    models = {
        "LinearRegression": LinearRegression(),
        "DecisionTreeRegressor": DecisionTreeRegressor(random_state=42),
        "RandomForestRegressor": RandomForestRegressor(
            n_estimators=100, random_state=42
        ),
    }

    best_model_name = None
    best_rmse = float("inf")
    best_run_id = None

    # 5. Train & log all models
    for name, model in models.items():
        run_id, rmse = train_and_log_model(
            name, model, X_train, X_test, y_train, y_test
        )
        if rmse < best_rmse:
            best_rmse = rmse
            best_model_name = name
            best_run_id = run_id

    print("\nBest model summary:")
    print(f"Model: {best_model_name}")
    print(f"RMSE: {best_rmse:.2f}")
    print(f"Run ID: {best_run_id}")
    print(
        f"Registered model name in MLflow Model Registry: {REGISTERED_MODEL_NAME}\n"
    )
    print(
        "Next step: open MLflow UI, compare runs, and set the best model to 'Production'."
    )


if __name__ == "__main__":
    main()

