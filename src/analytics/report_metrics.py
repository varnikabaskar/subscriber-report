"""Deterministic analytics used by the daily report."""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Sequence

from src.history import Observation


@dataclass(frozen=True)
class CalculatedMetrics:
    total_subscribers: int
    yesterday_subscribers: int | None
    daily_gain: int | None
    daily_growth_percentage: float | None
    weekly_growth: int | None
    weekly_growth_percentage: float | None
    monthly_growth: int | None
    monthly_growth_percentage: float | None
    seven_day_average_gain: float | None
    percent_difference_from_average: float | None
    trend_status: str
    variation_status: str
    next_milestone: int | None
    estimated_milestone_date: date | None
    summary: str
    last_seven_gains: list[int]
    weekly_totals: list[int]
    heatmap: list[list[int]]


def _percent(change: int | None, baseline: int | None) -> float | None:
    if change is None or not baseline:
        return None
    return change / baseline * 100


def calculate_metrics(history: Sequence[Observation], today: date) -> CalculatedMetrics:
    ordered = sorted(history, key=lambda item: item.observation_date)
    current = next(item for item in reversed(ordered) if item.observation_date == today)
    by_date = {item.observation_date: item for item in ordered}

    yesterday = by_date.get(today - timedelta(days=1))
    week_start = today - timedelta(days=7)
    month_start = today - timedelta(days=30)
    previous_week = by_date.get(week_start)
    previous_month = by_date.get(month_start)
    daily_gain = current.subscribers - yesterday.subscribers if yesterday else None
    weekly_growth = current.subscribers - previous_week.subscribers if previous_week else None
    monthly_growth = current.subscribers - previous_month.subscribers if previous_month else None

    daily_gains = []
    for offset in range(6, -1, -1):
        current_day = today - timedelta(days=offset)
        before = by_date.get(current_day - timedelta(days=1))
        after = by_date.get(current_day)
        daily_gains.append(after.subscribers - before.subscribers if after and before else 0)
    average = sum(daily_gains) / 7 if all(day in by_date for day in [today - timedelta(days=i) for i in range(7)]) else None

    previous_average = None
    if all(today - timedelta(days=i) in by_date for i in range(8, 15)):
        previous_average = sum(
            by_date[today - timedelta(days=i)].subscribers
            - by_date[today - timedelta(days=i + 1)].subscribers
            for i in range(8, 15)
        ) / 7
    if average is None or previous_average is None:
        trend = "stable"
    elif average > previous_average * 1.05:
        trend = "increasing"
    elif average < previous_average * 0.95:
        trend = "declining"
    else:
        trend = "stable"

    spread = max(daily_gains) - min(daily_gains) if daily_gains else 0
    variation = "no significant deviations" if spread <= 10 else "minor day-to-day fluctuations" if spread <= 30 else "higher-than-usual variability"
    milestone_step = 100_000
    milestone = math.ceil(current.subscribers / milestone_step) * milestone_step
    if milestone <= current.subscribers:
        milestone += milestone_step
    milestone_date = None
    if average and average > 0:
        milestone_date = today + timedelta(days=math.ceil((milestone - current.subscribers) / average))

    above_below = "equal to" if not average or daily_gain is None or daily_gain == average else "above" if daily_gain > average else "below"
    characteristic = "moderate audience growth" if average is None else "stronger-than-average audience growth" if above_below == "above" else "slower audience growth" if above_below == "below" else "sustained audience growth"
    difference = abs((daily_gain - average) / average * 100) if daily_gain is not None and average else None
    gain_text = str(daily_gain) if daily_gain is not None else "N/A"
    difference_text = f"{difference:.2f}" if difference is not None else "N/A"
    summary = (
        f"The channel recorded a net increase of {gain_text} subscribers today, "
        f"bringing the total subscriber count to {current.subscribers:,}. Today's growth is {above_below} "
        f"the 7-day average by {difference_text}%"
    )
    summary += (
        f", indicating {characteristic}. Overall subscriber growth remains {trend}, with {variation} observed over recent days. "
        f"Based on the current growth rate, the channel is projected to reach {milestone:,} by {milestone_date.strftime('%d %B %Y') if milestone_date else 'N/A'}."
    )

    weekly_totals = []
    for week in range(4, 0, -1):
        end = today - timedelta(days=(week - 1) * 7)
        start = end - timedelta(days=6)
        values = [by_date.get(start + timedelta(days=i)) for i in range(7)]
        weekly_totals.append(sum(values[i].subscribers - by_date.get(start + timedelta(days=i - 1)).subscribers for i in range(1, 7) if values[i] and by_date.get(start + timedelta(days=i - 1))))
    heatmap = []
    for week in range(3, -1, -1):
        end = today - timedelta(days=week * 7)
        row = []
        for weekday in range(7):
            target = end - timedelta(days=(end.weekday() - weekday) % 7)
            current_day = by_date.get(target)
            before = by_date.get(target - timedelta(days=1))
            row.append(current_day.subscribers - before.subscribers if current_day and before else 0)
        heatmap.append(row)

    return CalculatedMetrics(
        current.subscribers, yesterday.subscribers if yesterday else None, daily_gain,
        _percent(daily_gain, yesterday.subscribers if yesterday else None), weekly_growth,
        _percent(weekly_growth, previous_week.subscribers if previous_week else None), monthly_growth,
        _percent(monthly_growth, previous_month.subscribers if previous_month else None), average,
        difference, trend, variation, milestone, milestone_date, summary, daily_gains, weekly_totals, heatmap,
    )