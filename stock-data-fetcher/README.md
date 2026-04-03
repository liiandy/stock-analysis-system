# Stock Data Fetcher Skill

A comprehensive data fetching agent for the multi-agent stock analysis system. This skill retrieves real financial data from Yahoo Finance API and calculates technical indicators for downstream analysis.

## Quick Start

```bash
# Fetch data for TSMC (Taiwan Stock)
python scripts/fetch_data.py 2330.TW --output ./data/tsmc_data.json

# Fetch data for Apple (US Stock)
python scripts/fetch_data.py AAPL --output ./data/aapl_data.json --verbose

# Use default output filename
python scripts/fetch_data.py NVDA
```

## What Gets Fetched

### 1. Company Information
- Market cap, P/E ratio, P/B ratio, EPS, dividend yield
- 52-week high/low, beta, current/quick ratios
- Business summary, website, sector, industry

### 2. Financial Statements (Quarterly & Annual)
- Income Statement: Revenue, operating income, net income
- Balance Sheet: Assets, liabilities, equity, cash
- Cash Flow: Operating cash flow, capital expenditure

### 3. Price History (1-year daily data)
- OHLCV (Open, High, Low, Close, Volume)
- 6 Moving Averages: 5, 10, 20, 60, 120, 240-day SMA

### 4. Technical Indicators (Calculated from raw data, no external TA-Lib)
- **RSI (14-period)**: Relative Strength Index for momentum
- **MACD (12/26/9)**: Moving Average Convergence/Divergence with signal line
- **Bollinger Bands (20-period, 2σ)**: Upper, middle, lower bands
- **Stochastic KD (9-period)**: Fast %K and slow %D lines

### 5. News & Market Data
- Recent headlines (last 30 days)
- Major shareholders information
- Institutional holdings
- Analyst recommendations and price targets

### 6. Metadata
- Fetch timestamp and data freshness
- API status and list of any missing data
- Error tracking for robust error handling

## Output Format

JSON file with complete data package:

```json
{
  "metadata": {
    "ticker": "2330.TW",
    "fetch_timestamp": "2026-04-03T10:30:00Z",
    "api_status": "success",
    "missing_data": []
  },
  "company_info": { /* company details */ },
  "price_history": [ /* daily OHLCV + MAs */ ],
  "technical_indicators": {
    "rsi_14": { "value": 65.2, "interpretation": "neutral" },
    "macd": { "macd": 0.15, "signal": 0.12, "histogram": 0.03 },
    "bollinger_bands": { "upper": 185.5, "middle": 180.0, "lower": 174.5 },
    "stochastic_kd": { "k_percent": 72.5, "d_percent": 68.3 }
  },
  "financial_statements": { /* income, balance sheet, cash flow */ },
  "news": [ /* recent headlines */ ],
  "holders": { /* major shareholders */ },
  "analyst_data": { /* recommendations */ }
}
```

## Features

- **Comprehensive Data**: Fetches all key financial data in one call
- **Technical Indicators**: RSI, MACD, Bollinger Bands, KD Stochastic calculated from scratch
- **Robust Error Handling**: Retries, timeouts, graceful degradation
- **Multi-Market Support**: Taiwan Stock (2330.TW), US Stock (AAPL, NVDA, etc.)
- **JSON Output**: Easy integration with downstream analysis agents
- **Verbose Logging**: Optional debug output for troubleshooting
- **Type Safety**: All data converted to JSON-serializable formats

## Dependencies

```
yfinance>=0.2.0     # Yahoo Finance data
pandas>=1.5.0       # Data manipulation
numpy>=1.23.0       # Numerical computing
requests>=2.28.0    # HTTP resilience
```

## Installation

```bash
pip install yfinance pandas numpy requests
```

## Technical Implementation

### Technical Indicators (All calculated from raw data)

1. **RSI**: Calculated using EMA of gains/losses over 14 periods
2. **MACD**: 12-period EMA minus 26-period EMA with 9-period signal line
3. **Bollinger Bands**: 20-period SMA ± (2 × standard deviation)
4. **Stochastic KD**: 
   - %K = (Close - 9-period Low) / (9-period High - 9-period Low) × 100
   - %D = 3-period SMA of %K

### Error Handling Strategy

- **Retry Logic**: Up to 3 retries for failed API calls
- **Timeout Protection**: Skips sources that exceed time limits
- **Fallback**: If one data source fails, continues fetching others
- **Graceful Degradation**: Partial data better than none
- **Data Validation**: NaN and timestamp conversion for JSON compatibility

## Integration with Multi-Agent System

This skill provides the foundational data layer for:
- **Technical Analysis Agent**: Uses price history and indicators
- **Fundamental Analysis Agent**: Uses financial statements
- **Sentiment Analysis Agent**: Uses news for context
- **Portfolio Manager**: Aggregates data for multiple stocks

## Architecture

```
fetch_data.py
├── StockDataFetcher (main class)
│   ├── fetch() - orchestrates all data fetching
│   ├── _fetch_company_info() - company metrics
│   ├── _fetch_price_history() - daily OHLCV + MAs
│   ├── _fetch_financial_statements() - income, balance, cash flow
│   ├── _fetch_news() - recent headlines
│   ├── _fetch_holders() - shareholder data
│   ├── _fetch_analyst_data() - recommendations
│   ├── _calculate_technical_indicators() - RSI, MACD, BB, KD
│   └── save_to_json() - export results
│
└── Helper Functions
    ├── _serialize_value() - convert to JSON types
    ├── _serialize_timestamp() - ISO format timestamps
    └── _interpret_*() - indicator interpretations
```

## Usage Examples

### Basic Usage
```bash
python scripts/fetch_data.py 2330.TW
# Creates: stock_data_2330.TW.json
```

### Custom Output Path
```bash
python scripts/fetch_data.py AAPL --output /data/stocks/apple.json
```

### Verbose Mode
```bash
python scripts/fetch_data.py NVDA --output ./nvda.json --verbose
```

### Programmatic Usage
```python
from scripts.fetch_data import StockDataFetcher
import json

fetcher = StockDataFetcher("2330.TW")
data = fetcher.fetch()
fetcher.save_to_json("./output.json")

# Access specific data
rsi = data["technical_indicators"]["rsi_14"]["value"]
latest_price = data["price_history"][-1]["close"]
```

## Error Handling

If a data source fails:
1. The fetch continues with other sources
2. Failures are logged in `metadata.missing_data`
3. Partial JSON output is still saved
4. `api_status` indicates success/error

Example error response:
```json
{
  "metadata": {
    "api_status": "error: Network timeout",
    "missing_data": ["news", "analyst_data"]
  },
  "company_info": { /* still fetched */ },
  "price_history": [ /* still fetched */ ],
  ...
}
```

## Testing

The script includes:
- Argument validation
- Network error handling
- Type conversion verification
- JSON serialization testing

Tested with:
- Taiwan stocks: 2330.TW (TSMC), 2454.TW (MediaTek)
- US stocks: AAPL, NVDA, MSFT
- International markets supported by Yahoo Finance

## Performance

- Typical fetch time: 10-30 seconds depending on data availability
- Data freshness: Same-day for most metrics
- Historical data: 1 year of daily OHLCV
- Rate limiting: Respects Yahoo Finance API limits

## License

Part of the multi-agent stock analysis system.
