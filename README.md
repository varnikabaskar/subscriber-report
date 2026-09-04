# Kauvery Hospital YouTube Subscriber Report

This project generates a daily three-page subscriber report for the Kauvery Hospital YouTube channel. It uses the approved PDF template as a fixed visual master, fetches data from the official YouTube Data API, stores history in CSV, and runs automatically in GitHub Actions at 8:00 AM IST.

## Project Structure

```
kauvery-youtube-report
├── src
│   ├── main.py                # Entry point for the application
│   ├── config.py              # Configuration settings and API keys
│   ├── fetcher
│   │   ├── __init__.py
│   │   └── youtube_client.py   # Handles YouTube Data API interactions
│   ├── analytics
│   │   ├── __init__.py
│   │   ├── metrics.py          # Calculates subscriber growth metrics
│   │   └── trends.py           # Analyzes trends in subscriber growth
│   ├── report
│   │   ├── __init__.py
│   │   ├── pdf_generator.py     # Generates the PDF report
│   │   └── templates
│   │       └── report_template.html # HTML template for the report
│   ├── integrations
│   │   ├── __init__.py
│   │   └── todoist.py          # Integrates with Todoist API
│   ├── scheduler
│   │   ├── __init__.py
│   │   └── scheduler.py        # Schedules report generation
│   └── utils
│       └── helpers.py          # Utility functions
├── tests
│   ├── test_fetcher.py         # Unit tests for data fetching
│   └── test_report.py          # Unit tests for report generation
├── .github
│   └── workflows
│       └── scheduled-report.yml # GitHub Actions workflow for scheduling
├── scripts
│   ├── run_report.sh           # Script to run report generation locally
│   └── crontab_example.sh      # Example cron job setup
├── Dockerfile                   # Docker image instructions
├── requirements.txt             # Python dependencies
├── .env.example                 # Example environment variables
├── pyproject.toml              # Project dependencies and configurations
└── README.md                   # Project documentation
```

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/kauvery-youtube-report.git
   cd kauvery-youtube-report
   ```

2. **Install Dependencies**
   Ensure that Python 3.12 or higher is installed. Then, install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**
   For local runs, set `YOUTUBE_API_KEY` and `YOUTUBE_CHANNEL_URL` as environment variables. Never put a real key in `.env.example` or source files.

4. **Run the Application**
   You can run the application manually using:
   ```bash
   python -m src.main
   ```

## Usage

For GitHub hosting, add these repository secrets under **Settings > Secrets and variables > Actions**:

- `YOUTUBE_API_KEY`
- `TODOIST_API_TOKEN`

The channel defaults to `https://www.youtube.com/@KauveryHospital`. The report artifact link requires users to have permission to access the repository's Actions artifacts.

## Troubleshooting

- Ensure that `YOUTUBE_API_KEY` and `TODOIST_API_TOKEN` are configured as GitHub Secrets.
- Confirm that YouTube Data API v3 is enabled in Google Cloud.
- Early runs may show `N/A` for weekly/monthly metrics until enough CSV history exists.
- Check the logs for any errors during data fetching or report generation.
- If you encounter issues with the Todoist integration, verify your Todoist API token.

## Contributing

Feel free to submit issues or pull requests if you would like to contribute to this project.