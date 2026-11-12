# Stock Data Visualizer (Flask + Docker)

A web app that queries the [Alpha Vantage](https://www.alphavantage.co/) API and displays a bar or line chart of stock data for a chosen symbol, time series, and date range. Built with Python, Flask, Pygal, and Docker.

## Instructions for Graders

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed **and running** (the engine must show as running before step 4)
- A free Alpha Vantage API key: https://www.alphavantage.co/support/#api-key

### Run with Docker (recommended)

1. **Clone the repo**
   ```
   git clone https://github.com/AlexL0324/stock-data-app.git
   cd stock-data-app
   ```
2. **Create a `.env` file** in the project folder (copy `.env.example` and edit it):
   ```
   ALPHAVANTAGE_API_KEY=your_key_here
   ```
   Use no quotes and no spaces around the `=`.
3. **Make sure `stocks.csv` is in the project folder** (it supplies the stock symbols for the dropdown).
4. **Build and start the container**
   ```
   docker compose up --build
   ```
5. **Open the app** at http://localhost:5000
6. **Stop the app** with `Ctrl+C`, then optionally `docker compose down`.

### Run without Docker (alternative)

```
pip install -r requirements.txt
```
Set the key in the same terminal, then start the app:

- PowerShell: `$env:ALPHAVANTAGE_API_KEY="your_key_here"`
- Command Prompt: `set ALPHAVANTAGE_API_KEY=your_key_here`
- Mac/Linux: `export ALPHAVANTAGE_API_KEY=your_key_here`

```
python app.py
```
Then open http://localhost:5000.

## How to Use the App

1. Choose a **stock symbol** from the dropdown (populated from `stocks.csv`).
2. Choose a **chart type** (Bar or Line).
3. Choose a **time series** (Intraday, Daily, Weekly, or Monthly).
4. Choose a **begin date** and an **end date** (the end date cannot be before the begin date).
5. Click **Generate chart**. The chart appears below the form.

Invalid input or API problems show a message on the page instead of crashing the app.

## Suggested Test Cases

| Symbol | Chart | Time series | Begin | End | Expected |
|--------|-------|-------------|-------|-----|----------|
| IBM | Line | Monthly | 2015-01-01 | 2024-12-31 | Chart spanning ten years |
| AAPL | Bar | Weekly | 2022-01-01 | 2023-12-31 | Weekly bars across two years |
| MSFT | Line | Daily | (a range within the last ~100 trading days) | | Daily chart |
| Any | Any | Any | 2024-06-01 | 2024-01-01 | Error: end date cannot be before begin date |

## Known Limitations (Alpha Vantage Free Tier)

- **Daily and intraday data:** `outputsize=full` is a premium feature, so free keys only return roughly the most recent 100 data points. For older dates, use **Weekly** or **Monthly**, which return the full history.
- **Rate limits:** Free keys allow about 25 requests per day and 1 request per second. If you see a rate-limit message, wait and try again, or use a different key.
- If a date range has no data, the app reports the date range that is available.

## Project Structure

```
├── app.py                  # Flask routes, API calls, chart building
├── templates/index.html    # Web form and chart display
├── stocks.csv              # Stock symbols for the dropdown
├── requirements.txt        # Python dependencies
├── Dockerfile              # Container image definition
├── docker-compose.yml      # Launches the container
├── .env.example            # Template for the API key file
└── README.md
```

## Notes

- The API key is read from the `ALPHAVANTAGE_API_KEY` environment variable and is never stored in the repository (`.env` is gitignored).
