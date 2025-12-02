# Option instrument primitives.
#
# This module defines a minimal `Option` class focused on put options with
# intrinsic value only, sufficient for portfolio hedging simulations.

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import pandas as pd

# Default option parameters
DEFAULT_OPTION_QUANTITY = 1
"""Default number of option contracts (1 contract = 100 shares)."""

MIN_OPTION_VALUE = 0.0
"""Minimum option value; options cannot have negative intrinsic value."""


@dataclass
class Option:
    """Simple put option model with intrinsic value only.

    Models European-style put options using intrinsic value approximation,
    suitable for portfolio insurance simulations where time value is
    negligible compared to hedging cost.

    Parameters
    ----------
    strike : float
        Strike price (K) of the put option
    premium : float
        Premium cost per contract (C)
    expiry : datetime
        Expiration date of the option
    quantity : int, optional
        Number of contracts (default: 1, positive=long, negative=short)

    Attributes
    ----------
    strike : float
        Strike price
    premium : float
        Premium per contract
    expiry : datetime
        Expiration date
    quantity : int
        Number of contracts

    Methods
    -------
    payoff(current_price)
        Compute intrinsic payoff at expiration
    value(current_price, current_date)
        Compute current option value (zero after expiry)
    total_cost()
        Compute total premium cost
    """

    strike: float
    premium: float
    expiry: datetime
    quantity: int = DEFAULT_OPTION_QUANTITY

    def payoff(self, current_price: float) -> float:
        """Compute intrinsic payoff of put option.

        Parameters
        ----------
        current_price : float
            Current underlying price

        Returns
        -------
        float
            Put payoff = max(K - S, 0) * quantity
        """
        return max(self.strike - float(current_price), MIN_OPTION_VALUE) * self.quantity

    def value(
        self,
        current_price: float,
        current_date: pd.Timestamp,
    ) -> float:
        """Compute current option value.

        Returns zero after expiration, intrinsic value before.

        Parameters
        ----------
        current_price : float
            Current underlying price
        current_date : pd.Timestamp
            Current valuation date

        Returns
        -------
        float
            Option value (0 if expired, intrinsic value otherwise)
        """
        expiry_date = pd.Timestamp(self.expiry)
        if current_date >= expiry_date:
            return MIN_OPTION_VALUE
        return max(self.strike - float(current_price), MIN_OPTION_VALUE) * self.quantity

    def total_cost(self) -> float:
        """Compute total premium cost.

        Returns
        -------
        float
            Total cost = premium * quantity
        """
        return self.premium * self.quantity
