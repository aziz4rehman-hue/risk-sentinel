"""Check concentration, open loss, and cash. Rules are explicit and local."""

from __future__ import annotations

import json
from dataclasses import dataclass, field


@dataclass
class Holding:
    symbol: str
    qty: float
    avg_price: float
    last_price: float

    @property
    def value(self) -> float:
        return self.qty * self.last_price


@dataclass
class Snapshot:
    cash: float
    holdings: list[Holding] = field(default_factory=list)

    def equity(self) -> float:
        return self.cash + sum(item.value for item in self.holdings)


@dataclass(frozen=True)
class Alert:
    level: str
    code: str
    message: str


_RANK = {"critical": 0, "warn": 1, "info": 2}
_CODE = {"equity": 0, "concentration": 1, "drawdown": 2, "cash": 3, "clear": 4}


class RiskAgent:
    def __init__(self, max_weight: float = 0.25, max_loss: float = 0.08, min_cash: float = 0.10) -> None:
        if not 0 < max_weight <= 1:
            raise ValueError("max_weight must be between 0 and 1")
        if not 0 < max_loss < 1:
            raise ValueError("max_loss must be between 0 and 1")
        if not 0 <= min_cash < 1:
            raise ValueError("min_cash must be between 0 and 1")
        self.max_weight = max_weight
        self.max_loss = max_loss
        self.min_cash = min_cash

    def review(self, snapshot: Snapshot) -> list[Alert]:
        equity = snapshot.equity()
        if equity <= 0:
            return [Alert("critical", "equity", "equity is not positive")]
        alerts: list[Alert] = []
        if snapshot.cash / equity < self.min_cash:
            alerts.append(
                Alert(
                    "warn",
                    "cash",
                    f"cash is {snapshot.cash / equity * 100:.1f}% of equity (minimum {self.min_cash * 100:.0f}%)",
                )
            )
        for holding in snapshot.holdings:
            weight = holding.value / equity
            if weight > self.max_weight:
                alerts.append(
                    Alert(
                        "warn",
                        "concentration",
                        f"{holding.symbol} is {weight * 100:.1f}% of equity (limit {self.max_weight * 100:.0f}%)",
                    )
                )
            loss = (holding.avg_price - holding.last_price) / holding.avg_price
            if loss > self.max_loss:
                alerts.append(
                    Alert(
                        "warn",
                        "drawdown",
                        f"{holding.symbol} last {holding.last_price:.2f} is {loss * 100:.1f}% under "
                        f"average {holding.avg_price:.2f} (limit {self.max_loss * 100:.0f}%)",
                    )
                )
        if not alerts:
            alerts.append(Alert("info", "clear", "no rule breached"))
        alerts.sort(key=lambda item: (_RANK[item.level], _CODE[item.code], item.message))
        return alerts

    def report(self, snapshot: Snapshot) -> str:
        lines = ["risk sentinel — paper rules, not financial advice"]
        for alert in self.review(snapshot):
            lines.append(f"{alert.level.upper()} {alert.code} {alert.message}")
        lines.append(f"equity {snapshot.equity():.2f} cash {snapshot.cash:.2f}")
        return "\n".join(lines)


def snapshot_from_dict(data: dict) -> Snapshot:
    if not isinstance(data, dict):
        raise ValueError("snapshot must be an object")
    try:
        cash = float(data.get("cash", 0))
    except (TypeError, ValueError) as exc:
        raise ValueError("cash must be a number") from exc
    if cash < 0:
        raise ValueError("cash cannot be negative")
    holdings: list[Holding] = []
    seen: set[str] = set()
    for row in data.get("holdings", []):
        try:
            symbol = str(row["symbol"]).upper()
            qty = float(row["qty"])
            avg = float(row["avg_price"])
            last = float(row["last_price"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("each holding needs symbol, qty, avg_price, last_price") from exc
        if symbol in seen:
            raise ValueError(f"duplicate symbol {symbol}")
        seen.add(symbol)
        if qty <= 0 or avg <= 0 or last <= 0:
            raise ValueError("qty and prices must be positive")
        holdings.append(Holding(symbol, qty, avg, last))
    return Snapshot(cash, holdings)


def load_snapshot(text: str) -> Snapshot:
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError("snapshot is not valid json") from exc
    return snapshot_from_dict(data)


def demo_snapshot() -> Snapshot:
    return Snapshot(
        cash=80,
        holdings=[Holding("NVDA", 10, 100, 80)],
    )
