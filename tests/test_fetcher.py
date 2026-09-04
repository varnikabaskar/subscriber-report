import unittest
from unittest.mock import MagicMock, patch

from src.fetcher.youtube_client import YouTubeClient

class TestYouTubeClient(unittest.TestCase):

    def setUp(self):
        self.client = YouTubeClient(api_key="test-key", channel_id="UC-test")

    def test_fetch_latest_subscriber_count(self):
        request = MagicMock()
        request.execute.return_value = {
            "items": [{"statistics": {"subscriberCount": "125432"}}]
        }
        channels = MagicMock()
        channels.list.return_value = request
        with patch.object(self.client.youtube, "channels", return_value=channels):
            subscriber_count = self.client.fetch_latest_subscriber_count()
        self.assertIsInstance(subscriber_count, int)
        self.assertEqual(subscriber_count, 125432)

    def test_fetch_historical_data(self):
        historical_data = self.client.fetch_historical_data()
        self.assertIsInstance(historical_data, list)
        self.assertEqual(historical_data, [])

if __name__ == '__main__':
    unittest.main()