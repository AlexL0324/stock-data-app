"""Stock Data Visualizer - queries Alpha Vantage and charts a date range in the browser.
"""
import os
import sys
from datetime import datetime
import time
import pygal
import requests

API_URL = "https://www.alphavantage.co/query"
API_KEY = os.environ.get("ALPHAVANTAGE_API_KEY", "YOUR_API_KEY_HERE")

CHART_TYPES = {"1": ("Bar", pygal.Bar), "2": ("Line", pygal.Line)}

# menu choice -> (API function, JSON key holding the series, extra params)
TIME_SERIES = {
    "1": ("Intraday (60 min)", "TIME_SERIES_INTRADAY", "Time Series (60min)", {"interval": "60min"}),
    "2": ("Daily", "TIME_SERIES_DAILY", "Time Series (Daily)", {}),
    "3": ("Weekly", "TIME_SERIES_WEEKLY", "Weekly Time Series", {}),
    "4": ("Monthly", "TIME_SERIES_MONTHLY", "Monthly Time Series", {}),
}


def prompt_choice(title, options):
    """Show a numbered menu and return the chosen entry."""
    print(f"\n{title}")
    print("-" * len(title))
    for key, value in options.items():
        print(f"{key}. {value[0]}")
    while True:
        choice = input("Enter your choice: ").strip()
        if choice in options:
            return options[choice]
        print("Invalid choice, try again.")


def prompt_symbol():
    while True:
        symbol = input("Enter the stock symbol you are looking for (e.g. IBM): ").strip().upper()
        if symbol.isalpha() and 1 <= len(symbol) <= 10:
            return symbol
        print("Please enter a valid stock symbol (letters only).")


def prompt_date(message, minimum=None):
    """Ask for a YYYY-MM-DD date; reject bad formats and dates before `minimum`."""
    while True:
        text = input(message).strip()
        try:
            date = datetime.strptime(text, "%Y-%m-%d").date()
        except ValueError:
            print("Invalid format. Use YYYY-MM-DD.")
            continue
        if minimum and date < minimum:
            print("The end date cannot be before the begin date.")
            continue
        return date


def fetch_data(symbol, function, params):
    """Try full history first; fall back to compact (last ~100 points) on free keys."""
    for size in ("full", "compact"):
        query = {"function": function, "symbol": symbol, "apikey": API_KEY, "outputsize": size, **params}
        try:
            response = requests.get(API_URL, params=query, timeout=30)
            response.raise_for_status()
        except requests.RequestException as err:
            sys.exit(f"Network error: {err}")
        raw = response.json()
        message = str(raw.get("Information", "")) + str(raw.get("Note", ""))
        if size == "full" and "premium" in message.lower() and "outputsize" in message.lower():
            print("Full history is a premium feature; using the most recent ~100 data points instead.")
            time.sleep(1.5)  # stay under the free tier's 1 request/second limit
            continue
        return raw
    return raw


def filter_series(raw, series_key, start, end):
    """Return (labels, opens, highs, lows, closes) sorted oldest -> newest within the range."""
    if series_key not in raw:
        message = raw.get("Error Message") or raw.get("Note") or raw.get("Information") or "Unexpected response."
        sys.exit(f"Alpha Vantage error: {message}")

    rows = []
    for stamp, values in raw[series_key].items():
        day = datetime.strptime(stamp[:10], "%Y-%m-%d").date()  # works for intraday timestamps too
        if start <= day <= end:
            rows.append((stamp, values))
    rows.sort(key=lambda r: r[0])

    labels = [r[0] for r in rows]
    cols = [[float(r[1][f"{i}. {name}"]) for r in rows] for i, name in enumerate(["open", "high", "low", "close"], 1)]
    return (labels, *cols)


def build_chart(chart_cls, symbol, series_name, start, end, data):
    labels, opens, highs, lows, closes = data
    chart = chart_cls(x_label_rotation=45, show_minor_x_labels=False, width=1100, height=600)
    chart.title = f"Stock Data for {symbol}: {start} to {end} ({series_name})"
    chart.x_labels = labels
    chart.x_labels_major = labels[:: max(1, len(labels) // 12)]
    chart.add("Open", opens)
    chart.add("High", highs)
    chart.add("Low", lows)
    chart.add("Close", closes)
    return chart


def main():
    symbol = prompt_symbol()
    chart_name, chart_cls = prompt_choice("Chart Types", CHART_TYPES)
    series_name, function, series_key, extra = prompt_choice("Select the Time Series of the chart you want to generate", TIME_SERIES)
    start = prompt_date("Enter the begin date (YYYY-MM-DD): ")
    end = prompt_date("Enter the end date (YYYY-MM-DD): ", minimum=start)

    raw = fetch_data(symbol, function, extra)
    data = filter_series(raw, series_key, start, end)
    if not data[0]:
        sys.exit("No data found for that date range.")

    chart = build_chart(chart_cls, symbol, series_name, start, end, data)
    print(f"\nGenerating {chart_name.lower()} chart with {len(data[0])} points and opening your browser...")
    chart.render_in_browser()


if __name__ == "__main__":
    main()