#!/usr/bin/env python3
"""
Stock Data Fetcher for Multi-Agent Stock Analysis System
Fetches comprehensive financial data from Yahoo Finance API using yfinance library.

Supports Taiwan Stock Exchange (e.g., 2330.TW) and US Stock Exchange (e.g., AAPL).
Calculates technical indicators (RSI, MACD, Bollinger Bands, KD Stochastic) from raw OHLCV data.
Outputs a comprehensive JSON data package with all financial data, price history, and technical indicators.

Usage:
    python fetch_data.py 2330.TW --output /path/to/output.json
    python fetch_data.py AAPL --output ./data/aapl_data.json --verbose
"""

import argparse
import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import yfinance as yf
from pandas import DataFrame, Timestamp


# Configure logging
def setup_logging(verbose: bool = False) -> logging.Logger:
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)


logger = setup_logging()


class StockDataFetcher:
    """Fetches and processes comprehensive stock data from Yahoo Finance."""

    def __init__(self, ticker: str, verbose: bool = False):
        """
        Initialize the fetcher.

        Args:
            ticker: Stock ticker symbol (e.g., "2330.TW", "AAPL")
            verbose: Enable verbose logging
        """
        self.ticker = ticker
        self.verbose = verbose
        self.logger = setup_logging(verbose)
        self.data = {
            "metadata": {
                "ticker": ticker,
                "fetch_timestamp": None,
                "data_freshness": None,
                "missing_data": [],
                "api_status": "pending"
            },
            "company_info": {},
            "price_history": [],
            "technical_indicators": {},
            "financial_statements": {
                "income_statement": {},
                "balance_sheet": {},
                "cash_flow": {}
            },
            "news": [],
            "holders": {},
            "analyst_data": {}
        }
        self.yf_ticker = None
        self.price_df = None

    def fetch(self) -> Dict[str, Any]:
        """
        Fetch all stock data.

        Returns:
            Dictionary containing all fetched stock data
        """
        try:
            self.logger.info(f"Starting data fetch for ticker: {self.ticker}")
            self.data["metadata"]["fetch_timestamp"] = datetime.utcnow().isoformat() + "Z"

            # Initialize yfinance ticker object
            self._init_yfinance_ticker()

            # Fetch data from various sources
            self._fetch_company_info()
            self._fetch_price_history()
            self._fetch_financial_statements()
            self._fetch_news()
            self._fetch_holders()
            self._fetch_analyst_data()
            self._calculate_technical_indicators()

            self.data["metadata"]["api_status"] = "success"
            self.logger.info(f"Successfully fetched data for {self.ticker}")

        except Exception as e:
            self.logger.error(f"Error during data fetch: {str(e)}")
            self.data["metadata"]["api_status"] = f"error: {str(e)}"
            self.data["metadata"]["missing_data"].append("all_data_due_to_error")

        return self.data

    def _init_yfinance_ticker(self) -> None:
        """Initialize yfinance ticker object with retries."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self.yf_ticker = yf.Ticker(self.ticker)
                # Test if ticker is valid by fetching basic info
                _ = self.yf_ticker.info
                self.logger.debug(f"Yfinance ticker initialized: {self.ticker}")
                return
            except Exception as e:
                self.logger.warning(f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}")
                if attempt == max_retries - 1:
                    raise

    def _fetch_company_info(self) -> None:
        """Fetch company information."""
        try:
            self.logger.debug("Fetching company information...")
            info = self.yf_ticker.info

            company_info = {
                "name": info.get("longName", ""),
                "sector": info.get("sector", ""),
                "industry": info.get("industry", ""),
                "market_cap": _serialize_value(info.get("marketCap")),
                "pe_ratio": _serialize_value(info.get("trailingPE")),
                "forward_pe": _serialize_value(info.get("forwardPE")),
                "peg_ratio": _serialize_value(info.get("pegRatio")),
                "pb_ratio": _serialize_value(info.get("priceToBook")),
                "eps": _serialize_value(info.get("trailingEps")),
                "dividend_yield": _serialize_value(info.get("dividendYield")),
                "dividend_rate": _serialize_value(info.get("dividendRate")),
                "trailing_12_month_revenue": _serialize_value(info.get("totalRevenue")),
                "profit_margin": _serialize_value(info.get("profitMargins")),
                "operating_margin": _serialize_value(info.get("operatingMargins")),
                "return_on_equity": _serialize_value(info.get("returnOnEquity")),
                "return_on_assets": _serialize_value(info.get("returnOnAssets")),
                "debt_to_equity": _serialize_value(info.get("debtToEquity")),
                "current_ratio": _serialize_value(info.get("currentRatio")),
                "quick_ratio": _serialize_value(info.get("quickRatio")),
                "five_year_avg_dividend_yield": _serialize_value(info.get("fiveYearAvgDividendYield")),
                "52_week_high": _serialize_value(info.get("fiftyTwoWeekHigh")),
                "52_week_low": _serialize_value(info.get("fiftyTwoWeekLow")),
                "50_day_average": _serialize_value(info.get("fiftyDayAverage")),
                "200_day_average": _serialize_value(info.get("twoHundredDayAverage")),
                "beta": _serialize_value(info.get("beta")),
                "website": info.get("website", ""),
                "description": info.get("longBusinessSummary", "")[:500],  # Truncate for brevity
            }

            self.data["company_info"] = company_info
            self.logger.debug("Company information fetched successfully")

        except Exception as e:
            self.logger.warning(f"Failed to fetch company info: {str(e)}")
            self.data["metadata"]["missing_data"].append("company_info")

    def _fetch_price_history(self) -> None:
        """Fetch historical price data (1 year of daily data)."""
        try:
            self.logger.debug("Fetching price history...")
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)

            self.price_df = self.yf_ticker.history(start=start_date, end=end_date)

            if self.price_df.empty:
                raise ValueError("No price data retrieved")

            # Add moving averages
            self.price_df['MA_5'] = self.price_df['Close'].rolling(window=5, min_periods=1).mean()
            self.price_df['MA_10'] = self.price_df['Close'].rolling(window=10, min_periods=1).mean()
            self.price_df['MA_20'] = self.price_df['Close'].rolling(window=20, min_periods=1).mean()
            self.price_df['MA_60'] = self.price_df['Close'].rolling(window=60, min_periods=1).mean()
            self.price_df['MA_120'] = self.price_df['Close'].rolling(window=120, min_periods=1).mean()
            self.price_df['MA_240'] = self.price_df['Close'].rolling(window=240, min_periods=1).mean()

            # Convert to serializable format
            price_history = []
            for date, row in self.price_df.iterrows():
                price_record = {
                    "date": date.strftime("%Y-%m-%d"),
                    "open": _serialize_value(row['Open']),
                    "high": _serialize_value(row['High']),
                    "low": _serialize_value(row['Low']),
                    "close": _serialize_value(row['Close']),
                    "volume": int(row['Volume']) if pd.notna(row['Volume']) else None,
                    "ma_5": _serialize_value(row['MA_5']),
                    "ma_10": _serialize_value(row['MA_10']),
                    "ma_20": _serialize_value(row['MA_20']),
                    "ma_60": _serialize_value(row['MA_60']),
                    "ma_120": _serialize_value(row['MA_120']),
                    "ma_240": _serialize_value(row['MA_240']),
                }
                price_history.append(price_record)

            self.data["price_history"] = price_history
            self.logger.debug(f"Price history fetched: {len(price_history)} records")

        except Exception as e:
            self.logger.warning(f"Failed to fetch price history: {str(e)}")
            self.data["metadata"]["missing_data"].append("price_history")

    def _calculate_technical_indicators(self) -> None:
        """Calculate technical indicators from price data."""
        if self.price_df is None or self.price_df.empty:
            self.logger.warning("Cannot calculate technical indicators: no price data")
            return

        try:
            self.logger.debug("Calculating technical indicators...")

            # RSI (14-period)
            rsi = self._calculate_rsi(self.price_df['Close'], period=14)

            # MACD (12/26/9)
            macd, macd_signal, macd_hist = self._calculate_macd(self.price_df['Close'])

            # Bollinger Bands (20-period, 2 std dev)
            bb_upper, bb_middle, bb_lower = self._calculate_bollinger_bands(
                self.price_df['Close'], period=20, std_dev=2
            )

            # Stochastic KD (9-period)
            k_percent, d_percent = self._calculate_stochastic(
                self.price_df['High'], self.price_df['Low'], self.price_df['Close'], period=9
            )

            # Get latest values
            latest_idx = -1
            indicators = {
                "rsi_14": {
                    "value": _serialize_value(rsi.iloc[latest_idx]),
                    "period": 14,
                    "interpretation": _interpret_rsi(rsi.iloc[latest_idx])
                },
                "macd": {
                    "macd": _serialize_value(macd.iloc[latest_idx]),
                    "signal": _serialize_value(macd_signal.iloc[latest_idx]),
                    "histogram": _serialize_value(macd_hist.iloc[latest_idx]),
                    "periods": "12/26/9"
                },
                "bollinger_bands": {
                    "upper": _serialize_value(bb_upper.iloc[latest_idx]),
                    "middle": _serialize_value(bb_middle.iloc[latest_idx]),
                    "lower": _serialize_value(bb_lower.iloc[latest_idx]),
                    "period": 20,
                    "std_dev": 2
                },
                "stochastic_kd": {
                    "k_percent": _serialize_value(k_percent.iloc[latest_idx]),
                    "d_percent": _serialize_value(d_percent.iloc[latest_idx]),
                    "period": 9,
                    "interpretation": _interpret_stochastic(k_percent.iloc[latest_idx], d_percent.iloc[latest_idx])
                }
            }

            self.data["technical_indicators"] = indicators
            self.logger.debug("Technical indicators calculated successfully")

        except Exception as e:
            self.logger.warning(f"Failed to calculate technical indicators: {str(e)}")
            self.data["metadata"]["missing_data"].append("technical_indicators")

    @staticmethod
    def _calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period, min_periods=1).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period, min_periods=1).mean()

        rs = gain / loss.replace(0, np.nan)
        rsi = 100 - (100 / (1 + rs))
        return rsi

    @staticmethod
    def _calculate_macd(prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate MACD indicator."""
        ema_fast = prices.ewm(span=fast, adjust=False).mean()
        ema_slow = prices.ewm(span=slow, adjust=False).mean()
        macd = ema_fast - ema_slow
        macd_signal = macd.ewm(span=signal, adjust=False).mean()
        macd_hist = macd - macd_signal
        return macd, macd_signal, macd_hist

    @staticmethod
    def _calculate_bollinger_bands(prices: pd.Series, period: int = 20, std_dev: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate Bollinger Bands."""
        sma = prices.rolling(window=period, min_periods=1).mean()
        std = prices.rolling(window=period, min_periods=1).std()
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        return upper_band, sma, lower_band

    @staticmethod
    def _calculate_stochastic(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 9) -> Tuple[pd.Series, pd.Series]:
        """Calculate Stochastic %K and %D."""
        low_min = low.rolling(window=period, min_periods=1).min()
        high_max = high.rolling(window=period, min_periods=1).max()

        k_percent = 100 * ((close - low_min) / (high_max - low_min).replace(0, np.nan))
        d_percent = k_percent.rolling(window=3, min_periods=1).mean()

        return k_percent, d_percent

    def _fetch_financial_statements(self) -> None:
        """Fetch income statement, balance sheet, and cash flow statements."""
        try:
            self.logger.debug("Fetching financial statements...")

            financials = {
                "income_statement": self._process_financials(self.yf_ticker.quarterly_financials, "income_statement"),
                "balance_sheet": self._process_financials(self.yf_ticker.quarterly_balance_sheet, "balance_sheet"),
                "cash_flow": self._process_financials(self.yf_ticker.quarterly_cashflow, "cash_flow")
            }

            self.data["financial_statements"] = financials
            self.logger.debug("Financial statements fetched successfully")

        except Exception as e:
            self.logger.warning(f"Failed to fetch financial statements: {str(e)}")
            self.data["metadata"]["missing_data"].append("financial_statements")

    @staticmethod
    def _process_financials(financial_df: DataFrame, statement_type: str) -> Dict[str, Any]:
        """Process financial statement dataframes."""
        if financial_df is None or financial_df.empty:
            return {}

        result = {}
        try:
            # Get last 4 quarters
            cols = financial_df.columns[:4] if len(financial_df.columns) >= 4 else financial_df.columns
            for date in cols:
                date_str = date.strftime("%Y-%m-%d")
                result[date_str] = {}
                for index, value in financial_df[date].items():
                    result[date_str][str(index)] = _serialize_value(value)
        except Exception as e:
            logging.getLogger(__name__).warning(f"Error processing {statement_type}: {str(e)}")

        return result

    def _fetch_news(self) -> None:
        """Fetch recent news headlines."""
        try:
            self.logger.debug("Fetching news...")
            news_list = []

            try:
                news_data = self.yf_ticker.news
                if news_data:
                    for article in news_data[:20]:  # Limit to 20 most recent
                        news_record = {
                            "title": article.get("title", ""),
                            "publisher": article.get("publisher", ""),
                            "link": article.get("link", ""),
                            "publish_date": _serialize_timestamp(article.get("providerPublishTime")),
                            "type": article.get("type", "")
                        }
                        news_list.append(news_record)
            except Exception as e:
                self.logger.debug(f"News fetching encountered: {str(e)}")

            self.data["news"] = news_list
            self.logger.debug(f"News fetched: {len(news_list)} articles")

        except Exception as e:
            self.logger.warning(f"Failed to fetch news: {str(e)}")
            self.data["metadata"]["missing_data"].append("news")

    def _fetch_holders(self) -> None:
        """Fetch major shareholders information."""
        try:
            self.logger.debug("Fetching holders information...")

            holders_info = {}

            # Major holders
            try:
                major_holders = self.yf_ticker.major_holders
                if major_holders is not None and not major_holders.empty:
                    major_holders_list = []
                    for _, row in major_holders.iterrows():
                        major_holders_list.append({
                            "holder": row.get(0, ""),
                            "percentage": str(row.get(1, ""))
                        })
                    holders_info["major_holders"] = major_holders_list
            except Exception as e:
                self.logger.debug(f"Major holders fetch: {str(e)}")

            # Institutional holders
            try:
                inst_holders = self.yf_ticker.institutional_holders
                if inst_holders is not None and not inst_holders.empty:
                    inst_list = []
                    for _, row in inst_holders.iterrows():
                        inst_list.append({
                            "holder": row.get("Holder", ""),
                            "shares": _serialize_value(row.get("Shares", 0)),
                            "date_reported": str(row.get("Date Reported", ""))
                        })
                    holders_info["institutional_holders"] = inst_list[:10]  # Top 10
            except Exception as e:
                self.logger.debug(f"Institutional holders fetch: {str(e)}")

            self.data["holders"] = holders_info
            self.logger.debug("Holders information fetched")

        except Exception as e:
            self.logger.warning(f"Failed to fetch holders: {str(e)}")
            self.data["metadata"]["missing_data"].append("holders")

    def _fetch_analyst_data(self) -> None:
        """Fetch analyst recommendations and price targets."""
        try:
            self.logger.debug("Fetching analyst data...")

            analyst_info = {}

            # Recommendations
            try:
                recommendations = self.yf_ticker.recommendations
                if recommendations is not None and not recommendations.empty:
                    recent_rec = recommendations.tail(1)
                    if not recent_rec.empty:
                        rec_row = recent_rec.iloc[0]
                        analyst_info["recent_recommendation"] = {
                            "strong_buy": int(rec_row.get("strongBuy", 0)),
                            "buy": int(rec_row.get("buy", 0)),
                            "hold": int(rec_row.get("hold", 0)),
                            "sell": int(rec_row.get("sell", 0)),
                            "strong_sell": int(rec_row.get("strongSell", 0)),
                            "date": str(recent_rec.index[0])
                        }
            except Exception as e:
                self.logger.debug(f"Recommendations fetch: {str(e)}")

            # Target price
            try:
                target_price = self.yf_ticker.info.get("targetMeanPrice")
                if target_price:
                    analyst_info["target_mean_price"] = _serialize_value(target_price)
            except Exception as e:
                self.logger.debug(f"Target price fetch: {str(e)}")

            self.data["analyst_data"] = analyst_info
            self.logger.debug("Analyst data fetched")

        except Exception as e:
            self.logger.warning(f"Failed to fetch analyst data: {str(e)}")
            self.data["metadata"]["missing_data"].append("analyst_data")

    def save_to_json(self, output_path: str) -> None:
        """
        Save fetched data to JSON file.

        Args:
            output_path: Path to save the JSON file
        """
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Data saved to: {output_file}")

        except Exception as e:
            self.logger.error(f"Failed to save data to JSON: {str(e)}")
            raise


def _serialize_value(value: Any) -> Any:
    """Convert pandas/numpy types to JSON-serializable Python types."""
    if value is None:
        return None
    if pd.isna(value):
        return None
    if isinstance(value, (np.integer, np.floating)):
        return float(value)
    if isinstance(value, (int, float)):
        return value
    if isinstance(value, str):
        return value
    if isinstance(value, bool):
        return value
    if isinstance(value, (list, dict)):
        return value
    return str(value)


def _serialize_timestamp(timestamp: Any) -> Optional[str]:
    """Convert timestamp to ISO format string."""
    if timestamp is None:
        return None
    if isinstance(timestamp, Timestamp):
        return timestamp.isoformat()
    if isinstance(timestamp, datetime):
        return timestamp.isoformat()
    if isinstance(timestamp, int):
        # Unix timestamp
        return datetime.fromtimestamp(timestamp).isoformat()
    return str(timestamp)


def _interpret_rsi(rsi_value: float) -> str:
    """Interpret RSI value."""
    if pd.isna(rsi_value):
        return "insufficient data"
    if rsi_value >= 70:
        return "overbought"
    elif rsi_value <= 30:
        return "oversold"
    else:
        return "neutral"


def _interpret_stochastic(k_value: float, d_value: float) -> str:
    """Interpret Stochastic KD values."""
    if pd.isna(k_value) or pd.isna(d_value):
        return "insufficient data"
    if k_value >= 80 or d_value >= 80:
        return "overbought"
    elif k_value <= 20 or d_value <= 20:
        return "oversold"
    elif k_value > d_value:
        return "uptrend"
    else:
        return "downtrend"


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Fetch comprehensive stock data from Yahoo Finance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python fetch_data.py 2330.TW --output ./data/tsmc.json
  python fetch_data.py AAPL --output ./data/aapl.json --verbose
  python fetch_data.py NVDA
        """
    )

    parser.add_argument(
        "ticker",
        help="Stock ticker symbol (e.g., 2330.TW for TSMC, AAPL for Apple)"
    )

    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output JSON file path (default: ./stock_data_{ticker}.json)"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Setup logging
    logger_main = setup_logging(args.verbose)

    try:
        # Validate ticker format
        ticker = args.ticker.upper()
        logger_main.info(f"Processing ticker: {ticker}")

        # Fetch data
        fetcher = StockDataFetcher(ticker, verbose=args.verbose)
        fetcher.fetch()

        # Determine output path
        output_path = args.output or f"./stock_data_{ticker}.json"

        # Save to JSON
        fetcher.save_to_json(output_path)

        logger_main.info(f"Successfully completed data fetch for {ticker}")
        print(json.dumps({"status": "success", "ticker": ticker, "output": output_path}, indent=2))

        sys.exit(0)

    except Exception as e:
        logger_main.error(f"Fatal error: {str(e)}", exc_info=True)
        print(json.dumps({"status": "error", "message": str(e)}, indent=2), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
