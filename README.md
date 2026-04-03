<p align="center">
  <img src="https://img.shields.io/badge/Claude_Code-Plugin-blueviolet?style=for-the-badge&logo=anthropic" alt="Claude Code Plugin" />
  <img src="https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.9+" />
  <img src="https://img.shields.io/badge/yfinance-Yahoo_Finance-red?style=for-the-badge" alt="yfinance" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License" />
</p>

<h1 align="center">個人理財助理</h1>
<h3 align="center">AI 多重代理人個股分析系統 — Claude Code Plugin</h3>

<p align="center">
  <b>6 位 AI 分析師同時為你解讀一支股票，生成專業級互動式投資儀表板</b><br/>
  <i>6 AI analysts working in parallel to deliver professional-grade investment dashboards</i>
</p>

---

## Demo

> **指令**：`分析鴻海`

系統自動解析意圖 → 抓取 Yahoo Finance 資料 → 6 位 AI 分析師並行分析 → 整合報告 → 生成互動式 Dashboard

<!-- 請在此處放入 dashboard 截圖 -->
<!-- ![Dashboard Demo](docs/images/dashboard-demo.png) -->

---

## What is This?

**個人理財助理** 是一個以 **Claude Code Skills** 架構打造的多重代理人（Multi-Agent）個股分析系統。它不是傳統的 if/else 規則引擎——每位分析師都是一個獨立的 Claude LLM Agent，用真正的語義理解來解讀財報、技術指標、新聞情緒和法人動向。

### Key Highlights

| Feature                    | Description                                                    |
| -------------------------- | -------------------------------------------------------------- |
| **6 AI Analyst Agents**    | 財務、技術、量化、產業總經、新聞情緒、法人籌碼，各司其職       |
| **Parallel Execution**     | 6 位分析師同時運行，大幅縮短分析時間                           |
| **Professional Dashboard** | 互動式 HTML 儀表板，含雷達圖、K線圖、分析師觀點                |
| **Multi-Market Support**   | 台股（2330.TW）、美股（AAPL）、日股（4704.T）、港股（0700.HK） |
| **Traditional Chinese**    | 所有分析報告以繁體中文撰寫，專業投資級別用語                   |
| **Zero API Keys**          | 使用 yfinance 免費資料，無需任何 API Key                       |
| **Self-Contained Output**  | 單一 HTML 檔案即是完整報告，可離線瀏覽                         |

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   User: "分析台積電"                    │
└──────────────────────┬──────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────┐
│              🎯 Orchestrator (指揮官)                  │
│         解析意圖 → 調度流程 → 整合報告                    │
└──────────────────────┬──────────────────────────────┘
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
   ┌─────────┐  ┌──────────┐  ┌──────────┐
   │  Data   │  │  Data    │  │  Read &  │
   │ Fetcher │→ │Validator │→ │ Extract  │
   │ (Python)│  │ (Python) │  │  Data    │
   └─────────┘  └──────────┘  └────┬─────┘
                                   │
        ┌──────────┬──────────┬────┴────┬──────────┬──────────┐
        ▼          ▼          ▼         ▼          ▼          ▼
   ┌─────────┐┌─────────┐┌────────┐┌────────┐┌─────────┐┌─────────┐
   │ 💰 財務 ││ 📈 技術 ││ 🔢 量化 ││ 🏭 產業 ││ 📰 情緒 ││ 🏦 法人 │
   │ 分析師  ││ 分析師  ││ 分析師  ││ 分析師  ││ 分析師  ││ 分析師  │
   │(Claude) ││(Claude) ││(Claude) ││(Claude) ││(Claude) ││(Claude) │
   └────┬────┘└────┬────┘└────┬───┘└───┬────┘└────┬────┘└────┬────┘
        │          │          │        │          │          │
        └──────────┴──────────┴────┬───┴──────────┴──────────┘
                                   ▼
                    ┌──────────────────────────┐
                    │  🧠 Integration (Claude)  │
                    │  加權整合 → 綜合評分         │
                    └─────────────┬────────────┘
                                  ▼
                    ┌──────────────────────────┐
                    │  📊 Dashboard (Python)    │
                    │  互動式 HTML 儀表板         │
                    └──────────────────────────┘
```

### Hybrid Design Philosophy

| Layer                | Technology        | Why                                               |
| -------------------- | ----------------- | ------------------------------------------------- |
| **Data Fetching**    | Python + yfinance | 結構化 API 呼叫、數值計算、技術指標運算           |
| **Data Validation**  | Python            | 規則式品質檢查、異常偵測、信心度評分              |
| **6 Analyst Agents** | Claude LLM        | 語義理解、跨維度推理、專業判斷，遠超 if/else 規則 |
| **Integration**      | Claude LLM        | 多維度綜合推理、敘事報告撰寫                      |
| **Dashboard**        | Python → HTML     | 穩定的模板化輸出、Chart.js 互動圖表               |

---

## The 6 AI Analysts

每位分析師都有獨立的 SKILL.md 定義其角色、分析框架和輸出格式：

### 💰 財務分析師 Financial Analyst

> 基本面分析：獲利能力、估值水準、財務結構、股利政策

- PE / PB / PEG / Forward PE 估值比較
- ROE、ROA、毛利率、淨利率分析
- 負債比、流動比率、速動比率健康度
- 股利殖利率、配發率永續性評估

### 📈 技術分析師 Technical Analyst

> 價量分析：趨勢判斷、支撐壓力、動能指標

- 均線系統（MA5/10/20/50/200）排列與趨勢
- RSI 超買超賣、MACD 交叉、KD 黃金/死亡交叉
- 布林通道壓縮與突破
- 關鍵支撐壓力位辨識

### 🔢 量化分析師 Quantitative Analyst

> 風險報酬分析：波動度、夏普比率、最大回撤

- 年化報酬率 vs 市場基準
- 波動率評級與最大回撤分析
- Sharpe / Sortino Ratio 風險調整後報酬
- 情境分析（樂觀 / 基本 / 悲觀）

### 🏭 產業總經分析師 Industry & Macro Analyst

> 產業定位：競爭格局、景氣循環、總經環境

- 產業地位與市佔率分析
- 競爭護城河評估
- 景氣循環階段判斷
- 利率、匯率、地緣政治影響評估

### 📰 新聞情緒分析師 News Sentiment Analyst

> 市場情緒：新聞分類、重大事件、敘事方向

- 逐篇新聞情緒分類（正面/中性/負面）
- 情緒指數（-10 到 +10）加權計算
- 重大事件偵測（財報、併購、監管）
- 市場敘事方向與轉變判斷
- **自動 WebSearch**：若 yfinance 新聞資料為空（台股/日股常見），自動搜尋補充

### 🏦 法人籌碼分析師 Institutional Flow Analyst

> 法人動向：持股結構、分析師共識、聰明錢訊號

- 機構投資人持股比例與變化
- 分析師評級分佈與目標價共識
- 內部人買賣訊號
- Smart Money 累積/出貨判斷

---

## Installation

### Prerequisites

- **Python 3.9+**
- **Claude Code CLI** (with Claude Pro / Team / Enterprise subscription)

### Step 1: Clone & Install

```bash
git clone https://github.com/YourUsername/fubon-stock-advisor.git
cd fubon-stock-advisor
chmod +x install.sh
./install.sh
```

That's it! The install script will:
1. Install Python dependencies (`yfinance`, `pandas`, `numpy`)
2. Copy all 11 Skills to `~/.claude/skills/`
3. Replace path placeholders with your machine's absolute paths
4. Create output directory at `~/fubon-stock-reports/`
5. Write config to `~/.claude/stock-analysis.conf`

### Custom Output Directory (Optional)

```bash
./install.sh --output-dir ~/Desktop/stock-reports
```

### Step 2: Verify — Open Claude Code in **ANY** Directory

```bash
cd ~
claude   # or open Claude Code in any folder
```

Type:

```
分析台積電
```

If everything is set up correctly, the system will begin the full analysis pipeline. Reports will be saved to `~/fubon-stock-reports/tsmc/`.

### Uninstall

```bash
./uninstall.sh                  # Keep reports
./uninstall.sh --remove-reports # Remove everything
```

---

## Usage

### Quick Start — Just Talk to Claude

在 Claude Code 中直接用自然語言觸發：

```
分析台積電          → 分析 TSMC (2330.TW)
分析鴻海            → 分析 Foxconn (2317.TW)
analyze AAPL       → 分析 Apple Inc.
幫我看看 NVDA      → 分析 NVIDIA
這支股票值得投資嗎   → 搭配 ticker 進行完整分析
```

### Supported Ticker Formats

| Market        | Format          | Examples                                                 |
| ------------- | --------------- | -------------------------------------------------------- |
| 🇹🇼 Taiwan TSE | `{code}.TW`     | `2330.TW` (台積電), `2317.TW` (鴻海), `2454.TW` (聯發科) |
| 🇹🇼 Taiwan OTC | `{code}.TWO`    | `6547.TWO`                                               |
| 🇺🇸 US         | Symbol directly | `AAPL`, `NVDA`, `MSFT`, `GOOGL`, `TSLA`                  |
| 🇯🇵 Japan      | `{code}.T`      | `4704.T` (趨勢科技), `6758.T` (Sony)                     |
| 🇭🇰 Hong Kong  | `{code}.HK`     | `0700.HK` (騰訊), `9988.HK` (阿里巴巴)                   |

### Manual Pipeline Execution

安裝後，所有腳本都在 `~/.claude/skills/` 下，可從任何目錄手動執行：

```bash
SKILLS=~/.claude/skills
OUT=~/fubon-stock-reports/tsmc

# 1. Fetch data
python $SKILLS/stock-data-fetcher/scripts/fetch_data.py 2330.TW --output $OUT/raw_data.json

# 2. Validate data
python $SKILLS/stock-data-validator/scripts/validate_data.py --input $OUT/raw_data.json --output $OUT/validated_data.json

# 3. Run quantitative analysis
python $SKILLS/stock-quant-analyst/scripts/analyze_quant.py --input $OUT/validated_data.json --output $OUT/quant_analysis.json

# 4. Generate dashboard (after integrated_report.json is ready)
python $SKILLS/stock-dashboard/scripts/generate_dashboard.py \
  --integrated $OUT/integrated_report.json \
  --validated $OUT/validated_data.json \
  --output $OUT/dashboard.html

# 5. Open in browser
open $OUT/dashboard.html
```

---

## Pipeline Deep Dive

完整的 7 步驟分析流程：

### Step 1: 解析使用者意圖

Orchestrator 從自然語言中提取 ticker，支援公司名稱（鴻海）到 ticker（2317.TW）的自動映射。

### Step 2: 資料抓取 & 驗證

```
fetch_data.py → raw_data.json → validate_data.py → validated_data.json
```

- yfinance 抓取 7 大類資料（公司資訊、財報、股價歷史、技術指標、新聞、持股、分析師）
- 驗證器檢查資料新鮮度（股價 <15 分鐘、財報 <90 天）、異常值、跨來源一致性

### Step 3: 資料讀取 & 摘要

Orchestrator 讀取 validated_data.json，提取各分析師所需的關鍵數據。

### Step 4: 6 位 AI 分析師並行分析

6 個 Claude Agent 同時啟動，各自接收相關數據並進行專業分析。每位分析師輸出獨立的 JSON 報告，包含：

- **Score** (0-10)：該維度評分
- **Confidence**：信心水準
- **Summary**：繁體中文分析摘要

### Step 5: 整合與綜合評估

Claude 讀取 6 份分析報告，以加權方式計算綜合評分：

| Analyst    | Weight | Rationale            |
| ---------- | ------ | -------------------- |
| 財務分析師 | 25%    | 基本面是長期投資核心 |
| 產業總經   | 20%    | 產業趨勢決定中期方向 |
| 量化分析師 | 15%    | 風險量化提供客觀基準 |
| 技術分析師 | 15%    | 進出場時機參考       |
| 法人籌碼   | 15%    | 聰明錢方向指引       |
| 新聞情緒   | 10%    | 短期情緒波動參考     |

### Step 6: 生成 Dashboard

Python 腳本將 `integrated_report.json` 轉化為專業互動式 HTML 儀表板。

### Step 7: 自動開啟瀏覽器

Dashboard 完成後自動在瀏覽器中開啟。

---

## Output Structure

每次分析會在 `~/fubon-stock-reports/{stock_name}/` 下產生以下檔案：

```
~/fubon-stock-reports/foxconn/
├── raw_data.json              # Yahoo Finance 原始資料
├── validated_data.json        # 驗證後資料（含品質評分）
├── financial_analysis.json    # 💰 財務分析結果
├── technical_analysis.json    # 📈 技術分析結果
├── quant_analysis.json        # 🔢 量化分析結果
├── industry_analysis.json     # 🏭 產業總經分析結果
├── sentiment_analysis.json    # 📰 新聞情緒分析結果
├── institutional_analysis.json # 🏦 法人籌碼分析結果
├── integrated_report.json     # 🧠 綜合整合報告
└── dashboard.html             # 📊 互動式儀表板
```

### Scoring System

| Score Range | Rating      | Meaning            |
| ----------- | ----------- | ------------------ |
| 8.0 - 10.0  | Strong Buy  | 該維度強烈看多     |
| 6.0 - 7.9   | Buy         | 偏多，正面訊號居多 |
| 4.0 - 5.9   | Hold        | 中性，多空交錯     |
| 2.0 - 3.9   | Sell        | 偏空，負面訊號居多 |
| 0.0 - 1.9   | Strong Sell | 該維度強烈看空     |

---

## Dashboard Features

生成的 HTML Dashboard 包含：

- **Score Overview** — 綜合評分與信心水準
- **六維雷達圖** — 一眼看清六大維度強弱
- **股價走勢圖** — K 線 + 均線 + 成交量 + 支撐壓力線
- **財務指標卡片** — PE、PB、EPS、ROE、殖利率、負債比
- **分析師觀點** — 6 位分析師可展開的詳細分析（中英文名稱 + 專屬頭像）
- **共識與分歧** — 多空觀點對照
- **完整敘事報告** — 投資摘要、基本面、技術面、風險因素、投資建議
- **風險免責聲明**

Dashboard 為自包含的單一 HTML 檔案，使用 CDN 載入 Tailwind CSS 和 Chart.js，可離線瀏覽（圖表資料內嵌）。

---

## Project Structure

```
naya-stock-analyzer/
│
├── stock-orchestrator/           # 🎯 指揮官 — 整體流程控制
│   ├── SKILL.md                  #    Skill 定義（觸發條件、7 步驟流程）
│   └── scripts/
│       └── run_pipeline.py       #    Python fallback pipeline
│
├── stock-data-fetcher/           # 📥 資料抓取 — Yahoo Finance
│   ├── SKILL.md
│   └── scripts/
│       └── fetch_data.py         #    yfinance 資料收集（7 大類）
│
├── stock-data-validator/         # ✅ 資料驗證 — 品質把關
│   ├── SKILL.md
│   └── scripts/
│       └── validate_data.py      #    新鮮度、異常值、信心度檢查
│
├── stock-financial-analyst/      # 💰 財務分析師
│   ├── SKILL.md                  #    分析框架 & 輸出格式定義
│   └── scripts/
│       └── analyze_financial.py  #    資料前處理輔助
│
├── stock-technical-analyst/      # 📈 技術分析師
│   ├── SKILL.md
│   └── scripts/
│       └── analyze_technical.py
│
├── stock-quant-analyst/          # 🔢 量化分析師
│   ├── SKILL.md
│   └── scripts/
│       └── analyze_quant.py      #    統計指標計算（Sharpe, Sortino, etc.）
│
├── stock-industry-macro/         # 🏭 產業總經分析師
│   ├── SKILL.md
│   └── scripts/
│       └── analyze_industry.py
│
├── stock-news-sentiment/         # 📰 新聞情緒分析師
│   ├── SKILL.md                  #    含 WebSearch 自動補充規則
│   └── scripts/
│       └── analyze_sentiment.py
│
├── stock-institutional-flow/     # 🏦 法人籌碼分析師
│   ├── SKILL.md
│   └── scripts/
│       └── analyze_institutional.py
│
├── stock-integrator/             # 🧠 整合引擎
│   ├── SKILL.md
│   └── scripts/
│       └── integrate_analyses.py #    加權整合 & 評分
│
├── stock-dashboard/              # 📊 Dashboard 生成器
│   ├── SKILL.md
│   └── scripts/
│       └── generate_dashboard.py #    HTML/CSS/JS 報告產生
│
├── install.sh                    # 🔧 一鍵安裝腳本
├── uninstall.sh                  # 🗑  解除安裝腳本
├── requirements.txt              # 📦 Python 依賴
├── .gitignore
└── README.md                     # 📖 本文件

# 安裝後，報告輸出至：
# ~/fubon-stock-reports/{stock_name}/
```

---

## Configuration

### Analyst Weights

整合引擎的權重可在 `stock-orchestrator/SKILL.md` Step 5 中調整：

```
Financial:     25%  (基本面權重最高)
Industry:      20%  (產業趨勢次之)
Quantitative:  15%
Technical:     15%
Institutional: 15%
Sentiment:     10%  (短期情緒權重最低)
```

### Validation Thresholds

`stock-data-validator/scripts/validate_data.py` 中可調整：

| Parameter           | Default | Description        |
| ------------------- | ------- | ------------------ |
| Price Freshness     | 15 min  | 股價資料新鮮度上限 |
| Financial Freshness | 90 days | 財報資料新鮮度上限 |
| PE Ratio Range      | 0 - 500 | 合理 PE 區間       |
| Max Daily Change    | 20%     | 單日漲跌幅異常門檻 |
| EPS Growth Cap      | 300%    | EPS 季增長異常門檻 |

---

## Limitations & Known Issues

| Issue             | Description                               | Workaround                                       |
| ----------------- | ----------------------------------------- | ------------------------------------------------ |
| 台股/日股新聞為空 | yfinance 對台股、日股的新聞標題常回傳空白 | 情緒分析師自動使用 WebSearch 補充                |
| 即時報價延遲      | yfinance 免費資料有 15-20 分鐘延遲        | 適用於中長期分析，非即時交易                     |
| 台股財報格式      | 部分台股財報欄位與美股不同                | 驗證器會標記缺失欄位                             |
| 需要網路連線      | 資料抓取和 Dashboard CDN 資源需要網路     | 已生成的 dashboard.html 圖表資料內嵌，可部分離線 |

---

## Tech Stack

| Component       | Technology                             |
| --------------- | -------------------------------------- |
| LLM Engine      | Claude (Opus / Sonnet) via Claude Code |
| Skill Framework | Claude Code Skills (SKILL.md)          |
| Data Source     | Yahoo Finance (yfinance)               |
| Data Processing | Python, pandas, numpy                  |
| Dashboard       | HTML5, Tailwind CSS, Chart.js          |
| Output Format   | JSON + Self-contained HTML             |

---

## Contributing

歡迎貢獻！以下是一些可以改進的方向：

1. **新增分析師**：建立新的 `stock-{name}/SKILL.md` 定義角色，並在 Orchestrator 中加入
2. **新增市場**：擴展 ticker 格式支援（韓國、歐洲等）
3. **資料來源**：整合台灣本地財經媒體（工商時報、MoneyDJ）提升情緒分析品質
4. **Dashboard 主題**：新增亮色/暗色主題切換
5. **歷史比較**：支援同一股票不同時間點的分析比較

### Adding a New Analyst Agent

```bash
mkdir stock-new-analyst
mkdir stock-new-analyst/scripts
```

建立 `stock-new-analyst/SKILL.md`：

```yaml
---
name: stock-new-analyst
description: 你的新分析師描述
---
# Your Analyst Name

## Analysis Framework
...
## Output Format
{
  "agent": "new_analyst",
  "ticker": "...",
  "score": 5.0,
  "confidence": "Medium",
  "summary": "...",
}
```

然後在 `stock-orchestrator/SKILL.md` Step 4 中加入第 7 位分析師。

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Disclaimer

本系統產生的所有分析報告**僅供參考，不構成任何投資建議**。投資決策請諮詢專業財務顧問。股票投資有風險，過去績效不代表未來表現。

_All analysis reports generated by this system are for reference only and do not constitute investment advice. Please consult a professional financial advisor for investment decisions._

---

<p align="center">
  Built with Claude Code by <a href="https://www.linkedin.com/in/yen-hsun-li-093949354/">Yen-Hsun Li</a>
</p>
