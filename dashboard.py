import os
from evidently.dashboard import Dashboard
from evidently.tabs import DataDriftTab, DataQualityTab
from evidently.pipeline.column_mapping import ColumnMapping
from fastapi import FastAPI
from evidently.ui.dashboards import DashboardConfig
from evidently.ui.workspaces import Workspace, FileStorage
import uvicorn


WORKSPACE_PATH = "monitoring/dashboards"
REPORTS_PATH = "monitoring/batch_reports"


def create_workspace():
    os.makedirs(WORKSPACE_PATH, exist_ok=True)
    storage = FileStorage(path=WORKSPACE_PATH)
    ws = Workspace(storage=storage)
    return ws


def create_dashboard(ws):
    # Dashboard config
    config = DashboardConfig(
        name="Salary Prediction Monitoring Dashboard",
        description="Drift & Data Quality Monitoring for Salary Prediction Model",
    )

    dashboard = ws.create_dashboard(config)
    return dashboard


def add_reports_to_dashboard(dashboard):
    if not os.path.exists(REPORTS_PATH):
        print("No batch reports found yet.")
        return

    for file in sorted(os.listdir(REPORTS_PATH)):
        if file.endswith(".html"):
            report_path = os.path.join(REPORTS_PATH, file)
            dashboard.add_report(report_path)


def run_server():
    ws = create_workspace()
    dashboard = create_dashboard(ws)
    add_reports_to_dashboard(dashboard)

    # FastAPI application
    app = FastAPI()
    ws.register(app)

    print("🚀 Evidently Dashboard running at: http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    run_server()

