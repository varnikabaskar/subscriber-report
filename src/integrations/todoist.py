"""Todoist REST delivery for generated reports."""

from __future__ import annotations

import os
from datetime import date
from pathlib import Path

import requests


def create_report_task(report_path: str | Path, report_date: date, report_url: str | None = None) -> str:
    """Create a Todoist task with the generated report's artifact URL."""
    token = os.getenv("TODOIST_API_TOKEN")
    if not token:
        raise ValueError("TODOIST_API_TOKEN is not configured")
    description = (
        "Today's Subscribers\n\nDaily Growth\n\nWeekly Growth\n\n"
        "The detailed analytics report is attached."
    )
    if report_url:
        description += f"\n\nReport download: {report_url}"
    response = requests.post(
        "https://api.todoist.com/rest/v2/tasks",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={
            "content": f"YouTube Daily Subscriber Report - {report_date.strftime('%d %b %Y')}",
            "description": description,
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()["id"]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Create the daily report Todoist task")
    parser.add_argument("report_path")
    parser.add_argument("report_date", help="ISO date, YYYY-MM-DD")
    parser.add_argument("--report-url")
    arguments = parser.parse_args()
    print(create_report_task(arguments.report_path, date.fromisoformat(arguments.report_date), arguments.report_url))