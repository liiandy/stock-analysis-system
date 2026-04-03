#!/usr/bin/env python3
"""
Stock Analysis Master Orchestrator
Runs the complete multi-agent stock analysis pipeline end-to-end.

Orchestrates data fetching, validation, parallel analysis by 6 agents,
integration of results, and dashboard generation.

Usage:
    python run_pipeline.py 2330.TW --output-dir /path/to/output [--mode full|quick]
    python run_pipeline.py AAPL --output-dir ./analysis --mode full --verbose
"""

import json
import argparse
import sys
import subprocess
import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple


# Configure logging
def setup_logging(verbose: bool = False) -> logging.Logger:
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)


logger = setup_logging()


class StockAnalysisPipeline:
    """Orchestrates the complete stock analysis pipeline."""

    def __init__(self, ticker: str, output_dir: str, mode: str = 'full', verbose: bool = False):
        """
        Initialize the pipeline.

        Args:
            ticker: Stock ticker symbol (e.g., "2330.TW", "AAPL")
            output_dir: Directory for output files
            mode: 'full' (all 6 analysts) or 'quick' (financial + technical only)
            verbose: Enable verbose logging
        """
        self.ticker = ticker
        self.output_dir = Path(output_dir)
        self.mode = mode
        self.verbose = verbose
        self.logger = setup_logging(verbose)

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # File paths
        self.raw_data_file = self.output_dir / 'raw_data.json'
        self.validated_data_file = self.output_dir / 'validated_data.json'
        self.financial_analysis_file = self.output_dir / 'financial_analysis.json'
        self.technical_analysis_file = self.output_dir / 'technical_analysis.json'
        self.quant_analysis_file = self.output_dir / 'quant_analysis.json'
        self.industry_analysis_file = self.output_dir / 'industry_analysis.json'
        self.sentiment_analysis_file = self.output_dir / 'sentiment_analysis.json'
        self.institutional_analysis_file = self.output_dir / 'institutional_analysis.json'
        self.integrated_report_file = self.output_dir / 'integrated_report.json'
        self.dashboard_file = self.output_dir / 'dashboard.html'
        self.pipeline_log_file = self.output_dir / 'pipeline_execution.log'

        # Track execution state
        self.execution_log = []
        self.failed_steps = []
        self.completed_steps = []

        # Resolve script locations
        self._resolve_script_paths()

    def _resolve_script_paths(self):
        """Resolve paths to all required scripts."""
        # Get the directory containing this script
        script_dir = Path(__file__).parent

        # Base directory is stock-analysis-system
        base_dir = script_dir.parent.parent

        # Resolve paths to all scripts in sibling skill directories
        self.fetch_script = base_dir / 'stock-data-fetcher' / 'scripts' / 'fetch_data.py'
        self.validate_script = base_dir / 'stock-data-validator' / 'scripts' / 'validate_data.py'
        self.financial_script = base_dir / 'stock-financial-analyst' / 'scripts' / 'analyze_financial.py'
        self.technical_script = base_dir / 'stock-technical-analyst' / 'scripts' / 'analyze_technical.py'
        self.quant_script = base_dir / 'stock-quant-analyst' / 'scripts' / 'analyze_quant.py'
        self.industry_script = base_dir / 'stock-industry-macro' / 'scripts' / 'analyze_industry.py'
        self.sentiment_script = base_dir / 'stock-news-sentiment' / 'scripts' / 'analyze_sentiment.py'
        self.institutional_script = base_dir / 'stock-institutional-flow' / 'scripts' / 'analyze_institutional.py'
        self.integrator_script = base_dir / 'stock-integrator' / 'scripts' / 'integrate_analyses.py'
        self.dashboard_script = base_dir / 'stock-dashboard' / 'scripts' / 'generate_dashboard.py'

        # Verify critical scripts exist
        critical_scripts = [
            ('fetch_data', self.fetch_script),
            ('validate_data', self.validate_script),
            ('integrator', self.integrator_script)
        ]

        for name, path in critical_scripts:
            if not path.exists():
                self.logger.warning(f"Script not found: {name} at {path}")

    def _log_step(self, step_name: str, status: str, details: str = ''):
        """Log a pipeline step."""
        timestamp = datetime.now().isoformat()
        log_entry = {
            'timestamp': timestamp,
            'step': step_name,
            'status': status,
            'details': details
        }
        self.execution_log.append(log_entry)

        if status == 'started':
            self.logger.info(f"[{step_name}] Starting...")
        elif status == 'completed':
            self.logger.info(f"[{step_name}] Completed ✓")
            self.completed_steps.append(step_name)
        elif status == 'failed':
            self.logger.error(f"[{step_name}] Failed: {details}")
            self.failed_steps.append((step_name, details))

    def _run_subprocess(self, script_path: Path, args: List[str]) -> Tuple[bool, str]:
        """
        Run a subprocess and return success status and output.

        Args:
            script_path: Path to Python script
            args: Command-line arguments

        Returns:
            (success: bool, output: str)
        """
        try:
            cmd = ['python3', str(script_path)] + args
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            if result.returncode == 0:
                return True, result.stdout
            else:
                error_msg = result.stderr or result.stdout
                return False, error_msg

        except subprocess.TimeoutExpired:
            return False, "Process timeout (exceeded 300 seconds)"
        except Exception as e:
            return False, str(e)

    def run(self) -> bool:
        """
        Run the complete pipeline.

        Returns:
            True if pipeline completed (even with some failures), False if critical failure
        """
        self.logger.info(f"Starting stock analysis pipeline for {self.ticker}")
        self.logger.info(f"Mode: {self.mode}")
        self.logger.info(f"Output directory: {self.output_dir}")

        # Step 1: Fetch data
        if not self._fetch_data():
            self._log_step('fetch_data', 'failed', 'Cannot proceed without data')
            return False

        # Step 2: Validate data
        if not self._validate_data():
            self._log_step('validate_data', 'failed', 'Cannot proceed without validated data')
            return False

        # Step 3: Run analysts
        if self.mode == 'full':
            self._run_all_analysts()
        else:  # quick mode
            self._run_quick_analysts()

        # Step 4: Integrate analyses
        if not self._integrate_analyses():
            self.logger.warning("Integration failed, but generating partial report")

        # Step 5: Generate dashboard
        if self.integrated_report_file.exists():
            self._generate_dashboard()
        else:
            self.logger.warning("Skipping dashboard: no integrated report")

        # Step 6: Generate execution report
        self._generate_execution_report()

        # Summary
        self._print_execution_summary()

        return len(self.failed_steps) == 0

    def _fetch_data(self) -> bool:
        """
        Fetch raw stock data.

        Returns:
            True if successful
        """
        self._log_step('fetch_data', 'started')

        if not self.fetch_script.exists():
            self._log_step('fetch_data', 'failed', f'Script not found: {self.fetch_script}')
            return False

        success, output = self._run_subprocess(
            self.fetch_script,
            [self.ticker, '--output', str(self.raw_data_file)]
        )

        if success:
            self._log_step('fetch_data', 'completed', f'Data saved to {self.raw_data_file}')
            return True
        else:
            self._log_step('fetch_data', 'failed', output[:200])
            return False

    def _validate_data(self) -> bool:
        """
        Validate raw stock data.

        Returns:
            True if successful
        """
        self._log_step('validate_data', 'started')

        if not self.validate_script.exists():
            self._log_step('validate_data', 'failed', f'Script not found: {self.validate_script}')
            return False

        success, output = self._run_subprocess(
            self.validate_script,
            ['--input', str(self.raw_data_file), '--output', str(self.validated_data_file)]
        )

        if success:
            self._log_step('validate_data', 'completed', f'Validated data saved to {self.validated_data_file}')
            return True
        else:
            self._log_step('validate_data', 'failed', output[:200])
            return False

    def _run_all_analysts(self):
        """Run all 6 analyst agents in sequence."""
        self.logger.info("Running full analysis with all 6 analysts...")

        analysts = [
            ('financial_analysis', self.financial_script, self.financial_analysis_file),
            ('technical_analysis', self.technical_script, self.technical_analysis_file),
            ('quant_analysis', self.quant_script, self.quant_analysis_file),
            ('industry_analysis', self.industry_script, self.industry_analysis_file),
            ('sentiment_analysis', self.sentiment_script, self.sentiment_analysis_file),
            ('institutional_analysis', self.institutional_script, self.institutional_analysis_file),
        ]

        for analyst_name, script_path, output_file in analysts:
            self._run_analyst(analyst_name, script_path, output_file)

    def _run_quick_analysts(self):
        """Run quick analysis with Financial and Technical analysts only."""
        self.logger.info("Running quick analysis with Financial + Technical analysts...")

        analysts = [
            ('financial_analysis', self.financial_script, self.financial_analysis_file),
            ('technical_analysis', self.technical_script, self.technical_analysis_file),
        ]

        for analyst_name, script_path, output_file in analysts:
            self._run_analyst(analyst_name, script_path, output_file)

        # Create placeholder files for skipped analysts
        self._create_placeholder_analysis('quant_analysis', self.quant_analysis_file)
        self._create_placeholder_analysis('industry_analysis', self.industry_analysis_file)
        self._create_placeholder_analysis('sentiment_analysis', self.sentiment_analysis_file)
        self._create_placeholder_analysis('institutional_analysis', self.institutional_analysis_file)

    def _run_analyst(self, analyst_name: str, script_path: Path, output_file: Path) -> bool:
        """
        Run a single analyst agent.

        Args:
            analyst_name: Name of analyst for logging
            script_path: Path to analyst script
            output_file: Path for output file

        Returns:
            True if successful
        """
        self._log_step(analyst_name, 'started')

        if not script_path.exists():
            self._log_step(analyst_name, 'failed', f'Script not found: {script_path}')
            return False

        success, output = self._run_subprocess(
            script_path,
            ['--input', str(self.validated_data_file), '--output', str(output_file)]
        )

        if success:
            self._log_step(analyst_name, 'completed', f'Analysis saved to {output_file}')
            return True
        else:
            self._log_step(analyst_name, 'failed', output[:200])
            return False

    def _create_placeholder_analysis(self, analyst_type: str, output_file: Path):
        """Create a placeholder analysis for skipped analysts."""
        placeholder = {
            'agent': analyst_type,
            'ticker': self.ticker,
            'analysis_date': datetime.now().isoformat(),
            'summary': f'Analysis skipped (quick mode)',
            'confidence_score': 0,
            'bullish_points': [],
            'bearish_points': [],
            'note': 'This analyst was not run in quick mode'
        }

        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(placeholder, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.warning(f"Could not create placeholder for {analyst_type}: {e}")

    def _integrate_analyses(self) -> bool:
        """
        Integrate all analyst outputs.

        Returns:
            True if successful
        """
        self._log_step('integrate_analyses', 'started')

        if not self.integrator_script.exists():
            self._log_step('integrate_analyses', 'failed', f'Script not found: {self.integrator_script}')
            return False

        # Check that analysis files exist
        analysis_files = [
            self.financial_analysis_file,
            self.technical_analysis_file,
            self.quant_analysis_file,
            self.industry_analysis_file,
            self.sentiment_analysis_file,
            self.institutional_analysis_file,
        ]

        missing_files = [f for f in analysis_files if not f.exists()]
        if missing_files:
            self._log_step('integrate_analyses', 'failed', f'Missing analysis files: {missing_files}')
            return False

        success, output = self._run_subprocess(
            self.integrator_script,
            [
                '--financial', str(self.financial_analysis_file),
                '--technical', str(self.technical_analysis_file),
                '--quant', str(self.quant_analysis_file),
                '--industry', str(self.industry_analysis_file),
                '--sentiment', str(self.sentiment_analysis_file),
                '--institutional', str(self.institutional_analysis_file),
                '--output', str(self.integrated_report_file)
            ]
        )

        if success:
            self._log_step('integrate_analyses', 'completed', f'Integrated report saved to {self.integrated_report_file}')
            return True
        else:
            self._log_step('integrate_analyses', 'failed', output[:200])
            return False

    def _generate_dashboard(self) -> bool:
        """Generate interactive HTML dashboard."""
        self._log_step('generate_dashboard', 'started')

        if not self.dashboard_script.exists():
            self._log_step('generate_dashboard', 'failed', f'Script not found: {self.dashboard_script}')
            return False

        success, output = self._run_subprocess(
            self.dashboard_script,
            [
                '--integrated', str(self.integrated_report_file),
                '--validated', str(self.validated_data_file),
                '--output', str(self.dashboard_file)
            ]
        )

        if success:
            self._log_step('generate_dashboard', 'completed', f'Dashboard saved to {self.dashboard_file}')
            return True
        else:
            self._log_step('generate_dashboard', 'failed', output[:200])
            return False

    def _generate_execution_report(self):
        """Generate a report of pipeline execution."""
        report = {
            'pipeline_execution': {
                'start_time': self.execution_log[0]['timestamp'] if self.execution_log else datetime.now().isoformat(),
                'end_time': datetime.now().isoformat(),
                'ticker': self.ticker,
                'mode': self.mode,
                'output_directory': str(self.output_dir),
                'completed_steps': self.completed_steps,
                'failed_steps': [(step, reason) for step, reason in self.failed_steps],
                'total_steps': len(self.completed_steps) + len(self.failed_steps),
                'success_rate': f"{len(self.completed_steps) / max(1, len(self.completed_steps) + len(self.failed_steps)) * 100:.1f}%"
            },
            'execution_log': self.execution_log,
            'output_files': {
                'raw_data': str(self.raw_data_file) if self.raw_data_file.exists() else None,
                'validated_data': str(self.validated_data_file) if self.validated_data_file.exists() else None,
                'financial_analysis': str(self.financial_analysis_file) if self.financial_analysis_file.exists() else None,
                'technical_analysis': str(self.technical_analysis_file) if self.technical_analysis_file.exists() else None,
                'quant_analysis': str(self.quant_analysis_file) if self.quant_analysis_file.exists() else None,
                'industry_analysis': str(self.industry_analysis_file) if self.industry_analysis_file.exists() else None,
                'sentiment_analysis': str(self.sentiment_analysis_file) if self.sentiment_analysis_file.exists() else None,
                'institutional_analysis': str(self.institutional_analysis_file) if self.institutional_analysis_file.exists() else None,
                'integrated_report': str(self.integrated_report_file) if self.integrated_report_file.exists() else None,
                'dashboard': str(self.dashboard_file) if self.dashboard_file.exists() else None,
            }
        }

        # Save execution report
        try:
            with open(self.pipeline_log_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Execution report saved to {self.pipeline_log_file}")
        except Exception as e:
            self.logger.error(f"Error writing execution report: {e}")

    def _print_execution_summary(self):
        """Print a summary of pipeline execution."""
        self.logger.info("\n" + "="*60)
        self.logger.info("PIPELINE EXECUTION SUMMARY")
        self.logger.info("="*60)

        self.logger.info(f"Ticker: {self.ticker}")
        self.logger.info(f"Mode: {self.mode}")
        self.logger.info(f"Completed Steps: {len(self.completed_steps)}")

        for step in self.completed_steps:
            self.logger.info(f"  ✓ {step}")

        if self.failed_steps:
            self.logger.info(f"Failed Steps: {len(self.failed_steps)}")
            for step, reason in self.failed_steps:
                self.logger.warning(f"  ✗ {step}: {reason[:80]}")

        if self.integrated_report_file.exists():
            self.logger.info(f"\nFinal Report: {self.integrated_report_file}")
            try:
                with open(self.integrated_report_file, 'r', encoding='utf-8') as f:
                    report = json.load(f)
                    rating = report.get('rating', 'Unknown')
                    score = report.get('overall_score', 0)
                    self.logger.info(f"Investment Rating: {rating} (Score: {score}/100)")
            except Exception as e:
                self.logger.warning(f"Could not read integrated report: {e}")

        self.logger.info("="*60)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Run complete stock analysis pipeline'
    )
    parser.add_argument(
        'ticker',
        help='Stock ticker symbol (e.g., 2330.TW, AAPL)'
    )
    parser.add_argument(
        '--output-dir',
        required=True,
        help='Output directory for analysis results'
    )
    parser.add_argument(
        '--mode',
        choices=['full', 'quick'],
        default='full',
        help='Analysis mode: full (all 6 analysts) or quick (financial + technical only)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    # Create and run pipeline
    pipeline = StockAnalysisPipeline(
        args.ticker,
        args.output_dir,
        args.mode,
        args.verbose
    )

    success = pipeline.run()

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
