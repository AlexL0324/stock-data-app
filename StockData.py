"""Stock Data Visualizer - Flask web app (Project 3a)."""
"""LQJW0U7AXY205L0K"""
import csv
import os
import time
from datetime import datetime

import pygal
import requests
from flask import Flask, render_template, request

app = Flask(__name__)

API_URL = "https://www.alphavantage.co/query"
API_KEY = os.environ.get("ALPHAVANTAGE_API_KEY", "")
STOCKS_CSV = os.path.join(os.path.dirname(__file__), "stocks.csv")
FALLBACK_SYMBOLS = ["AAPL", "AMZN", "GOOGL", "IBM", "MSFT", "NVDA", "TSLA"]

CHART_TYPES = {"bar": ("Bar", pygal.Bar), "line": ("Line", pygal.Line)}

# form value -> (label, API function, JSON key, extra params)
TIME_SERIES = {
    "intraday": ("Intraday (60 min)", "TIME_SERIES_INTRADAY", "Time Series (60min)", {"interval": "60min"}),
    "daily": ("Daily", "TIME_SERIES_DAILY", "Time Series (Daily)", {}),
    "weekly": ("Weekly", "TIME_SERIES_WEEKLY", "Weekly Time Series", {}),
    "monthly": ("Monthly", "TIME_SERIES_MONTHLY", "Monthly Time Series", {}),
}


class AppError(Exception):
    """A user-facing error message (never crashes the page)."""


def load_symbols():
    """Read stock symbols from stocks.csv so nothing is hard-coded in the form."""
    try:
        with open(STOCKS_CSV, newline="", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            header = next(reader)
            col = next((i for i, h in enumerate(header) if h.strip().lower() in ("symbol", "ticker")), 0)
            symbols = sorted({row[col].strip().upper() for row in reader if len(row) > col and row[col].strip()})
            return symbols or FALLBACK_SYMBOLS
    except (OSError, StopIteration):
        return FALLBACK_SYMBOLS


def fetch_data(symbol, function, params):
    """Try full history first; fall back to compact on free keys."""
    if not API_KEY:
        raise AppError("Server has no API key. Set ALPHAVANTAGE_API_KEY.")
    raw = {}
    for size in ("full", "compact"):
        query = {"function": function, "symbol": symbol, "apikey": API_KEY, "outputsize": size, **params}
        try:
            resp = requests.get(API_URL, params=query, timeout=30)
            resp.raise_for_status()
            raw = resp.json()
        except (requests.RequestException, ValueError):
            raise AppError("Could not reach Alpha Vantage. Please try again.")
        msg = (str(raw.get("Information", "")) + str(raw.get("Note", ""))).lower()
        if size == "full" and "premium" in msg and "outputsize" in msg:
            time.sleep(1.5)  # free tier: 1 request/second
            continue
        break
    return raw


def filter_series(raw, series_key, start, end):
    if series_key not in raw:
        msg = raw.get("Error Message") or raw.get("Note") or raw.get("Information") or "Unexpected API response."
        raise AppError(f"Alpha Vantage: {msg}")
    rows = []
    for stamp, vals in raw[series_key].items():
        day = datetime.strptime(stamp[:10], "%Y-%m-%d").date()
        if start <= day <= end:
            rows.append((stamp, vals))
    rows.sort(key=lambda r: r[0])
    if not rows:
        all_days = sorted(k[:10] for k in raw[series_key])
        raise AppError(f"No data in that range. Available data: {all_days[0]} to {all_days[-1]}. "
                       "(Free keys only return ~100 daily points; use Weekly/Monthly for older dates.)")
    labels = [r[0] for r in rows]
    cols = [[float(r[1][f"{i}. {n}"]) for r in rows] for i, n in enumerate(["open", "high", "low", "close"], 1)]
    return labels, cols


def build_chart(chart_key, symbol, series_label, start, end, labels, cols):
    chart = CHART_TYPES[chart_key][1](x_label_rotation=45, show_minor_x_labels=False, width=1100, height=600)
    chart.title = f"Stock Data for {symbol}: {start} to {end} ({series_label})"
    chart.x_labels = labels
    chart.x_labels_major = labels[:: max(1, len(labels) // 12)]
    for name, values in zip(["Open", "High", "Low", "Close"], cols):
        chart.add(name, values)
    return chart.render_data_uri()


@app.route("/", methods=["GET", "POST"])
def index():
    symbols = load_symbols()
    form = request.form if request.method == "POST" else {}
    chart_uri, error = None, None

    if request.method == "POST":
        try:
            symbol = form.get("symbol", "")
            chart_key = form.get("chart_type", "")
            series_key = form.get("time_series", "")
            if symbol not in symbols:
                raise AppError("Please choose a valid stock symbol.")
            if chart_key not in CHART_TYPES or series_key not in TIME_SERIES:
                raise AppError("Please choose a valid chart type and time series.")
            try:
                start = datetime.strptime(form.get("start_date", ""), "%Y-%m-%d").date()
                end = datetime.strptime(form.get("end_date", ""), "%Y-%m-%d").date()
            except ValueError:
                raise AppError("Dates must be in YYYY-MM-DD format.")
            if end < start:
                raise AppError("The end date cannot be before the begin date.")

            label, function, json_key, extra = TIME_SERIES[series_key]
            raw = fetch_data(symbol, function, extra)
            labels, cols = filter_series(raw, json_key, start, end)
            chart_uri = build_chart(chart_key, symbol, label, start, end, labels, cols)
        except AppError as err:
            error = str(err)
        except Exception:
            app.logger.exception("Unexpected error")
            error = "Something went wrong. Please try again."

    return render_template("index.html", symbols=symbols, chart_types=CHART_TYPES,
                           time_series=TIME_SERIES, form=form, chart_uri=chart_uri, error=error)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)