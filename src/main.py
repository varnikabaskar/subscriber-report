"""Single-run production entry point used by GitHub Actions."""

from __future__ import annotations

import logging
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from src.analytics.report_metrics import calculate_metrics
from src.fetcher.youtube_client import YouTubeClient
from src.history import Observation, load_history, upsert_observation
from src.report.template_renderer import ReportData, render_report


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
ROOT = Path(__file__).resolve().parents[1]

def main():
    now = datetime.now(ZoneInfo(os.getenv("TIMEZONE", "Asia/Kolkata")))
    report_date = now.date()
    history_path = ROOT / "data" / "subscriber_history.csv"
    report_path = ROOT / "reports" / f"Kauvery_YouTube_Subscriber_Report_{report_date.isoformat()}.pdf"
    subscriber_count = YouTubeClient().fetch_latest_subscriber_count()
    upsert_observation(history_path, Observation(report_date, subscriber_count))
    metrics = calculate_metrics(load_history(history_path), report_date)
    report_data = ReportData(
        report_date=report_date, generated_time=now.strftime("%I:%M %p"),
        total_subscribers=metrics.total_subscribers,
        yesterday_subscribers=metrics.yesterday_subscribers or 0,
        daily_gain=metrics.daily_gain or 0,
        daily_growth_percentage=metrics.daily_growth_percentage,
        weekly_growth_percentage=metrics.weekly_growth_percentage,
        monthly_growth_percentage=metrics.monthly_growth_percentage,
        summary=metrics.summary, last_seven_gains=metrics.last_seven_gains,
        weekly_totals=metrics.weekly_totals, heatmap=metrics.heatmap,
    )
    render_report(report_data, report_path)
    logging.info("Generated report: %s", report_path)
    return report_path

if __name__ == "__main__":
    main()