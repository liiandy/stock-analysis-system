#!/usr/bin/env python3
"""
Quick Quote — lightweight single-call stock data lookup.
Returns only basic company info (price, PE, EPS, etc.) as JSON.
Designed for quick_answer mode where no full analysis is needed.

Usage:
    python quick_quote.py 2330.TW
    python quick_quote.py AAPL --fields current_price,pe_ratio
"""

import argparse
import json
import sys
from datetime import datetime
from typing import Dict, List, Optional

import yfinance as yf


# Map of field names to yfinance info keys
FIELD_MAP = {
    "current_price": ("currentPrice", "regularMarketPrice", "previousClose"),
    "previous_close": ("previousClose",),
    "pe_ratio": ("trailingPE",),
    "forward_pe": ("forwardPE",),
    "pb_ratio": ("priceToBook",),
    "eps": ("trailingEps",),
    "dividend_yield": ("dividendYield",),
    "market_cap": ("marketCap",),
    "return_on_equity": ("returnOnEquity",),
    "debt_to_equity": ("debtToEquity",),
    "revenue": ("totalRevenue",),
    "profit_margin": ("profitMargins",),
    "operating_margin": ("operatingMargins",),
    "52_week_high": ("fiftyTwoWeekHigh",),
    "52_week_low": ("fiftyTwoWeekLow",),
    "beta": ("beta",),
    "sector": ("sector",),
    "industry": ("industry",),
    "currency": ("currency",),
    "company_name": ("longName", "shortName"),
}


def extract_field(info: dict, keys: tuple):
    """Try multiple yfinance keys, return the first non-None value."""
    for key in keys:
        val = info.get(key)
        if val is not None:
            return val
    return None


def quick_quote(ticker: str, fields: Optional[List[str]] = None) -> dict:
    """Fetch minimal stock data from yfinance."""
    yf_ticker = yf.Ticker(ticker)
    info = yf_ticker.info

    if fields:
        target_fields = {k: v for k, v in FIELD_MAP.items() if k in fields}
    else:
        target_fields = FIELD_MAP

    result = {"ticker": ticker, "timestamp": datetime.now().isoformat()}
    for field_name, yf_keys in target_fields.items():
        val = extract_field(info, yf_keys)
        # Format percentages
        if val is not None and field_name in ("dividend_yield", "return_on_equity", "profit_margin", "operating_margin"):
            result[field_name] = round(val * 100, 2)
            result[f"{field_name}_fmt"] = f"{val * 100:.2f}%"
        elif val is not None and field_name == "market_cap":
            result[field_name] = val
            if val >= 1e12:
                result[f"{field_name}_fmt"] = f"{val / 1e12:.2f}兆"
            elif val >= 1e8:
                result[f"{field_name}_fmt"] = f"{val / 1e8:.1f}億"
            else:
                result[field_name] = val
        else:
            result[field_name] = val

    return result


def main():
    parser = argparse.ArgumentParser(description="Quick stock quote lookup")
    parser.add_argument("ticker", help="Stock ticker (e.g., 2330.TW, AAPL)")
    parser.add_argument("--fields", "-f", default=None,
                        help="Comma-separated fields to fetch (default: all)")
    args = parser.parse_args()

    try:
        fields = args.fields.split(",") if args.fields else None
        result = quick_quote(args.ticker.upper(), fields)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
