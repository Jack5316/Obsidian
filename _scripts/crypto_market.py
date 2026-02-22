#!/usr/bin/env python3
"""Fetch and analyze cryptocurrency market data using CoinGecko API.

Uses the free CoinGecko API (no API key needed) to get crypto prices,
market data, and analysis, then saves to Obsidian vault as a digest note.
"""

import argparse
import datetime
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

import requests

from config import summarize, save_note, VAULT_PATH, TRACKER

# CoinGecko API configuration
COINGECKO_API = "https://api.coingecko.com/api/v3"
REQUEST_DELAY = 1.5  # Be nice to the free API
TIMEOUT = 30

# Default cryptocurrencies to track
DEFAULT_CRYPTOS = ["bitcoin", "ethereum", "solana", "cardano", "polkadot"]
DEFAULT_CURRENCY = "usd"

ANALYSIS_PROMPT = """You are a cryptocurrency market analyst. Given crypto market data from CoinGecko,
create a comprehensive analysis digest. For each cryptocurrency:

1. Current price and market cap
2. 24h price movement and trend
3. Volume and market activity
4. Rank and market dominance

Also include:
- Market overview with sentiment
- Key movers & shakers
- Risk assessment
- Suggested [[wikilinks]] for crypto/financial concepts

Focus on clarity and actionable insights. Do NOT include YAML frontmatter or title heading -
start directly with the market overview."""


def fetch_crypto_data(coin_ids: List[str], currency: str = DEFAULT_CURRENCY) -> List[Dict[str, Any]]:
    """Fetch crypto market data from CoinGecko."""
    params = {
        "ids": ",".join(coin_ids),
        "vs_currency": currency,
        "order": "market_cap_desc",
        "per_page": 100,
        "page": 1,
        "sparkline": "false",
        "price_change_percentage": "24h,7d,30d",
    }
    
    try:
        time.sleep(REQUEST_DELAY)
        resp = requests.get(
            f"{COINGECKO_API}/coins/markets",
            params=params,
            timeout=TIMEOUT
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"  Error fetching crypto data: {e}")
        return []


def format_crypto_data(coin: Dict[str, Any]) -> str:
    """Format crypto data for AI analysis."""
    return f"""**{coin.get('name', 'N/A')} ({coin.get('symbol', 'N/A').upper()})**
Price: ${coin.get('current_price', 'N/A'):,.2f}
Market Cap: ${coin.get('market_cap', 'N/A'):,.0f}
Rank: #{coin.get('market_cap_rank', 'N/A')}
24h Change: {coin.get('price_change_percentage_24h', 0):+.2f}%
7d Change: {coin.get('price_change_percentage_7d_in_currency', 0):+.2f}%
30d Change: {coin.get('price_change_percentage_30d_in_currency', 0):+.2f}%
24h Volume: ${coin.get('total_volume', 'N/A'):,.0f}
High 24h: ${coin.get('high_24h', 'N/A'):,.2f}
Low 24h: ${coin.get('low_24h', 'N/A'):,.2f}"""


def main():
    parser = argparse.ArgumentParser(
        description="Fetch crypto market data from CoinGecko",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "-c", "--cryptos", nargs="+", default=DEFAULT_CRYPTOS,
        help=f"Crypto coin IDs to fetch (default: {', '.join(DEFAULT_CRYPTOS)})"
    )
    parser.add_argument(
        "--currency", default=DEFAULT_CURRENCY,
        help=f"Currency for prices (default: {DEFAULT_CURRENCY})"
    )
    args = parser.parse_args()

    # Track operation start
    if TRACKER:
        TRACKER.record_operation(
            script_name="crypto_market.py",
            operation_type="fetch_crypto_data",
            status="in_progress",
            metrics={"cryptos": len(args.cryptos)}
        )

    try:
        print(f"Fetching crypto data for {len(args.cryptos)} coins...")
        crypto_data = fetch_crypto_data(args.cryptos, args.currency)
        
        if not crypto_data:
            raise Exception("No crypto data could be fetched")
        
        print(f"Got data for {len(crypto_data)} coins")
        
        # Format data for AI
        cryptos_text = "\n\n".join(format_crypto_data(c) for c in crypto_data)
        
        print(f"Generating analysis with AI...")
        analysis_body = summarize(cryptos_text, ANALYSIS_PROMPT)
        
        # Save to Obsidian
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        filename = f"Crypto Market Digest - {today}.md"
        
        # Build table
        table_rows = []
        for coin in crypto_data:
            change_24h = coin.get('price_change_percentage_24h', 0)
            table_rows.append(
                f"| {coin.get('name', 'N/A')} ({coin.get('symbol', 'N/A').upper()}) | "
                f"${coin.get('current_price', 0):,.2f} | "
                f"{change_24h:+.2f}% | "
                f"#{coin.get('market_cap_rank', 'N/A')} |"
            )
        table = "\n".join(table_rows)
        
        note = f"""---
type: crypto-digest
date: {today}
cryptos: [{', '.join(args.cryptos)}]
tags:
  - source/coingecko
  - finance
  - crypto
---

# Crypto Market Digest - {today}

> [!info] Market data for {len(crypto_data)} cryptocurrencies

## Market Overview

| Coin | Price | 24h Change | Rank |
|------|-------|------------|------|
{table}

---

## AI Analysis

{analysis_body}

---

*Data provided by CoinGecko (https://www.coingecko.com)*
"""
        
        save_note(f"Sources/{filename}", note)
        print(f"Digest saved to Sources/{filename}")
        
        # Track operation completion
        if TRACKER:
            TRACKER.record_operation(
                script_name="crypto_market.py",
                operation_type="fetch_crypto_data",
                status="success",
                metrics={
                    "cryptos": len(crypto_data),
                    "output_file": f"Sources/{filename}"
                }
            )
        
    except Exception as e:
        print(f"Error: {e}")
        if TRACKER:
            TRACKER.record_operation(
                script_name="crypto_market.py",
                operation_type="fetch_crypto_data",
                status="failed",
                metrics={"error": str(e)}
            )
        import sys
        sys.exit(1)


if __name__ == "__main__":
    main()
