from dataclasses import dataclass
from datetime import datetime

import pandas as pd


@dataclass()
class Option:
    """Simplified European put option with intrinsic value only."""

    strike: float
    premium: float
    expiry: datetime
    quantity: int = 1

    def payoff(self, current_price: float) -> float:
        return max(self.strike - current_price, 0.0) * self.quantity

    def value(self, current_price: float, current_date: datetime) -> float:
        if pd.Timestamp(current_date) >= pd.Timestamp(self.expiry):
            return 0.0
        return max(self.strike - current_price, 0.0) * self.quantity

    def total_cost(self) -> float:
        return self.premium * self.quantity
