from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, TypedDict

from .options_instruments import Option


class HistoryRow(TypedDict):
    Date: datetime
    Value: float


@dataclass
class Portfolio:
    initial_value: float = 1_000_000.0
    beta: float = 1.0
    equity_value: float = field(init=False)
    cash: float = field(default=0.0)
    options: List[Option] = field(default_factory=list)
    history: List[HistoryRow] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.equity_value = self.initial_value

    def buy_put(
        self,
        strike: float,
        premium: float,
        expiry: datetime,
        quantity: int = 1,
    ) -> None:
        opt = Option(strike, premium, expiry, quantity)
        self.options.append(opt)
        self.cash -= opt.total_cost()

    def update_equity(self, daily_return: float) -> None:
        self.equity_value *= 1 + daily_return * self.beta

    def total_value(
        self,
        current_price: float,
        current_date: datetime,
    ) -> float:
        option_value = sum(o.value(current_price, current_date) for o in self.options)
        return self.equity_value + self.cash + option_value

    def record(self, date: datetime, total_value: float) -> None:
        self.history.append({"Date": date, "Value": total_value})
