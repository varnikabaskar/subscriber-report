from datetime import date, timedelta

from src.analytics.report_metrics import calculate_metrics
from src.history import Observation, load_history, upsert_observation


def test_history_upsert_replaces_duplicate_date(tmp_path):
    path = tmp_path / "subscriber_history.csv"
    upsert_observation(path, Observation(date(2026, 9, 1), 100))
    upsert_observation(path, Observation(date(2026, 9, 1), 125))
    assert load_history(path) == [Observation(date(2026, 9, 1), 125)]


def test_metrics_calculate_daily_and_weekly_growth():
    start = date(2026, 8, 25)
    history = [Observation(start + timedelta(days=i), 1000 + i * 10) for i in range(9)]
    metrics = calculate_metrics(history, start + timedelta(days=8))
    assert metrics.total_subscribers == 1080
    assert metrics.daily_gain == 10
    assert metrics.weekly_growth == 70
    assert metrics.seven_day_average_gain == 10