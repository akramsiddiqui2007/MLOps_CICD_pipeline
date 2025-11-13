import os
import pandas as pd
import streamlit as st
import mlflow
import mlflow.sklearn
import datetime

# Evidently (v0.4.17)
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, DataQualityPreset


# ---------------------------------
# Load Production Model from MLflow
# ---------------------------------
MODEL_URI = "models:/SalaryPredictionModel/Production"

@st.cache_resource
def load_model():
    model = mlflow.sklearn.load_model(MODEL_URI)
    return model


# ---------------------------------
# Load reference dataset (required by Evidently)
# ---------------------------------
def load_reference_data():
    df = pd.read_csv("data/salary_data.csv")

    # Clean data
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])

    # For Evidently consistency, rename Salary → PredictedSalary
    df = df.rename(columns={"Salary": "PredictedSalary"})
    return df


reference_df = load_reference_data()


# ---------------------------------
# Evidently Monitoring Function
# ---------------------------------
def log_evidently(years_experience, prediction):
    # Current inference data point
    df = pd.DataFrame([
        {"YearsExperience": years_experience, "PredictedSalary": prediction}
    ])

    # Evidently report
    report = Report(
        metrics=[
            DataDriftPreset(),
            DataQualityPreset()
        ]
    )

    # IMPORTANT: Evidently requires reference_data (cannot be None)
    report.run(reference_data=reference_df, current_data=df)

    # Save the report
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    os.makedirs("monitoring", exist_ok=True)
    report_path = f"monitoring/report_{timestamp}.html"

    report.save_html(report_path)

    return report_path


# ---------------------------------
# Streamlit App UI
# ---------------------------------
def main():
    st.title("Salary Prediction App – MLOps Capstone")
    st.write("""
    Predict salary from years of experience using a Production MLflow model.  
    Each prediction is monitored using Evidently to detect data drift and quality issues.
    """)

    model = load_model()

    # Sidebar Inputs
    st.sidebar.header("Input Features")
    years_exp = st.sidebar.slider(
        "Years of Experience", 
        min_value=0.0, 
        max_value=20.0, 
        value=3.0, 
        step=0.1
    )

    if st.button("Predict Salary"):
        input_df = pd.DataFrame({"YearsExperience": [years_exp]})
        prediction = model.predict(input_df)[0]

        st.subheader("Prediction Result")
        st.write(f"**Estimated Salary:** ${prediction:,.2f}")

        # Generate Evidently report
        try:
            report_file = log_evidently(years_exp, prediction)
            st.success("Monitoring Report Generated!")
            st.write(f"📄 Report saved to: `{report_file}`")
        except Exception as e:
            st.error(f"Error generating Evidently report: {e}")


if __name__ == "__main__":
    main()

