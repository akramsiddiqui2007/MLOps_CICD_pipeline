# 📈 Salary Prediction – End-to-End MLOps Capstone Project

This project demonstrates a complete **end-to-end MLOps workflow** using:

- **MLflow** for experiment tracking and model registry  
- **Streamlit** for model deployment  
- **Evidently** for real-time model monitoring  
- **Python (scikit-learn)** for model development  
- **Local CSV dataset** as the training source  

The system predicts **Salary** based on **Years of Experience** and includes a full monitoring setup where each prediction generates an Evidently drift + data-quality analysis report.

---

## 🚀 Key Features

### ✅ **Model Development**
- Linear Regression  
- Decision Tree Regressor  
- Random Forest Regressor  
- Automatic experiment logging using MLflow  

### ✅ **MLflow Tracking & Registry**
- Tracks metrics, parameters & artifacts  
- Stores models  
- Select best model & promote to **Production** stage

### ✅ **Model Deployment (Streamlit)**
- Loads Production model dynamically from MLflow  
- Clean UI for user input  
- Predicts Salary in real-time  

### ✅ **Monitoring (Evidently 0.4.17)**
- Each prediction generates:
  - Data Drift Analysis  
  - Data Quality Checks  
- Reports stored automatically under `/monitoring`  

---

# 🏗 Architecture Diagram

### **ASCII Diagram**

                      ┌───────────────────────────┐
                      │       Raw Dataset         │
                      │   salary_data.csv (CSV)   │
                      └───────────────┬───────────┘
                                      │
                                      ▼
                     ┌──────────────────────────────┐
                     │    Model Training Pipeline    │
                     │         (train.py)            │
                     │  • Linear Regression          │
                     │  • Decision Tree              │
                     │  • Random Forest              │
                     └───────────────┬──────────────┘
                                     │
                                     ▼
             ┌────────────────────────────────────────────────┐
             │                MLflow Tracking                  │
             │  • Metrics & Params                            │
             │  • Saved Models                                │
             └───────────────┬────────────────────────────────┘
                             │
                             ▼
       ┌───────────────────────────────────────────────────────────┐
       │                   MLflow Model Registry                   │
       │   Best model promoted to PRODUCTION stage                 │
       └───────────────┬──────────────────────────────────────────┘
                       │
                       ▼
      ┌────────────────────────────────────────────────────────────┐
      │                      Streamlit Deployment                   │
      │                          (app.py)                          │
      │  • Loads Production model via MLflow                       │
      │  • Predicts Salary                                         │
      │  • Generates Evidently drift reports                       │
      └─────────────────────────┬──────────────────────────────────┘
                                │
                                ▼
                     ┌────────────────────────────────┐
                     │      Monitoring Reports        │
                     │  /monitoring/report_*.html     │
                     └────────────────────────────────┘




---


```

mlops_salary_capstone/
│
├── data/
│   └── salary_data.csv
│
├── monitoring/
│   └── report_*.html
│
├── models/
│
├── logs/
│
├── train.py
├── app.py
├── requirements.txt
└── README.md

```

## ⚙️ Installation & Setup
1️⃣ Create Virtual Environment

python3 -m venv mlopct
source mlopct/bin/activate

2️⃣ Install Requirements
pip install -r requirements.txt


🧪 Training the Models
python train.py

This will:
Train 3 models
Log metrics & artifacts into MLflow
Register the best model as SalaryPredictionModel


#### You can view runs using:
mlflow ui

Open:

👉 http://127.0.0.1:5000

Promote the best model to: Production


## 🚀 Running the Streamlit App

Start the app:
streamlit run app.py


The app will:

Load the Production model from MLflow
Accept user input
Predict salary
Generate Evidently reports
Save them into /monitoring


#### 📊 Monitoring With Evidently

Each prediction triggers:
Data Drift Report
Data Quality Report

Stored in:
monitoring/report_YYYY-MM-DD_HH-MM-SS.html


## 📦 Requirements
See requirements.txt for full list:
numpy==1.26.4
pandas
scikit-learn
mlflow
streamlit
evidently==0.4.17
...
