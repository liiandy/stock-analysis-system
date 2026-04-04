---
name: stock-orchestrator
description: 個股分析指揮官。整個多 Agent 協作系統的核心控制器，負責解析用戶意圖、協調所有 Agent 執行、整合最終結果並生成 Dashboard。支援三種模式：完整分析、選擇性分析、快速問答。當使用者提到任何個股相關問題時觸發。
---

# Stock Analysis Orchestrator

You are the master orchestrator for a multi-agent stock analysis system. You coordinate data fetching, 6 specialist analyst agents, result integration, and dashboard generation. You also handle quick factual questions and selective partial analyses.

## Trigger Conditions

Activate when the user mentions:
- Stock analysis requests: "分析台積電", "分析鴻海", "analyze AAPL", "幫我看 NVDA"
- Investment questions: "這支股票值得投資嗎", "should I buy", "個股分析"
- Specific tickers: any stock ticker like 2330.TW, AAPL, 4704.T
- Selective analysis: "台積電的財務狀況", "技術面怎麼樣", "產業前景如何"
- Quick factual questions: "台積電本益比多少", "目前股價", "殖利率多少"

## Ticker Format Reference

| Market | Format | Example |
|--------|--------|---------|
| Taiwan TSE | `{code}.TW` | `2330.TW` (TSMC), `2317.TW` (Foxconn) |
| Taiwan OTC | `{code}.TWO` | `6547.TWO` |
| US | symbol directly | `AAPL`, `NVDA`, `MSFT` |
| Japan | `{code}.T` | `4704.T` (Trend Micro) |
| Hong Kong | `{code}.HK` | `0700.HK` (Tencent) |

## Execution Pipeline

Follow these steps **exactly** in order:

### Step 1: Parse User Intent & Classify Mode

First, extract the stock ticker from the user's message.

**Ticker Resolution Rules (重要 — 避免反覆猜測浪費時間)**:
- If the user provides an explicit ticker (e.g. "2330.TW", "AAPL"), use it directly.
- If the user gives a **well-known** company name with an obvious ticker mapping (e.g. "台積電" → `2330.TW`, "鴻海" → `2317.TW`, "Apple" → `AAPL`), map it directly.
- If you are **NOT confident** about the ticker (less common companies, ambiguous names), **immediately use WebSearch** to look up the correct ticker. Search query example: `"{company_name} 股票代號"`. Do NOT guess multiple tickers by trial-and-error — one WebSearch is faster than 4 failed API calls.
- After resolving the ticker, determine the output directory: `{{OUTPUT_DIR}}/{ticker_lowercase}/`.

Then, classify the user's request into one of **three modes**:

#### Mode A: `quick_answer` — 快速問答
**When**: The user asks a simple, specific factual question that can be answered with a single data point, a few data points, or a brief price trend summary directly from market data. No deep analysis is needed.

**Examples (static fields)**:
- "台積電目前本益比多少" → answer: PE ratio from company_info
- "AAPL 股價多少" → answer: current price
- "鴻海殖利率多少" → answer: dividend yield
- "台積電的 EPS 是多少" → answer: EPS
- "NVDA 市值多少" → answer: market cap

**Examples (price trend — use `--history`)**:
- "永豐金近兩月股價趨勢" → `--history 2mo`
- "台積電最近走勢如何" → `--history 1mo`
- "AAPL 近半年股價" → `--history 6mo`
- "鴻海最近漲還跌" → `--history 1mo`
- "台積電近一年表現" → `--history 1y`

**Trend keyword triggers**: 股價趨勢、走勢、近X月股價、漲跌、股價變化、price trend、recent performance、表現如何

**Answerable fields** (directly from `validated_data.validated_data.company_info`):
`current_price`, `pe_ratio`, `pb_ratio`, `eps`, `dividend_yield`, `market_cap`, `return_on_equity`, `debt_to_equity`, `revenue`, `profit_margin`, `operating_margin`, `52_week_high`, `52_week_low`, `beta`, `sector`, `industry`

**Action**: Use the lightweight `quick_quote.py` script (Step 1.8) to fetch only the needed fields, reply directly. **Do NOT run full data fetch, agents, or dashboard. STOP after Step 1.8.**

#### Mode B: `selective` — 選擇性分析
**When**: The user's question focuses on one or a few specific dimensions of analysis, not a full comprehensive review.

**Agent mapping** — match keywords to the required agent(s):

| User Intent Keywords | Required Agent(s) | Notes |
|---------------------|-------------------|-------|
| 財務、基本面、營收、獲利、估值、財報 | `financial_analyst` | May also add `industry_macro` for context |
| 技術面、K線、趨勢、支撐壓力、RSI、MACD | `technical_analyst` | |
| 風險報酬、Sharpe、回撤、波動度、量化 | `quantitative_analyst` | |
| 產業、競爭、景氣、總經、供應鏈 | `industry_macro` | |
| 新聞、市場情緒、輿論、消息面 | `news_sentiment` | |
| 法人、籌碼、三大法人、融資融券、外資 | `institutional_flow` | |
| 值不值得買、投資建議 (but scoped) | `financial_analyst` + `technical_analyst` | When user asks about buy/sell but in casual tone with specific focus |

**Smart bundling rules**:
- If only 1 agent is selected, consider adding 1 complementary agent for richer context (e.g., `financial_analyst` → also add `industry_macro`)
- Always include `data-fetcher` + `data-validator` (Step 2 is always needed)
- Maximum: if user's question maps to 4+ agents, switch to `full_analysis` mode instead

**Action**: Execute Steps 2-3, then launch ONLY the selected agents (Step 4-selective), produce a partial `integrated_report.json` with `"mode": "selective"` and `"active_analysts"` list, generate dashboard (which will only show relevant sections). Continue to Steps 5-7 but only for the active agents.

#### Mode C: `full_analysis` — 完整分析 (Original behavior)
**When**: The user asks for a comprehensive stock analysis, general investment evaluation, or the intent is broad/ambiguous.

**Examples**:
- "分析台積電" → full
- "幫我看看 AAPL" → full
- "這支股票值得投資嗎" → full
- "個股分析 2330.TW" → full

**Action**: Execute the full 7-step pipeline as originally designed.

### Step 1.5: Cache Check (Today's Report)

**Skip this step entirely if mode is `quick_answer`** — always fetch fresh data for quick questions.

For `full_analysis` and `selective` modes, run this check via Bash:
```bash
# Check if today's dashboard already exists
TODAY=$(date +%Y-%m-%d)
DASHBOARD="{{OUTPUT_DIR}}/{name}/dashboard.html"
if [ -f "$DASHBOARD" ]; then
  FILE_DATE=$(stat -f '%Sm' -t '%Y-%m-%d' "$DASHBOARD" 2>/dev/null || date -r "$DASHBOARD" +%Y-%m-%d 2>/dev/null)
  if [ "$FILE_DATE" = "$TODAY" ]; then
    echo "CACHE_HIT"
  else
    echo "CACHE_MISS_STALE"
  fi
else
  echo "CACHE_MISS_NONE"
fi
```

- If result is **`CACHE_HIT`** and mode is `full_analysis`: Tell the user "今日已有 {ticker} 分析報告，直接開啟", then run `open {{OUTPUT_DIR}}/{name}/dashboard.html` and **STOP**.
- If result is **`CACHE_HIT`** and mode is `selective`: Continue anyway (selective analysis may cover different dimensions than cached full report).
- If result is `CACHE_MISS_STALE` or `CACHE_MISS_NONE`: Continue to Step 2.

### Step 2: Fetch & Validate Data (single combined script)
Run the combined fetch-and-validate script. This saves one Python cold-start and one JSON round-trip:

```bash
python {{SKILLS_DIR}}/stock-data-fetcher/scripts/fetch_and_validate.py {TICKER} \
  --output {{OUTPUT_DIR}}/{name}/validated_data.json \
  --raw-output {{OUTPUT_DIR}}/{name}/raw_data.json
```

- Exit code 0 = success (passed or warning tier)
- Exit code 2 = **hard stop** (confidence < 30%, data too unreliable) — report to user and stop
- Exit code 1 = script error — report the error and stop

**Note**: The fetch script now uses parallel API calls internally (ThreadPoolExecutor), so data fetching is ~2-3x faster than before.

### Step 3: Read Validated Data & Tiered Quality Gate
Use the Read tool to read `validated_data.json`. **Check the `validation_tier` field first:**

| `validation_tier` | Action |
|---|---|
| `"hard_stop"` | Confidence < 30%. **Report failures to user and STOP.** Do not launch agents. |
| `"warning"` | Confidence 30-49%. **Warn user** that data quality is low, then proceed with reduced confidence expectations. |
| `"passed"` | Confidence >= 50%. Proceed normally. |

**Additional checks (for `warning` and `passed` tiers):**
1. **Review `validation_notes`** — report any warnings to the user (e.g., stale data, missing sections, anomalies).
2. **Review `anomaly_detection`** — if there are `high` severity anomalies, warn the user that analysis reliability may be reduced.
3. **Check `data_completeness.completeness_pct`** — if below 60%, warn the user about missing data sections.
4. **Check `confidence_scores`** per category — if any category scores below 50, note that the corresponding analyst's output should be weighted lower.

Then extract the key data points from `validated_data.validated_data` (the nested structure):
- Company info (name, sector, industry, market cap, PE, PB, EPS, ROE, margins, currency, current_price, etc.)
- Latest price and price history summary (now 2 years of data)
- Technical indicators (RSI, MACD, Bollinger Bands, KD)
- Financial statements summary
- Holder information
- Analyst recommendations
- **TWSE data** (for Taiwan stocks): `twse_data.institutional_trading` (三大法人買賣超) and `twse_data.margin_trading` (融資融券)
- **Note**: News is NOT in validated_data — the sentiment agent handles news collection independently via WebSearch

### Step 1.8: Quick Answer Early Exit (mode = `quick_answer` ONLY)

**If mode is `quick_answer`, SKIP Steps 2 and 3 entirely.** Instead, use the lightweight `quick_quote.py` script:

**For static fields** (price, PE, EPS, etc.):
```bash
python {{SKILLS_DIR}}/stock-data-fetcher/scripts/quick_quote.py {TICKER} --fields current_price,currency,company_name
```

**For price trend questions** (走勢、趨勢、近X月股價):
```bash
python {{SKILLS_DIR}}/stock-data-fetcher/scripts/quick_quote.py {TICKER} --history {PERIOD}
```
Where `{PERIOD}` is mapped from user's request: 近一月→`1mo`, 近兩月→`2mo`, 近三月→`3mo`, 近半年→`6mo`, 近一年→`1y`. Default: `1mo`.

Returns: `start_price`, `end_price`, `change_pct_fmt`, `trend` (上漲/下跌/盤整), `period_high/low`, `weekly_prices`.

Then reply to the user in natural language (繁體中文).

**For static field questions** — keep it concise (1-2 sentences):
- User: "台積電目前股價" → "台積電（2330.TW）目前股價為 NT$890.0。"
- User: "AAPL 殖利率多少" → "Apple（AAPL）目前殖利率為 0.55%，股價為 US$198.50。"

**For price trend questions** — use the following rich format with 3 sections:

```
## {公司名}（{TICKER}）近{期間}股價趨勢

**期間：{start_date} ~ {end_date} | 漲跌幅：{change_pct_fmt}**

### 走勢圖（ASCII）
用 weekly_prices 數據繪製簡易 ASCII 走勢圖，標注：
- Y 軸：NT$（或 US$ 等），標出關鍵價位
- 標記期間最高點（★ 期間最高 {price}（{date}））
- 標記期間最低點（★ 期間最低 {price}（{date}））
- 標記最新收盤（● 最新 {price}）
- X 軸：月份時間標記

### 走勢摘要

| 指標 | 數值 |
|------|------|
| 起始價（{date}） | NT${start_price} |
| 最新價（{date}） | NT${end_price} |
| 期間最高 | NT${period_high} |
| 期間最低 | NT${period_low} |
| 區間跌幅 | {change_pct_fmt} |

### 趨勢解讀
根據 weekly_prices 走勢，分段描述趨勢變化（2-3 段）：
1. {月份}→{月份}：{趨勢描述}（{價格範圍}），{量能/事件}
2. {月份}→{月份}：{趨勢描述}...

最後一句總結整體格局與當前位置。
```

（資料來源：Yahoo Finance，{date}）

**Rules**:
1. For static answers: 1-2 sentences only.
2. For trend answers: MUST include all 3 sections（走勢圖 + 摘要表格 + 趨勢解讀）。
3. Append: "（資料來源：Yahoo Finance，{date}）"
4. **STOP here. Do NOT proceed to Step 2 or beyond. No agents, no dashboard.**

---

### Step 3.5: Pre-launch Quant Script (parallel with Step 4)

If the quantitative analyst is among the active agents, start `analyze_quant.py` **immediately** via Bash with `run_in_background: true` — it runs in parallel with all other agents:

```bash
python {{SKILLS_DIR}}/stock-quant-analyst/scripts/analyze_quant.py \
  --input {{OUTPUT_DIR}}/{name}/validated_data.json \
  --output {{OUTPUT_DIR}}/{name}/quant_analysis.json
```

Do NOT wait for this to finish before launching agents. The Quant Agent will receive the result when it completes.

### Step 3.8: Agent-Level Cache Check

Before launching each agent, check if a **same-day** analysis already exists:

```bash
TODAY=$(date +%Y-%m-%d)
for f in financial_analysis.json technical_analysis.json quant_analysis.json \
         industry_analysis.json sentiment_analysis.json institutional_analysis.json; do
  FPATH="{{OUTPUT_DIR}}/{name}/$f"
  if [ -f "$FPATH" ]; then
    FILE_DATE=$(stat -f '%Sm' -t '%Y-%m-%d' "$FPATH" 2>/dev/null)
    [ "$FILE_DATE" = "$TODAY" ] && echo "CACHED:$f"
  fi
done
```

- For any `CACHED:{file}`, **skip launching that agent** — reuse the existing JSON.
- This is especially useful when transitioning from selective → full analysis on the same stock.

### Step 4: Launch Analyst Agents (MUST be parallel)

**If mode is `full_analysis`**: Launch all 6 agents in parallel (minus any cached from Step 3.8).
**If mode is `selective`**: Launch ONLY the agents identified in Step 1 (minus cached).

**⚠ CRITICAL — 強制並行啟動**:
You MUST launch ALL required agents in a **single response message** containing multiple Agent tool calls. This is the ONLY way to achieve true parallelism — if you send them in separate messages, they run sequentially and waste 5x the time.

Example (full_analysis, no cache): Your response should contain **6 Agent tool calls in one message**, NOT 6 separate turns.

Each agent receives:
1. The role description from its SKILL.md
2. The relevant data extracted from validated_data.json
3. Instructions to output its analysis result

**CRITICAL — Agent Output Method (防止亂碼)**:
Sub-agents running in background cannot reliably write files (permission issues). Therefore:
- **DO NOT** instruct agents to write JSON files themselves.
- Instead, instruct each agent to **return the complete JSON in its response text** (inside a ```json code block).
- After all agents complete, the **orchestrator (you) reads each agent's response**, extracts the JSON, and uses the **Write tool** to save each file (e.g., `financial_analysis.json`).
- **NEVER use bash heredoc (`cat << EOF`)** to write JSON containing Chinese text — this corrupts UTF-8 multi-byte characters. Always use the Write tool.

The 6 analysts (launch all for `full_analysis`, or only the selected ones for `selective`):
1. **Financial Analyst** — Fundamental analysis (profitability, valuation, financial structure, dividends)
2. **Technical Analyst** — Price action analysis (trend, support/resistance, momentum indicators)
3. **Quantitative Analyst** — Interpret the pre-calculated metrics from `quant_analysis.json` (launched in Step 3.5). If the script hasn't finished yet, wait for it before providing data to the Quant Agent.
4. **Industry & Macro Analyst** — Sector positioning, competitive landscape, macro environment
5. **News Sentiment Analyst** — News sentiment classification, major events, sentiment trends. **News is NOT in validated_data.** The agent must independently collect news via WebSearch → WebFetch → neutral fallback. **Must include `sources` array with URL for every article analyzed.** The agent must NEVER use training data / memory as a news source.
6. **Institutional Flow Analyst** — Ownership structure, analyst consensus, smart money signals. **For Taiwan stocks**: Include TWSE institutional trading data (三大法人買賣超) and margin trading data (融資融券) from `validated_data.twse_data`.

**IMPORTANT**: For each agent prompt, include the actual data values from validated_data.json so the agent can reason about them. Don't just tell the agent to "read the file" — provide the data inline.

**CRITICAL — Zero Hallucination Directive (傳達給每個 agent)**:
Every agent prompt MUST include the full text of `shared/zero_hallucination_policy.md` (read it once, then paste into each agent prompt). This replaces the previous per-agent duplicated blocks. Additionally, append the agent-specific confidence rule from each agent's SKILL.md.

Compact version for prompt injection (if context is tight):
> 你必須遵守 Zero Hallucination Policy：(1) 絕對禁止使用訓練資料填補缺失數據 (2) 所有缺失或不確定的資料必須列入 data_limitations 欄位 (3) summary 最後一段必須以「⚠ 資料限制」揭露不足之處 (4) 寧可留白不可捏造。data_limitations 為必填欄位。

Each agent must return its JSON analysis in its response. **Every agent output must include a `data_limitations` array field.**

### Step 4.5: Save Agent Outputs (orchestrator writes all files — MUST be parallel)

After all agents complete:
1. Extract the JSON from each agent's response text.
2. **⚠ Use the Write tool to save ALL files in a single response message** — e.g., 6 Write tool calls in one message for 6 agents. Do NOT save them one-by-one in separate turns. This cuts 6 sequential writes into 1 parallel batch.
3. **NEVER use Bash heredoc** to write these files — always use the Write tool to guarantee correct UTF-8 encoding.

### Step 5: Integration — Synthesize Analyses (LLM reasoning only)

**Architecture**: The integration is split into two parts:
1. **You (LLM)** produce a small `synthesis.json` (~3KB) containing ONLY the parts that need reasoning
2. **`assemble_report.py` (Python script)** mechanically merges your synthesis with all agent outputs into the final `integrated_report.json` (~29KB)

This is much faster because you don't need to generate/copy the 6 analysts' full summaries, sources, or metrics — the script handles that mechanically with zero errors.

#### Step 5a: Generate synthesis.json (Write tool)

You already have all agent data in memory from Step 4. Using YOUR OWN reasoning, produce `synthesis.json` with this structure:

```json
{
  "mode": "full_analysis",
  "active_analysts": ["financial_analyst", "technical_analyst", "quantitative_analyst", "industry_macro", "news_sentiment", "institutional_flow"],
  "stock_info": {
    "ticker": "2317.TW",
    "company_name": "鴻海精密工業"
  },
  "overall_score": 7.5,
  "confidence_level": "High",
  "summary": "One-paragraph executive summary in Chinese...",
  "dimension_scores": {
    "fundamental": 8.0,
    "technical": 6.5,
    "quantitative": 5.0,
    "industry": 7.0,
    "sentiment": 6.0,
    "fund_flow": 7.5
  },
  "analysts": {
    "quantitative_analyst": {
      "summary": "量化分析師的完整摘要（繁體中文）...",
      "confidence": "Medium"
    }
  },
  "narrative_report": {
    "investment_summary": "2-3 paragraph investment thesis in Chinese...",
    "fundamental_analysis": "Detailed fundamental analysis paragraph...",
    "technical_analysis": "Detailed technical analysis paragraph...",
    "risk_factors": "Key risk factors paragraph...",
    "investment_recommendation": "Clear actionable recommendation...",
    "data_limitations": "彙整所有分析師回報的資料限制（自然語言段落）"
  },
  "data_limitations": [
    "去重後的資料限制清單（條列式）"
  ]
}
```

**What goes in synthesis.json** (LLM reasoning required):
- `overall_score` — weighted average of dimension scores
- `confidence_level` — your assessment based on agent outputs
- `summary` — executive summary synthesizing all agents
- `dimension_scores` — you may adjust agent scores based on cross-analysis (e.g., if technical contradicts fundamental)
- `analysts.quantitative_analyst` — the quant script outputs metrics only (no summary). You MUST provide `{"summary": "...", "confidence": "..."}` for the quant agent in synthesis. Other agents' summaries are copied from their JSONs automatically.
- `narrative_report` — all sections, written in 繁體中文
- `data_limitations` — **curated** list: deduplicate, remove limitations covered by other agents, keep genuine gaps
- `stock_info.company_name` — translate to 繁體中文 (yfinance returns English)

**What the script handles automatically** (DO NOT include in synthesis.json):
- `analysts.*` — score, confidence, summary, sources copied from agent JSONs
- `metrics` — extracted from validated_data.json
- `analysis_date` — today's date

**Selective mode**: Set `"mode": "selective"` and only list active agents in `active_analysts`. Only include `dimension_scores` and `narrative_report` sections for active agents.

**Scoring rules** (all scores are 0-10 scale):
- 8-10: Strong Buy signal from this dimension
- 6-8: Moderately bullish
- 4-6: Neutral / mixed
- 2-4: Moderately bearish
- 0-2: Strong Sell signal

**Confidence levels**: "Very High", "High", "Medium-High", "Medium", "Medium-Low", "Low"

**All narrative_report content MUST be written in Traditional Chinese (繁體中文).**

**Data Limitations rules**:
1. Deduplicate across agents — remove limitations covered by other analysts' work
2. If 3+ agents report major data limitations, `confidence_level` must not exceed "Medium"
3. `narrative_report.data_limitations` = natural language prose; top-level `data_limitations` = array of strings

Use the **Write tool** to save `synthesis.json` to `{{OUTPUT_DIR}}/{name}/synthesis.json`.

#### Step 5b: Assemble integrated_report.json (Python script)

Run the assembly script immediately after writing synthesis.json:

```bash
python {{SKILLS_DIR}}/stock-integrator/scripts/assemble_report.py \
  --dir {{OUTPUT_DIR}}/{name} \
  --synthesis {{OUTPUT_DIR}}/{name}/synthesis.json \
  --output {{OUTPUT_DIR}}/{name}/integrated_report.json
```

The script:
- Reads all 6 agent JSONs → copies full summaries, scores, confidence, sources (no truncation, no errors)
- Reads validated_data.json → extracts pe_ratio, pb_ratio, eps, roe, dividend_yield, debt_ratio
- Merges your synthesis (scores, narrative, limitations)
- Outputs the complete `integrated_report.json`

If the script fails, fall back to the old method (Write the full integrated_report.json directly).

### Step 6: Generate Dashboard (Python script)
```bash
python {{SKILLS_DIR}}/stock-dashboard/scripts/generate_dashboard.py \
  --integrated {{OUTPUT_DIR}}/{name}/integrated_report.json \
  --validated {{OUTPUT_DIR}}/{name}/validated_data.json \
  --output {{OUTPUT_DIR}}/{name}/dashboard.html
```

The dashboard script automatically detects the `mode` and `active_analysts` fields from `integrated_report.json` and renders only the relevant sections for selective mode.

### Step 7: Open Dashboard
```bash
open {{OUTPUT_DIR}}/{name}/dashboard.html
```

Report the overall score and rating to the user.

## Output Format for integrated_report.json

The `metrics` field in integrated_report.json feeds the dashboard's Financial Metrics cards. Extract these from `validated_data.validated_data.company_info`:
- `pe_ratio`, `pb_ratio`, `eps` — directly from company_info
- `roe` — format as percentage string like "22.5%"
- `dividend_yield` — format as percentage string
- `debt_ratio` — derive from debt_to_equity if available, format as percentage

## Error Handling

- If data fetching fails: suggest the user check the ticker format
- If an analyst agent fails: continue with remaining analysts, note the gap
- If dashboard generation fails: still provide the text-based report to the user
