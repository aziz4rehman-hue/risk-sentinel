import unittest

from risksentinel.agent import Holding, RiskAgent, Snapshot, load_snapshot
from risksentinel.cli import main


class SentinelTests(unittest.TestCase):
    def test_flags_concentration_drawdown_and_cash(self):
        snap = Snapshot(cash=80, holdings=[Holding("NVDA", 10, 100, 80)])
        codes = [alert.code for alert in RiskAgent().review(snap)]
        self.assertEqual(codes, ["concentration", "drawdown", "cash"])

    def test_clean_book_is_clear(self):
        snap = Snapshot(cash=9_000, holdings=[Holding("AAPL", 1, 100, 100)])
        alerts = RiskAgent().review(snap)
        self.assertEqual(alerts[0].level, "info")
        self.assertIn("no rule breached", alerts[0].message)

    def test_zero_equity_is_critical(self):
        alerts = RiskAgent().review(Snapshot(cash=0, holdings=[]))
        self.assertEqual(alerts[0].level, "critical")

    def test_limit_can_silence_concentration(self):
        snap = Snapshot(cash=80, holdings=[Holding("NVDA", 10, 100, 100)])
        codes = [alert.code for alert in RiskAgent(max_weight=0.99, min_cash=0.0).review(snap)]
        self.assertEqual(codes, ["clear"])

    def test_json_and_demo_cli(self):
        snap = load_snapshot('{"cash": 80, "holdings": [{"symbol": "nvda", "qty": 10, "avg_price": 100, "last_price": 80}]}')
        self.assertEqual(snap.holdings[0].symbol, "NVDA")
        with self.assertRaises(ValueError):
            load_snapshot("{")
        self.assertEqual(main(["--demo"]), 0)


if __name__ == "__main__":
    unittest.main()
