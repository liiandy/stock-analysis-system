#!/usr/bin/env python3
"""
Stock Data Validator Script
Validates raw stock data against quality thresholds and assigns confidence scores.
"""

import json
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import sys


class StockDataValidator:
    """Validates stock data and assigns confidence scores."""

    # Validation thresholds
    PRICE_FRESHNESS_MINUTES = 15
    FINANCIAL_FRESHNESS_DAYS = 90
    NEWS_FRESHNESS_DAYS = 30
    PE_MAX = 500
    SINGLE_DAY_CHANGE_LIMIT = 0.20  # 20%
    EPS_GROWTH_LIMIT = 3.0  # 300%
    CROSS_SOURCE_TOLERANCE = 0.02  # 2%
    MIN_CONFIDENCE_PASS = 50

    def __init__(self):
        self.anomalies = []
        self.validation_notes = []
        self.excluded_fields = []

    def validate_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main validation pipeline.

        Args:
            raw_data: Raw data dictionary from data fetcher

        Returns:
            Validated data package with confidence scores
        """
        self.anomalies = []
        self.validation_notes = []
        self.excluded_fields = []

        ticker = raw_data.get('ticker', 'UNKNOWN')

        # Step 1: Freshness check
        freshness_results = self._check_freshness(raw_data)

        # Step 2: Cross-source comparison
        cross_source_results = self._cross_source_comparison(raw_data)

        # Step 3: Anomaly detection
        self._detect_anomalies(raw_data)

        # Step 4: Calculate confidence scores
        data_confidence = self._calculate_data_confidence(
            freshness_results,
            cross_source_results
        )
        overall_confidence = self._calculate_overall_confidence(data_confidence)

        # Step 5: Build validated package
        validated_package = {
            'ticker': ticker,
            'validation_timestamp': datetime.now().isoformat(),
            'data_freshness': freshness_results,
            'cross_source_check': cross_source_results,
            'anomaly_detection': self.anomalies,
            'confidence_scores': data_confidence,
            'overall_confidence': overall_confidence,
            'validated_data': self._build_validated_data(raw_data, data_confidence),
            'excluded_fields': self.excluded_fields,
            'validation_notes': self.validation_notes,
            'passed_validation': overall_confidence >= self.MIN_CONFIDENCE_PASS
        }

        return validated_package

    def _check_freshness(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check freshness of different data categories."""
        now = datetime.now()
        freshness = {}

        # Price data freshness
        if 'price_timestamp' in data:
            price_time = datetime.fromisoformat(data['price_timestamp'])
            age_minutes = (now - price_time).total_seconds() / 60
            freshness['price'] = {
                'timestamp': data['price_timestamp'],
                'age_minutes': round(age_minutes, 2),
                'fresh': age_minutes < self.PRICE_FRESHNESS_MINUTES,
                'max_age_minutes': self.PRICE_FRESHNESS_MINUTES
            }
            if age_minutes >= self.PRICE_FRESHNESS_MINUTES:
                self.validation_notes.append(
                    f"Price data is {age_minutes:.1f} minutes old (threshold: {self.PRICE_FRESHNESS_MINUTES}min)"
                )

        # Financial data freshness
        if 'financial_timestamp' in data:
            fin_time = datetime.fromisoformat(data['financial_timestamp'])
            age_days = (now - fin_time).days
            freshness['financial'] = {
                'timestamp': data['financial_timestamp'],
                'age_days': age_days,
                'fresh': age_days < self.FINANCIAL_FRESHNESS_DAYS,
                'max_age_days': self.FINANCIAL_FRESHNESS_DAYS
            }
            if age_days >= self.FINANCIAL_FRESHNESS_DAYS:
                self.validation_notes.append(
                    f"Financial data is {age_days} days old (threshold: {self.FINANCIAL_FRESHNESS_DAYS}d)"
                )

        # News data freshness
        if 'news' in data and isinstance(data['news'], list) and len(data['news']) > 0:
            oldest_news_time = None
            for news_item in data['news']:
                if 'timestamp' in news_item:
                    try:
                        news_time = datetime.fromisoformat(news_item['timestamp'])
                        if oldest_news_time is None or news_time < oldest_news_time:
                            oldest_news_time = news_time
                    except ValueError:
                        pass

            if oldest_news_time:
                age_days = (now - oldest_news_time).days
                freshness['news'] = {
                    'oldest_timestamp': oldest_news_time.isoformat(),
                    'age_days': age_days,
                    'fresh': age_days < self.NEWS_FRESHNESS_DAYS,
                    'max_age_days': self.NEWS_FRESHNESS_DAYS
                }
                if age_days >= self.NEWS_FRESHNESS_DAYS:
                    self.validation_notes.append(
                        f"Oldest news item is {age_days} days old (threshold: {self.NEWS_FRESHNESS_DAYS}d)"
                    )

        return freshness

    def _cross_source_comparison(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Compare data across multiple sources."""
        results = {'sources': {}, 'aligned': True, 'alignment_issues': []}

        if 'sources' not in data:
            return results

        sources = data['sources']
        if not isinstance(sources, dict):
            return results

        # Compare price across sources
        prices = {}
        for source, source_data in sources.items():
            if isinstance(source_data, dict) and 'price' in source_data:
                prices[source] = source_data['price']

        if len(prices) >= 2:
            price_list = list(prices.values())
            max_price = max(price_list)
            min_price = min(price_list)
            tolerance = max_price * self.CROSS_SOURCE_TOLERANCE

            if (max_price - min_price) > tolerance:
                results['aligned'] = False
                results['alignment_issues'].append({
                    'metric': 'price',
                    'sources': prices,
                    'max_diff_pct': round(((max_price - min_price) / min_price * 100), 2),
                    'tolerance_pct': round(self.CROSS_SOURCE_TOLERANCE * 100, 2)
                })
                self.validation_notes.append(
                    f"Price discrepancy between sources: {round(((max_price - min_price) / min_price * 100), 2)}% "
                    f"(tolerance: {round(self.CROSS_SOURCE_TOLERANCE * 100, 2)}%)"
                )

        results['sources'] = prices
        return results

    def _detect_anomalies(self, data: Dict[str, Any]):
        """Detect anomalies in the data."""

        # PE ratio check
        if 'pe_ratio' in data and data['pe_ratio'] is not None:
            pe = float(data['pe_ratio'])
            if pe < 0 or pe > self.PE_MAX:
                self.anomalies.append({
                    'type': 'pe_ratio_anomaly',
                    'value': pe,
                    'acceptable_range': f"0 to {self.PE_MAX}",
                    'severity': 'high'
                })

        # EPS growth check
        if 'eps_current' in data and 'eps_previous' in data:
            eps_curr = data['eps_current']
            eps_prev = data['eps_previous']
            if eps_prev and eps_prev != 0:
                try:
                    growth = abs((eps_curr - eps_prev) / eps_prev)
                    if growth > self.EPS_GROWTH_LIMIT:
                        self.anomalies.append({
                            'type': 'eps_growth_anomaly',
                            'growth_rate': round(growth, 2),
                            'threshold': self.EPS_GROWTH_LIMIT,
                            'current_eps': eps_curr,
                            'previous_eps': eps_prev,
                            'severity': 'medium'
                        })
                except (TypeError, ValueError):
                    pass

        # Single-day price change check
        if 'price' in data and 'price_previous' in data:
            price = data['price']
            price_prev = data['price_previous']
            if price_prev and price_prev > 0:
                try:
                    change = abs((price - price_prev) / price_prev)
                    if change > self.SINGLE_DAY_CHANGE_LIMIT:
                        self.anomalies.append({
                            'type': 'price_spike',
                            'change_pct': round(change * 100, 2),
                            'threshold_pct': round(self.SINGLE_DAY_CHANGE_LIMIT * 100, 2),
                            'current_price': price,
                            'previous_price': price_prev,
                            'severity': 'medium'
                        })
                except (TypeError, ValueError):
                    pass

        # Currency consistency check
        if 'currency' in data:
            currency = data['currency']
            for key in ['price', 'market_cap', 'volume_value']:
                if key in data and data[key] is not None:
                    # Just note that we have the currency
                    pass

        # Volume anomaly check
        if 'volume' in data and 'volume_average' in data:
            vol = data['volume']
            vol_avg = data['volume_average']
            if vol_avg and vol_avg > 0:
                try:
                    vol_ratio = vol / vol_avg
                    if vol_ratio > 5.0:  # 500% of average
                        self.anomalies.append({
                            'type': 'volume_anomaly',
                            'volume_ratio': round(vol_ratio, 2),
                            'threshold': 5.0,
                            'current_volume': vol,
                            'average_volume': vol_avg,
                            'severity': 'low'
                        })
                except (TypeError, ValueError):
                    pass

    def _calculate_data_confidence(self, freshness: Dict, cross_source: Dict) -> Dict[str, int]:
        """Calculate confidence scores for each data category."""
        confidence = {}

        # Price confidence
        price_conf = 85  # Base
        if 'price' in freshness:
            if freshness['price']['fresh']:
                price_conf = 95
            else:
                price_conf -= 20

        # Check cross-source alignment
        if not cross_source.get('aligned', True):
            price_conf -= 15

        # Check for price anomalies
        for anomaly in self.anomalies:
            if anomaly['type'] == 'price_spike':
                price_conf -= 25

        confidence['price'] = max(0, min(100, price_conf))

        # Financial confidence
        fin_conf = 80  # Base
        if 'financial' in freshness:
            if freshness['financial']['fresh']:
                fin_conf = 90
            else:
                fin_conf -= 30

        for anomaly in self.anomalies:
            if anomaly['type'] in ['pe_ratio_anomaly', 'eps_growth_anomaly']:
                fin_conf -= 20

        confidence['financial'] = max(0, min(100, fin_conf))

        # News confidence
        news_conf = 70  # Base
        if 'news' in freshness:
            if freshness['news']['fresh']:
                news_conf = 85
            else:
                news_conf -= 15

        confidence['news'] = max(0, min(100, news_conf))

        # Volume confidence
        vol_conf = 75  # Base
        for anomaly in self.anomalies:
            if anomaly['type'] == 'volume_anomaly':
                vol_conf -= 10

        confidence['volume'] = max(0, min(100, vol_conf))

        return confidence

    def _calculate_overall_confidence(self, data_confidence: Dict[str, int]) -> int:
        """Calculate overall confidence score."""
        if not data_confidence:
            return 50

        # Weight the categories
        weights = {
            'price': 0.4,
            'financial': 0.35,
            'news': 0.15,
            'volume': 0.1
        }

        overall = 0
        for category, weight in weights.items():
            if category in data_confidence:
                overall += data_confidence[category] * weight

        # Penalty for anomalies
        if self.anomalies:
            high_severity = sum(1 for a in self.anomalies if a.get('severity') == 'high')
            overall -= high_severity * 15

        return max(0, min(100, int(overall)))

    def _build_validated_data(self, raw_data: Dict, confidence: Dict) -> Dict[str, Any]:
        """Build the validated data subset, excluding low-confidence fields."""
        validated = {}

        for key, value in raw_data.items():
            if key in ['ticker', 'price_timestamp', 'financial_timestamp', 'price', 'pe_ratio',
                      'eps_current', 'eps_previous', 'volume', 'volume_average', 'currency']:
                # Check if this field passes confidence threshold
                field_category = self._get_field_category(key)
                field_confidence = confidence.get(field_category, 100)

                if field_confidence >= self.MIN_CONFIDENCE_PASS:
                    validated[key] = value
                else:
                    self.excluded_fields.append({
                        'field': key,
                        'confidence': field_confidence,
                        'threshold': self.MIN_CONFIDENCE_PASS
                    })
            else:
                # Include non-scored fields
                validated[key] = value

        return validated

    def _get_field_category(self, field: str) -> str:
        """Determine which category a field belongs to."""
        if field in ['price', 'price_timestamp', 'price_previous']:
            return 'price'
        elif field in ['pe_ratio', 'eps_current', 'eps_previous', 'financial_timestamp']:
            return 'financial'
        elif field == 'volume' or field == 'volume_average':
            return 'volume'
        else:
            return 'news'


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Validate stock data and assign confidence scores'
    )
    parser.add_argument(
        '--input',
        required=True,
        help='Input raw data JSON file'
    )
    parser.add_argument(
        '--output',
        required=True,
        help='Output validated data JSON file'
    )

    args = parser.parse_args()

    # Read raw data
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error reading input file: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate
    validator = StockDataValidator()
    validated_package = validator.validate_data(raw_data)

    # Write output
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(validated_package, f, indent=2, ensure_ascii=False)
        print(f"Validation complete. Output written to {args.output}")
    except IOError as e:
        print(f"Error writing output file: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
