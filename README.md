# risk-sentinel

A risk agent for a paper book. It checks three rules and prints the breaches:

- no position above 25% of equity
- no open loss worse than 8% versus your average price
- cash at least 10% of equity

**[See the live demo](https://aziz4rehman-hue.github.io/risk-sentinel/)**

**Not financial advice. It does not sell, hedge, or send an order.**

```bash
git clone https://github.com/aziz4rehman-hue/risk-sentinel.git
cd risk-sentinel
python -m risksentinel --demo
```

```
risk sentinel — paper rules, not financial advice
WARN concentration NVDA is 90.9% of equity (limit 25%)
WARN drawdown NVDA last 80.00 is 20.0% under average 100.00 (limit 8%)
WARN cash cash is 9.1% of equity (minimum 10%)
equity 880.00 cash 80.00
```

## Your book

```json
{
  "cash": 5000,
  "holdings": [
    {"symbol": "AAPL", "qty": 10, "avg_price": 190, "last_price": 180}
  ]
}
```

```bash
python -m risksentinel --json book.json
python -m risksentinel --json book.json --max-weight 0.40 --max-loss 0.15 --min-cash 0.05
```

A book that breaks nothing comes back as `INFO clear no rule breached`. Zero equity is `CRITICAL`.

From Python:

```python
from risksentinel.agent import Holding, RiskAgent, Snapshot

snap = Snapshot(cash=80, holdings=[Holding("NVDA", 10, 100, 80)])
print(RiskAgent().report(snap))
```

## Tests

```bash
python -m unittest discover -s tests -v
```

Python 3.10+. No third-party packages.

## License

MIT. Built by [Aziz Rehman](https://github.com/aziz4rehman-hue).
