# TSMC Stock Analysis Dashboard

## Overview
A stunning, professional, fully self-contained HTML dashboard for Taiwan Semiconductor Manufacturing Company (TSMC - 2330.TW) stock analysis.

## Features

### Design & Technology
- **Dark Theme**: Professional gradient background (#0f172a to #1e293b)
- **Responsive Layout**: Works on desktop, tablet, and mobile
- **Smooth Animations**: Glass-morphism cards, hover effects, pulse animations
- **CDN-Based**: All resources from Tailwind CSS and Chart.js CDNs
- **Self-Contained**: Single HTML file with embedded data (no external dependencies except CDN)

### Core Sections
1. **Sticky Header** - Live price ticker (1,038 TWD), daily change (+0.78%), analysis date
2. **Navigation Bar** - Smooth scroll links to all sections
3. **Score Overview** - Comprehensive 78.4 rating with Buy recommendation
4. **Radar Chart** - 6-dimensional analysis (Financial: 82, Technical: 68, Quant: 85, Industry: 78, Sentiment: 73, Institutional: 80)
5. **Price Chart** - Interactive chart with:
   - Closing price (blue line)
   - MA20 (green dashed)
   - MA60 (orange dashed)
   - Volume bars
   - Support/Resistance levels (985/1085)
6. **Financial Metrics** - 6 key metrics in grid layout:
   - PE Ratio: 28.5x
   - Price-to-Book: 8.2x
   - EPS: 36.43 TWD (+38% YoY)
   - ROE: 28.5%
   - Dividend Yield: 1.15%
   - Debt-to-Equity: 25.3%
7. **Analyst Views** - 6 interactive accordions:
   - Financial Analyst (82/100)
   - Technical Analyst (68/100)
   - Quantitative Analyst (85/100)
   - Industry & Macro Analyst (78/100)
   - News Sentiment Analyst (73/100)
   - Institutional & Consensus Analyst (80/100)
8. **Consensus & Divergence** - Key agreement points and areas of disagreement
9. **Detailed Analysis Report** - Comprehensive Chinese narrative covering:
   - Investment Summary
   - Fundamental Analysis
   - Technical Analysis
   - Risk Assessment
   - Investment Recommendations
10. **Risk Disclaimer** - Full legal disclaimers in Chinese and English
11. **Footer** - System metadata and date

### Charts
- **Radar Chart**: 6-axis multi-dimensional scoring visualization
- **Price Chart**: Mixed chart with bars (volume) and lines (price + MAs)
  - Displays price history from 2025-04-01 to 2025-12-05
  - Calculated 20 and 60-period moving averages
  - Support/resistance lines overlaid
  - Only shows date labels every 20 periods for cleanliness

### Data Embedded
- Complete price history (170 data points from April 2025 to December 2025)
- All financial metrics and ratios
- All analyst views and scoring details
- Six-dimensional evaluation framework
- Comprehensive narrative analysis

### Interactive Elements
- Smooth scrolling navigation
- Expandable/collapsible analyst accordions
- Hover effects on all cards
- Confidence level progress bars
- Color-coded sentiment indicators

## Styling Highlights
- **Color Scheme**:
  - Primary Blue: #3b82f6 (financial, technical metrics)
  - Success Green: #22c55e (positive, bullish)
  - Warning Red: #ef4444 (negative, bearish)
  - Amber: #f59e0b (caution, neutral)
- **Glass Morphism**: Semi-transparent cards with backdrop blur
- **Gradients**: Smooth color transitions throughout
- **Typography**: Clean sans-serif with proper hierarchy

## File Details
- **Path**: `/sessions/amazing-compassionate-archimedes/mnt/07_Naya/stock-analysis-system/output/dashboard.html`
- **Size**: 75 KB
- **Lines**: 1,200+ lines of HTML, CSS, and JavaScript
- **Format**: Single self-contained HTML file

## How to Use
1. Open the HTML file in any modern web browser
2. Navigate using the sticky header navigation menu
3. Click analyst names to expand/collapse detailed views
4. Scroll through sections or use smooth-scroll navigation links
5. All charts are interactive (hover for details)

## Data Sources
- Data embedded from: integrated_report.json and validated_data.json
- Price history: 170 trading days of OHLCV data
- Analysis: Multi-dimensional scoring from 6 specialized analysts

## Browser Compatibility
- Chrome/Chromium (90+)
- Firefox (88+)
- Safari (14+)
- Edge (90+)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Features Implemented
✓ Responsive design
✓ Dark theme with gradients
✓ Professional financial dashboard layout
✓ Interactive charts (Chart.js 4.4.1)
✓ Accordion components
✓ Smooth scroll navigation
✓ Color-coded indicators
✓ Comprehensive analysis narrative
✓ Multi-language support (Chinese primary, English fallback)
✓ Risk disclaimers
✓ Self-contained (single HTML file)
✓ Fast loading with CDN resources

## Customization
To modify:
- Change colors: Update CSS color variables
- Add new analysts: Duplicate accordion sections
- Update data: Modify embedded priceData array
- Adjust styling: Edit Tailwind classes or add custom CSS

---
**Generated**: 2026-04-03
**System**: AI 智能個股分析系統 v1.0
