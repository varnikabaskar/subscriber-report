import os
import math
import logging
import sys
from datetime import datetime, timedelta
from io import BytesIO
from pathlib import Path
from typing import Optional, Dict

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.fetcher.youtube_client import YouTubeClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def make_sample_history(days: int = 30, start_subs: int = 1_020_000) -> pd.DataFrame:
    """Create deterministic sample subscriber history for `days` days ending today."""
    rng = np.random.default_rng(42)
    gains = rng.integers(low=5, high=120, size=days)  # deterministic
    dates = [datetime.utcnow().date() - timedelta(days=(days - 1 - i)) for i in range(days)]
    subs = [start_subs]
    for g in gains[1:]:
        subs.append(subs[-1] + int(g))
    df = pd.DataFrame({"date": dates, "subscribers": subs})
    df["daily_gain"] = df["subscribers"].diff().fillna(0).astype(int)
    return df


def fetch_live_subscriber_count() -> Optional[int]:
    """Fetch the live count when an API key is configured; otherwise return None."""
    if not os.getenv("YOUTUBE_API_KEY"):
        return None
    return YouTubeClient().fetch_latest_subscriber_count()


def compute_analytics(df: pd.DataFrame) -> Dict[str, Optional[object]]:
    today = df.iloc[-1]
    yesterday = df.iloc[-2] if len(df) >= 2 else None
    last7 = df.tail(7)
    prev7 = df.tail(14).head(7) if len(df) >= 14 else None

    current = int(today["subscribers"])
    prev = int(yesterday["subscribers"]) if yesterday is not None else None
    daily_gain = int(today["daily_gain"]) if yesterday is not None else None
    daily_pct = (daily_gain / prev * 100) if (prev and prev > 0) else None

    weekly_total = int(last7["daily_gain"].sum())
    weekly_pct = (weekly_total / (prev7["subscribers"].iloc[0]) * 100) if (prev7 is not None and prev7["subscribers"].iloc[0] > 0) else None
    avg_daily_7 = float(last7["daily_gain"].mean())

    highest_day = last7.loc[last7["daily_gain"].idxmax()]
    lowest_day = last7.loc[last7["daily_gain"].idxmin()]

    moving_avg_7 = float(df["daily_gain"].rolling(window=7, min_periods=1).mean().iloc[-1])

    # Trend: compare last 7 average vs previous 7 average
    if prev7 is not None:
        prev7_avg = float(prev7["daily_gain"].mean())
        if prev7_avg == 0:
            trend = "Stable"
        else:
            change_pct = (avg_daily_7 - prev7_avg) / prev7_avg * 100
            if change_pct > 5:
                trend = "Increasing"
            elif change_pct < -5:
                trend = "Declining"
            else:
                trend = "Stable"
    else:
        trend = "Stable"

    # Next milestone: next 0.1M (100k) above current, formatted
    milestone_step = 100_000
    next_milestone = math.ceil(current / milestone_step) * milestone_step
    if next_milestone <= current:
        next_milestone += milestone_step
    days_to_milestone = math.ceil((next_milestone - current) / avg_daily_7) if avg_daily_7 > 0 else None
    milestone_date = (datetime.utcnow().date() + timedelta(days=days_to_milestone)) if days_to_milestone is not None else None

    return {
        "current_subscribers": current,
        "yesterday_subscribers": prev,
        "daily_gain": daily_gain,
        "daily_pct": round(daily_pct, 2) if daily_pct is not None else None,
        "weekly_total_gain": weekly_total,
        "weekly_pct": round(weekly_pct, 2) if weekly_pct is not None else None,
        "avg_daily_7": round(avg_daily_7, 2),
        "highest_gain_day": {"date": str(highest_day["date"]), "gain": int(highest_day["daily_gain"])},
        "lowest_gain_day": {"date": str(lowest_day["date"]), "gain": int(lowest_day["daily_gain"])},
        "moving_avg_7": round(moving_avg_7, 2),
        "trend": trend,
        "next_milestone": f"{next_milestone:,}",
        "estimated_milestone_date": str(milestone_date) if milestone_date else None,
    }


def plot_charts(df: pd.DataFrame, out_dir: str) -> Dict[str, str]:
    os.makedirs(out_dir, exist_ok=True)
    charts = {}

    # Chart 1: Last 30 days subscriber trend
    fig, ax = plt.subplots(figsize=(8, 3.5), dpi=200)
    last30 = df.tail(30)
    ax.plot(last30["date"], last30["subscribers"], marker="o", linewidth=1.5)
    ax.set_title("Subscriber Trend — Last 30 Days")
    ax.set_xlabel("Date")
    ax.set_ylabel("Subscribers")
    ax.grid(True, linestyle="--", alpha=0.5)
    fig.autofmt_xdate(rotation=45)
    path1 = os.path.join(out_dir, "subscriber_trend_30d.png")
    fig.tight_layout()
    fig.savefig(path1, dpi=200, facecolor="white")
    plt.close(fig)
    charts["trend_30d"] = path1

    # Chart 2: Daily gain last 7 days
    fig, ax = plt.subplots(figsize=(6.5, 3.5), dpi=200)
    last7 = df.tail(7)
    ax.bar(last7["date"].astype(str), last7["daily_gain"], color="#2a9d8f")
    ax.set_title("Daily Subscriber Gain — Last 7 Days")
    ax.set_xlabel("Date")
    ax.set_ylabel("Daily Gain")
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    fig.autofmt_xdate(rotation=45)
    path2 = os.path.join(out_dir, "daily_gain_7d.png")
    fig.tight_layout()
    fig.savefig(path2, dpi=200, facecolor="white")
    plt.close(fig)
    charts["gain_7d"] = path2

    return charts


def generate_pdf(report_path: str, channel_name: str, date_str: str, analytics: Dict, charts: Dict[str, str], executive_summary: str) -> None:
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    c = canvas.Canvas(report_path, pagesize=A4)
    w, h = A4
    margin = 50
    y = h - margin

    c.setFont("Helvetica-Bold", 18)
    c.drawString(margin, y, "YouTube Daily Subscriber Report")
    c.setFont("Helvetica", 10)
    c.drawRightString(w - margin, y, date_str)
    y -= 30

    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, f"Channel: {channel_name}")
    y -= 18

    # Executive Summary
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin, y, "Executive Summary")
    y -= 14
    c.setFont("Helvetica", 10)
    text = c.beginText(margin, y)
    text.textLines(executive_summary)
    c.drawText(text)
    y = text.getY() - 10

    # Key metrics (two-column)
    metrics = [
        ("Subscribers Today", f"{analytics['current_subscribers']:,}"),
        ("Subscribers Yesterday", f"{analytics['yesterday_subscribers']:,}" if analytics["yesterday_subscribers"] else "N/A"),
        ("Daily Gain/Loss", f"{analytics['daily_gain']:+,}"),
        ("Daily Growth %", f"{analytics['daily_pct']}%"),
        ("Weekly Gain (7d)", f"{analytics['weekly_total_gain']:,}"),
        ("Weekly Growth %", f"{analytics['weekly_pct']}%"),
        ("Avg Daily (7d)", f"{analytics['avg_daily_7']:,}"),
        ("Highest Gain Day (7d)", f"{analytics['highest_gain_day']['date']} (+{analytics['highest_gain_day']['gain']:,})"),
        ("Lowest Gain Day (7d)", f"{analytics['lowest_gain_day']['date']} ({analytics['lowest_gain_day']['gain']:,})"),
        ("7-day Moving Avg", f"{analytics['moving_avg_7']:,}"),
        ("Growth Trend", analytics["trend"]),
        ("Next Milestone", analytics["next_milestone"]),
        ("Est. Milestone Date", analytics["estimated_milestone_date"] or "N/A"),
    ]
    col1_x = margin
    col2_x = w / 2 + 10
    y0 = y
    c.setFont("Helvetica", 10)
    for i, (k, v) in enumerate(metrics):
        x = col1_x if i % 2 == 0 else col2_x
        if i % 2 == 0 and i != 0:
            y -= 16
        c.drawString(x, y, f"{k}: {v}")
    y = y - 36

    # Charts
    try:
        img1 = ImageReader(charts["trend_30d"])
        img2 = ImageReader(charts["gain_7d"])
        img_w = (w - 2 * margin - 20) / 2
        img_h = 130
        c.drawImage(img1, margin, y - img_h, width=img_w, height=img_h, preserveAspectRatio=True, mask="auto")
        c.drawImage(img2, margin + img_w + 20, y - img_h, width=img_w, height=img_h, preserveAspectRatio=True, mask="auto")
    except Exception as e:
        logging.error("Failed to embed charts: %s", e)

    # Footer
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(margin, 30, "Automatically generated by the YouTube Analytics Automation System.")
    c.save()


def main() -> None:
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    out_reports = os.path.join(base_dir, "reports")
    out_charts = os.path.join(base_dir, "charts")
    os.makedirs(out_reports, exist_ok=True)
    os.makedirs(out_charts, exist_ok=True)

    live_count = fetch_live_subscriber_count()
    df = make_sample_history(days=30, start_subs=1_020_000)
    if live_count is not None:
        df["subscribers"] += live_count - int(df.iloc[-1]["subscribers"])
        df["daily_gain"] = df["subscribers"].diff().fillna(0).astype(int)
    analytics = compute_analytics(df)
    charts = plot_charts(df, out_charts)

    data_source = "live YouTube Data API data" if live_count is not None else "deterministic sample data"
    exec_summary = (
        f"The channel gained {analytics['daily_gain']} subscribers since yesterday, "
        f"with a weekly gain of {analytics['weekly_total_gain']} and a 7-day average of {analytics['avg_daily_7']:.1f} subscribers/day. "
        f"Growth trend is {analytics['trend'].lower()}. "
        f"Next milestone {analytics['next_milestone']} is estimated around {analytics['estimated_milestone_date']}. "
        f"Data source: {data_source}."
    )

    date_str = datetime.utcnow().strftime("%d %b %Y")
    report_path = os.path.join(out_reports, f"sample_report_{datetime.utcnow().strftime('%Y%m%d')}.pdf")
    generate_pdf(report_path, "Kauvery Hospital", date_str, analytics, charts, exec_summary)
    logging.info("Sample report generated: %s", report_path)


if __name__ == "__main__":
    main()
