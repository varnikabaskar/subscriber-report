"""Populate the approved three-page PDF template with report data."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Sequence

import fitz
import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt


PAGE_WIDTH = 595.5
PAGE_HEIGHT = 842.25
BRAND = "#A21F91"
TEMPLATE_PATH = Path(__file__).parent / "template" / "template.pdf"


@dataclass(frozen=True)
class ReportData:
    report_date: date
    generated_time: str
    total_subscribers: int
    yesterday_subscribers: int
    daily_gain: int
    daily_growth_percentage: float | None
    weekly_growth_percentage: float | None
    monthly_growth_percentage: float | None
    summary: str
    last_seven_gains: Sequence[int]
    weekly_totals: Sequence[int]
    heatmap: Sequence[Sequence[int]]


def _chart_bytes(plotter) -> bytes:
    figure, axis = plt.subplots(figsize=(6.1, 2.65), dpi=220)
    figure.patch.set_alpha(0)
    axis.set_facecolor("white")
    plotter(axis)
    figure.tight_layout(pad=0.3)
    output = __import__("io").BytesIO()
    figure.savefig(output, format="png", dpi=220, transparent=False)
    plt.close(figure)
    return output.getvalue()


def _trend_chart(gains: Sequence[int], report_date: date) -> bytes:
    def plot(axis):
        labels = [(report_date - timedelta(days=6 - i)).strftime("%d %b") for i in range(7)]
        axis.plot(labels, gains, color="#D23873", linewidth=2.2, marker="o", markersize=4.5)
        axis.set_ylim(0, max(40, max(gains) + 10))
        axis.grid(axis="y", color="#D9D9D9", linewidth=0.6)
        axis.spines[["top", "right", "left"]].set_visible(False)
        axis.spines["bottom"].set_color("#A0A0A0")
        axis.tick_params(axis="both", labelsize=7, colors="#333333", length=0)
        axis.set_ylabel("")

    return _chart_bytes(plot)


def _weekly_chart(weekly_totals: Sequence[int]) -> bytes:
    def plot(axis):
        bars = axis.bar(["week 1", "week 2", "week 3", "week 4"], weekly_totals,
                        color="#F6C957", width=0.82)
        for bar in bars:
            bar.set_clip_on(False)
        axis.set_ylim(0, max(80, max(weekly_totals) + 10))
        axis.grid(axis="y", color="#D9D9D9", linewidth=0.6)
        axis.set_axisbelow(True)
        axis.spines[["top", "right", "left"]].set_visible(False)
        axis.spines["bottom"].set_color("#A0A0A0")
        axis.tick_params(axis="both", labelsize=7, colors="#333333", length=0)

    return _chart_bytes(plot)


def _heatmap_chart(values: Sequence[Sequence[int]]) -> bytes:
    def plot(axis):
        matrix = np.asarray(values, dtype=float)
        image = axis.imshow(matrix, cmap="YlOrRd", aspect="auto")
        axis.set_xticks(range(7), ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], fontsize=6)
        axis.set_yticks([])
        axis.tick_params(length=0)
        axis.set_xticks(np.arange(-.5, 7, 1), minor=True)
        axis.set_yticks(np.arange(-.5, matrix.shape[0], 1), minor=True)
        axis.grid(which="minor", color="#F6E6A4", linewidth=0.8)
        axis.tick_params(which="minor", bottom=False, left=False)
        figure = axis.figure
        figure.colorbar(image, ax=axis, fraction=0.046, pad=0.04)

    return _chart_bytes(plot)


def _mask(page: fitz.Page, rect: tuple[float, float, float, float]) -> None:
    page.draw_rect(fitz.Rect(*rect), color=None, fill=(1, 1, 1), overlay=True)


def _text(page: fitz.Page, rect: tuple[float, float, float, float], value: str,
          size: float, font: str = "helv", color: tuple[float, float, float] = (0, 0, 0),
          align: int = 0) -> None:
    page.insert_textbox(fitz.Rect(*rect), value, fontsize=size, fontname=font,
                        color=color, align=align, overlay=True)


def _point_text(page: fitz.Page, point: tuple[float, float], value: str,
                size: float, font: str = "helv",
                color: tuple[float, float, float] = (0, 0, 0)) -> None:
    page.insert_text(point, value, fontsize=size, fontname=font, color=color, overlay=True)


def render_report(data: ReportData, output_path: str | Path,
                  template_path: str | Path = TEMPLATE_PATH) -> Path:
    """Copy the master PDF and replace only approved dynamic regions."""
    source = fitz.open(str(template_path))
    page1, page2, page3 = source[0], source[1], source[2]

    _mask(page1, (55, 525, 260, 570))
    _point_text(page1, (61, 558), data.report_date.strftime("%d %B %Y"), 21, "hebo")

    _mask(page2, (55, 130, 540, 252))
    _text(page2, (59, 134, 536, 247), data.summary, 12, "helv")
    metric_values = [
        f"{data.total_subscribers:,}",
        f"{data.yesterday_subscribers:,}",
        f"{data.daily_gain:+,}",
        f"{data.daily_growth_percentage:+.2f}%" if data.daily_growth_percentage is not None else "N/A",
        f"{data.weekly_growth_percentage:+.2f}%" if data.weekly_growth_percentage is not None else "N/A",
        f"{data.monthly_growth_percentage:+.2f}%" if data.monthly_growth_percentage is not None else "N/A",
    ]
    for index, value in enumerate(metric_values):
        y = 293 + index * 33
        _mask(page2, (300, y, 535, y + 22))
        _text(page2, (300, y, 535, y + 22), value, 13, "hebo", align=2)

    _mask(page2, (55, 565, 540, 805))
    page2.insert_image(fitz.Rect(59.5, 565, 536, 805), stream=_trend_chart(data.last_seven_gains, data.report_date), overlay=True)

    _mask(page3, (55, 135, 500, 330))
    page3.insert_image(fitz.Rect(59.5, 135, 500, 330), stream=_weekly_chart(data.weekly_totals), overlay=True)
    _mask(page3, (55, 375, 505, 680))
    page3.insert_image(fitz.Rect(59.5, 375, 500, 680), stream=_heatmap_chart(data.heatmap), overlay=True)
    _mask(page3, (60, 800, 540, 825))
    timestamp = f"Report Generated: {data.report_date.strftime('%d %B %Y')} • {data.generated_time} IST"
    _point_text(page3, (67, 815), timestamp, 9.3, "helv")

    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    source.save(str(destination), garbage=4, deflate=True)
    source.close()
    return destination


def mock_report_data() -> ReportData:
    """Return the approved sample values requested for visual inspection."""
    gains = [32, 41, 28, 52, 45, 20, 48]
    return ReportData(
        report_date=date(2026, 9, 2),
        generated_time="08:00 AM",
        total_subscribers=125_432,
        yesterday_subscribers=125_384,
        daily_gain=48,
        daily_growth_percentage=0.04,
        weekly_growth_percentage=0.31,
        monthly_growth_percentage=1.22,
        summary=(
            "The channel recorded a net increase of 48 subscribers today, bringing the total "
            "subscriber count to 125,432. Today's growth is above the 7-day average by 18.52%, "
            "indicating stronger-than-average audience growth. Overall subscriber growth remains "
            "increasing, with minor day-to-day fluctuations observed over recent days. Based on "
            "the current growth rate, the channel is projected to reach 125,500 by 04 September 2026."
        ),
        last_seven_gains=gains,
        weekly_totals=[76, 60, 45, 30],
        heatmap=[
            [18, 21, 25, 17, 29, 35, 31],
            [24, 32, 28, 40, 44, 38, 36],
            [14, 19, 22, 27, 31, 26, 24],
            [32, 41, 28, 52, 45, 20, 48],
        ],
    )


if __name__ == "__main__":
    render_report(mock_report_data(), "reports/sample_report.pdf")