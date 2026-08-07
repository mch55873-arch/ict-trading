#!/usr/bin/env python3
"""
Python Unit Test Suite for Journal Analyzer Engine (v10.1 Standard)
Repository: github.com/mch55873-arch/ict-trading/tests
Runs automatically on every GitHub push via CI/CD.
"""

import sys
import unittest
sys.path.append('.')

from python.journal_analyzer import (
    parse_csv_line,
    calculate_bootstrap_ci,
    calculate_rolling_expectancy,
    calculate_consecutive_loss_distribution
)

class TestJournalAnalyzer(unittest.TestCase):

    def test_parse_csv_line(self):
        sample_line = "1, XAUUSD, M5, London KZ, Tue, LONG, Bullish, SSL Sweep, 2.45, 90%, 85%, 85%, 3.20, 0.25, 2380.50, 2374.20, 2405.00, 2399.40, 1:3.8, +3.0R, 18, +3.8R, -0.4R, CLOSED_TP2"
        parsed = parse_csv_line(sample_line)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed['trade_id'], 1)
        self.assertEqual(parsed['symbol'], 'XAUUSD')
        self.assertEqual(parsed['session'], 'London KZ')
        self.assertEqual(parsed['direction'], 'LONG')
        self.assertEqual(parsed['r_multiple'], 3.0)

    def test_calculate_bootstrap_ci(self):
        r_multiples = [3.0, -1.0, 2.0, -1.0, 4.0, -1.0]
        ci_lower, ci_upper = calculate_bootstrap_ci(r_multiples, iterations=100)
        self.assertIsInstance(ci_lower, float)
        self.assertIsInstance(ci_upper, float)
        self.assertGreaterEqual(ci_upper, ci_lower)

    def test_calculate_rolling_expectancy(self):
        r_multiples = [1.0, 2.0, 3.0, 4.0]
        rolling = calculate_rolling_expectancy(r_multiples, window=2)
        self.assertEqual(len(rolling), 4)
        self.assertEqual(rolling[-1], 3.5)

    def test_calculate_consecutive_loss_distribution(self):
        r_multiples = [1.0, -1.0, -1.0, 2.0, -1.0, -1.0, -1.0, 3.0]
        streaks = calculate_consecutive_loss_distribution(r_multiples)
        self.assertEqual(streaks.get(2), 1)
        self.assertEqual(streaks.get(3), 1)

if __name__ == '__main__':
    unittest.main()
