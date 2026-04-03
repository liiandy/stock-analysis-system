---
name: stock-integrator
description: 整合 Agent。由 Orchestrator 內部執行，不單獨觸發。彙整 6 位分析師的輸出，產出符合 dashboard 格式的 integrated_report.json。
---

# Integration Agent

This agent's logic is embedded in the orchestrator's Step 5. It synthesizes all 6 analyst outputs into `integrated_report.json` matching the dashboard's expected format.

See the orchestrator SKILL.md Step 5 for the exact output schema.

## Data Limitations Integration (CRITICAL)

When synthesizing analyst outputs, you MUST:

1. **Collect all `data_limitations`** from each of the 6 analyst JSONs.
2. **Merge into `integrated_report.data_limitations`** — a flat array of all unique limitation strings. Do NOT discard, minimize, or rephrase any limitation.
3. **Write `narrative_report.data_limitations`** — a natural-language paragraph in Traditional Chinese summarizing the key limitations that affect overall analysis reliability.
4. **Adjust `confidence_level`** downward if multiple analysts report significant limitations:
   - 1-2 agents with limitations → reduce by one level (e.g., "High" → "Medium-High")
   - 3-4 agents with limitations → confidence cannot exceed "Medium"
   - 5-6 agents with limitations → confidence cannot exceed "Low"
5. **Each analyst's summary** in the `analysts` section should retain the ⚠ 資料限制 paragraph from their original output — do NOT strip it out.

## Score Stability Audit（評分穩定性審計）

每位分析師的 JSON 輸出現在包含 `preliminary_score`、`score`、和 `score_adjustment_reason` 三個欄位。整合時你必須：

1. **記錄每位分析師的初步分數與最終分數差距**：在 `integrated_report.json` 的 `analysts` 區塊中保留 `preliminary_score` 欄位。
2. **標記大幅調整**：若任何分析師的 `|score - preliminary_score| > 1.0`，在 `score_stability_flags` 陣列中記錄該分析師名稱與調整原因。
3. **整體穩定性指標**：計算 6 位分析師的平均 `|score - preliminary_score|`，記錄為 `avg_score_drift`。若 > 0.8，降低整體 confidence 一級。

```json
{
  "score_stability": {
    "avg_score_drift": 0.4,
    "flags": [
      {"agent": "news_sentiment", "preliminary": 6.0, "final": 4.5, "reason": "初步評分未考量單篇高影響力的負面獨家報導"}
    ]
  }
}
```

## Zero Hallucination Policy

The integrator must NEVER:
- Add analysis or data points not present in any analyst's output
- Fill gaps left by analysts with its own reasoning or training data
- Upgrade confidence levels beyond what the data quality supports
- Remove or downplay data limitation warnings from individual analysts
