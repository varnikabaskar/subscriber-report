import os

YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
YOUTUBE_CHANNEL_URL = os.getenv(
	'YOUTUBE_CHANNEL_URL',
	'https://www.youtube.com/@KauveryHospital',
)
YOUTUBE_CHANNEL_ID = os.getenv('YOUTUBE_CHANNEL_ID')
TODOIST_API_TOKEN = os.getenv('TODOIST_API_TOKEN')
REPORT_OUTPUT_PATH = os.getenv('REPORT_OUTPUT_PATH', 'reports/daily_report.pdf')
SCHEDULE_TIME = os.getenv('SCHEDULE_TIME', '08:00')  # Default to 8:00 AM IST