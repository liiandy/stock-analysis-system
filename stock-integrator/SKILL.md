---
name: stock-integrator
description: 整合 Agent。由 Orchestrator 內部執行，不單獨觸發。彙整 6 位分析師的輸出，產出符合 dashboard 格式的 integrated_report.json。
---

# Integration Agent

This agent's logic is embedded in the orchestrator's Step 5. It synthesizes all 6 analyst outputs into `integrated_report.json` matching the dashboard's expected format.

See the orchestrator SKILL.md Step 5 for the exact output schema.
