"""Official YouTube Data API client for channel subscriber statistics."""

import os
import re
from typing import Any, Dict, List, Optional

from googleapiclient.discovery import build


class YouTubeClient:
    """Fetch subscriber data without scraping YouTube pages."""

    def __init__(self, api_key: Optional[str] = None,
                 channel_id: Optional[str] = None,
                 channel_url: Optional[str] = None) -> None:
        self.api_key = api_key or os.getenv("YOUTUBE_API_KEY")
        self.channel_id = channel_id or os.getenv("YOUTUBE_CHANNEL_ID")
        self.channel_url = channel_url or os.getenv(
            "YOUTUBE_CHANNEL_URL",
            "https://www.youtube.com/@KauveryHospital",
        )
        if not self.api_key:
            raise ValueError("YOUTUBE_API_KEY is not configured")
        self.youtube = build("youtube", "v3", developerKey=self.api_key)

    def resolve_channel_id(self) -> str:
        """Resolve the configured channel URL handle using the official API."""
        if self.channel_id:
            return self.channel_id
        match = re.search(r"youtube\.com/@([^/?#]+)", self.channel_url)
        if not match:
            raise ValueError("YOUTUBE_CHANNEL_URL must contain a YouTube handle")
        response = self.youtube.channels().list(
            part="id", forHandle=match.group(1)
        ).execute(num_retries=3)
        items = response.get("items", [])
        if not items or not items[0].get("id"):
            raise LookupError(f"No YouTube channel found for {self.channel_url}")
        self.channel_id = items[0]["id"]
        return self.channel_id

    def fetch_latest_subscriber_count(self) -> int:
        """Return the latest public subscriber count for the configured channel."""
        response = self.youtube.channels().list(
            part="statistics", id=self.resolve_channel_id()
        ).execute(num_retries=3)
        items = response.get("items", [])
        if not items:
            raise LookupError("YouTube API returned no channel statistics")
        subscriber_count = items[0].get("statistics", {}).get("subscriberCount")
        if subscriber_count is None or not str(subscriber_count).isdigit():
            raise ValueError("YouTube API returned an invalid subscriber count")
        return int(subscriber_count)

    def get_subscriber_count(self) -> int:
        """Backward-compatible alias for the latest subscriber count."""
        return self.fetch_latest_subscriber_count()

    def fetch_historical_data(self) -> List[Dict[str, Any]]:
        """Return an empty history placeholder until CSV persistence is connected."""
        return []

    def get_historical_data(self) -> List[Dict[str, Any]]:
        """Backward-compatible alias for historical data."""
        return self.fetch_historical_data()

    def fetch_channel_data(self) -> Dict[str, Any]:
        """Return the current count and historical records."""
        return {
            "subscriber_count": self.fetch_latest_subscriber_count(),
            "historical_data": self.fetch_historical_data(),
        }