#!/usr/bin/env python3
"""Fetch and analyze stock market data using Alpha Vantage API.

Uses https://www.alphavantage.co/ API to get stock quotes, technical indicators,
and market analysis, then saves to Obsidian vault as a digest note.
"""

import argparse
import datetime
import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

import requests

from config import summarize, save_note, VAULT_PATH, TRACKER

# Alpha Vantage API configuration
ALPHA_VANTAGE_API = "https://www.alphavantage.co/query"
REQUEST_DELAY = 12  # Free tier: 5 requests per minute
TIMEOUT = 30

# Default stocks to track
DEFAULT_STOCKS = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN"]

ANALYSIS_PROMPT = """You are a financial analyst. Given stock market data from Alpha Vantage,
create a comprehensive analysis digest. For each stock:

1. Current price and recent trend
2. Key technical indicators and what they suggest
3. Volume and market activity
4. Any notable price movements or patterns

Also include:
- Market overview section with sentiment
- Key insights and observations
- Risk assessment
- Suggested [[wikilinks]] for financial concepts

Focus on clarity and actionable insights. Do NOT include YAML frontmatter or title heading -
start directly with the market overview."""


def get_alpha_vantage_key() -> str:
    """Get Alpha Vantage API key from environment or .env file."""
    key = os.environ.get("ALPHAVANTAGE_API_KEY")
    if not key:
        env_path = VAULT_PATH / ".env"
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if line.startswith("ALPHAVANTAGE_API_KEY="):
                    key = line.split("=", 1)[1].strip()
                    break
    if not key:
        raise ValueError(
            "ALPHAVANTAGE_API_KEY not found. "
            "Please set it in your environment or .env file. "
            "Get one free at https://www.alphavantage.co/support/#api-key"
        )
    return key


def fetch_stock_data(symbol: str, api_key: str) -> Optional[Dict[str, Any]]:
    """Fetch stock data (quote + SMA) from Alpha Vantage."""
    time.sleep(REQUEST_DELAY)
    
    # Get latest price
    quote_params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol,
        "apikey": api_key,
    }
    
    try:
        quote_resp = requests.get(ALPHA_VANTAGE_API, params=quote_params, timeout=TIMEOUT)
        quote_resp.raise_for_status()
        quote_data = quote_resp.json()
        
        if "Global Quote" not in quote_data or not quote_data["Global Quote"]:
            print(f"  Warning: No quote data for {symbol}")
            return None
        
        # Get SMA (20-day)
        time.sleep(REQUEST_DELAY)
        sma_params = {
            "function": "SMA",
            "symbol": symbol,
            "interval": "daily",
            "time_period": "20",
            "series_type": "close",
            "apikey": api_key,
        }
        sma_resp = requests.get(ALPHA_VANTAGE_API, params=sma_params, timeout=TIMEOUT)
        sma_resp.raise_for_status()
        sma_data = sma_resp.json()
        
        return {
            "symbol": symbol,
            "quote": quote_data["Global Quote"],
            "sma": sma_data.get("Technical Analysis: SMA", {}),
        }
    except Exception as e:
        print(f"  Error fetching data for {symbol}: {e}")
        return None


def format_stock_data(data: Dict[str, Any]) -> str:
    """Format stock data for AI analysis."""
    quote = data["quote"]
    symbol = data["symbol"]
    sma = data["sma"]
    
    latest_sma = None
    if sma:
        dates = sorted(sma.keys(), reverse=True)
        if dates:
            latest_sma = sma[dates[0]].get("SMA")
    
    return f"""**{symbol}**
Price: {quote.get('05. price', 'N/A')}
Change: {quote.get('09. change', 'N/A')} ({quote.get('10. change percent', 'N/A')})
Open: {quote.get('02. open', 'N/A')}
High: {quote.get('03. high', 'N/A')}
Low: {quote.get('04. low', 'N/A')}
Volume: {quote.get('06. volume', 'N/A')}
Latest Trading Day: {quote.get('07. latest trading day', 'N/A')}
Previous Close: {quote.get('08. previous close', 'N/A')}
20-day SMA: {latest_sma or 'N/A'}"""


def main():
    parser = argparse.ArgumentParser(
        description="Fetch stock market data from Alpha Vantage",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "-s", "--stocks", nargs="+", default=DEFAULT_STOCKS,
        help=f"Stock symbols to fetch (default: {', '.join(DEFAULT_STOCKS)})"
    )
    args = parser.parse_args()

    # Track operation start
    if TRACKER:
        TRACKER.record_operation(
            script_name="alpha_vantage.py",
            operation_type="fetch_stock_data",
            status="in_progress",
            metrics={"stocks": len(args.stocks)}
        )

    try:
        api_key = get_alpha_vantage_key()
        print(f"Fetching data for {len(args.stocks)} stocks...")
        
        all_stock_data = []
        for symbol in args.stocks:
            print(f"  Fetching {symbol}...")
            data = fetch_stock_data(symbol, api_key)
            if data:
                all_stock_data.append(data)
        
        if not all_stock_data:
            raise Exception("No stock data could be fetched")
        
        # Format data for AI
        stocks_text = "\n\n".join(format_stock_data(d) for d in all_stock_data)
        
        print(f"Generating analysis with AI...")
        analysis_body = summarize(stocks_text, ANALYSIS_PROMPT)
        
        # Save to Obsidian
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        filename = f"Alpha Vantage Digest - {today}.md"
        
        # Build table
        table_rows = []
        for data in all_stock_data:
            q = data["quote"]
            table_rows.append(
                f"| {data['symbol']} | {q.get('05. price', 'N/A')} | "
                f"{q.get('10. change percent', 'N/A')} | {q.get('06. volume', 'N/A')} |"
            )
        table = "\n".join(table_rows)
        
        note = f"""---
type: alpha-vantage-digest
date: {today}
stocks: [{', '.join(args.stocks)}]
tags:
  - source/alpha-vantage
  - finance
  - stocks
---

# Alpha Vantage Digest - {today}

> [!info] Market data for {len(all_stock_data)} stocks

## Stock Overview

| Symbol | Price | Change | Volume |
|--------|-------|--------|--------|
{table}

---

## AI Analysis

{analysis_body}

---

*Data provided by Alpha Vantage (https://www.alphavantage.co)*
"""
        
        save_note(f"Sources/{filename}", note)
        print(f"Digest saved to Sources/{filename}")
        
        # Track operation completion
        if TRACKER:
            TRACKER.record_operation(
                script_name="alpha_vantage.py",
                operation_type="fetch_stock_data",
                status="success",
                metrics={
                    "stocks": len(all_stock_data),
                    "output_file": f"Sources/{filename}"
                }
            )
        
    except Exception as e:
        print(f"Error: {e}")
        if TRACKER:
            TRACKER.record_operation(
                script_name="alpha_vantage.py",
                operation_type="fetch_stock_data",
                status="failed",
                metrics={"error": str(e)}
            )
        import sys
        sys.exit(1)


if __name__ == "__main__":
    main()
