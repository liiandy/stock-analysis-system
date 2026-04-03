---
name: stock-dashboard
description: Dashboard 視覺化報告 Agent。將 integrated_report.json 轉化為專業的互動式 HTML 儀表板。由 Orchestrator 的最後步驟自動觸發，執行 generate_dashboard.py 腳本。當使用者說「產生報告」、「做 Dashboard」、「視覺化結果」時也可單獨觸發。
---

# Dashboard Generator

Generates a professional HTML dashboard from analysis results.

## Usage

This is typically triggered automatically by the orchestrator as the final step. It can also be triggered manually:

```bash
python {{SKILLS_DIR}}/stock-dashboard/scripts/generate_dashboard.py \
  --integrated {{OUTPUT_DIR}}/{name}/integrated_report.json \
  --validated {{OUTPUT_DIR}}/{name}/validated_data.json \
  --output {{OUTPUT_DIR}}/{name}/dashboard.html
```

Then open the HTML file in a browser:
```bash
open {{OUTPUT_DIR}}/{name}/dashboard.html
```

## Expected Input Format

The `integrated_report.json` must follow the schema defined in the orchestrator SKILL.md Step 5, with:
- `stock_info`, `overall_score` (0-10), `dimension_scores` (0-10 each)
- `analysts` dict with score/confidence/summary per analyst
- `narrative_report` with investment_summary, fundamental_analysis, **data_limitations**, etc.
- `metrics` with pe_ratio, pb_ratio, eps, roe, dividend_yield, debt_ratio
- `data_limitations` — array of strings describing data quality issues (displayed as "⚠ 資料限制" section in the report)

## Data Limitations Display

The dashboard automatically renders a **⚠ 資料限制 Data Limitations** section in the research report area if `data_limitations` is present and non-empty in the integrated report. This section:
- Appears between "Risk Factors" and "Recommendation"
- Uses amber/warning styling to draw attention
- Lists each limitation as a bullet point
- Also displays `narrative_report.data_limitations` as a summary paragraph if present

This ensures users always see what data was missing or unreliable before making investment decisions.
