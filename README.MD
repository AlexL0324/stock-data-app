# Stock Data Visualizer
Queries Alpha Vantage and charts stock data for a chosen date range.

## Setup
1. pip install -r requirements.txt
2. Get a free key at https://www.alphavantage.co/support/#api-key
3. Set it in your terminal:
   - Windows (PowerShell): $env:ALPHAVANTAGE_API_KEY="your_key"
   - Windows (cmd): set ALPHAVANTAGE_API_KEY=your_key
   - Mac/Linux: export ALPHAVANTAGE_API_KEY=your_key
4. python StockData.py

Note: free keys limit daily data to the last ~100 trading days
and 25 requests per day. Use Weekly/Monthly for long date ranges.

Testing it, we only manage to get data for 2026 only
