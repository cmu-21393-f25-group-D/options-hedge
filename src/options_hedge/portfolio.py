from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, List, TypedDict

import pandas as pd

from .option import Option

# Default portfolio parameters
DEFAULT_INITIAL_VALUE = 1_000_000.0
"""Default starting portfolio value ($1M typical for retirement portfolio)."""

DEFAULT_BETA = 1.0
"""Default portfolio beta (1.0 = matches index volatility)."""

DEFAULT_CASH = 0.0
"""Default starting cash position (fully invested initially)."""

DEFAULT_OPTION_QUANTITY = 1
"""Default number of option contracts per purchase."""

# Transaction cost parameters
DEFAULT_OPTION_BID_ASK_SPREAD = 0.05
"""Default bid-ask spread for options as fraction of premium.

5% typical for liquid SPX options at mid-market.
"""

DEFAULT_EQUITY_TRANSACTION_COST = 0.0005
"""Default equity transaction cost as fraction of notional.

5 bps for institutional trading, conservative estimate.
"""

DEFAULT_MARGIN_RATE = 0.055
"""Default annual margin borrowing rate.

5.5% typical for retail margin in 2024-2025.
"""


class HistoryRow(TypedDict):
    Date: datetime
    Value: float


@dataclass
class Portfolio:
    """Portfolio state tracker with equity, cash, and options positions.

    Tracks portfolio value over time including equity exposure (with beta),
    cash position, and options holdings. Designed for backtesting hedging
    strategies on historical market data.

    Parameters
    ----------
    initial_value : float, optional
        Starting portfolio value (default: $1M)
    beta : float, optional
        Portfolio beta to index (default: 1.0)
    cash : float, optional
        Starting cash position (default: 0)
    option_bid_ask_spread : float, optional
        Bid-ask spread as fraction of premium (default: 0.05 = 5%)
    equity_transaction_cost : float, optional
        Equity transaction cost as fraction of notional
        (default: 0.0005 = 5 bps)
    margin_rate : float, optional
        Annual margin borrowing rate (default: 0.055 = 5.5%)

    Attributes
    ----------
    initial_value : float
        Starting portfolio value
    beta : float
        Portfolio beta
    equity_value : float
        Current equity value (initialized to initial_value)
    cash : float
        Current cash position (can be negative with margin)
    options : List[Option]
        List of option positions
    history : List[HistoryRow]
        Historical record of portfolio values
    option_bid_ask_spread : float
        Bid-ask spread for options
    equity_transaction_cost : float
        Transaction cost for equity trades
    margin_rate : float
        Annual margin rate
    total_transaction_costs : float
        Cumulative transaction costs incurred
    """

    initial_value: float = DEFAULT_INITIAL_VALUE
    beta: float = DEFAULT_BETA
    equity_value: float = field(init=False)
    cash: float = field(default=DEFAULT_CASH)
    options: List[Option] = field(default_factory=list)
    history: List[HistoryRow] = field(default_factory=list)
    option_bid_ask_spread: float = DEFAULT_OPTION_BID_ASK_SPREAD
    equity_transaction_cost: float = DEFAULT_EQUITY_TRANSACTION_COST
    margin_rate: float = DEFAULT_MARGIN_RATE
    total_transaction_costs: float = field(default=0.0, init=False)

    def __post_init__(self) -> None:
        self.equity_value = self.initial_value

    def buy_put(
        self,
        strike: float,
        premium: float,
        expiry: datetime,
        quantity: int = DEFAULT_OPTION_QUANTITY,
        allow_margin: bool = True,
    ) -> None:
        """Buy a put option and deduct cost from cash.

        Parameters
        ----------
        strike : float
            Strike price of the put option
        premium : float
            Premium cost per contract (mid price)
        expiry : datetime
            Expiration date
        quantity : int, optional
            Number of contracts (default: 1)
        allow_margin : bool, optional
            If False, raises ValueError when cash insufficient (default: True)

        Raises
        ------
        ValueError
            If allow_margin=False and insufficient cash available

        Notes
        -----
        Applies bid-ask spread to premium cost. Actual cost is:
        premium * (1 + option_bid_ask_spread) * quantity
        """
        opt = Option(strike, premium, expiry, quantity)
        base_cost = opt.total_cost()
        # Apply bid-ask spread (we pay the ask when buying)
        transaction_cost = base_cost * self.option_bid_ask_spread
        total_cost = base_cost + transaction_cost

        if not allow_margin and self.cash < total_cost:
            raise ValueError(
                f"Insufficient funds: need ${total_cost:,.2f}, have ${self.cash:,.2f}"
            )

        self.options.append(opt)
        self.cash -= total_cost
        self.total_transaction_costs += transaction_cost

    def update_equity(self, daily_return: float) -> None:
        """Update equity value based on daily return and beta.

        Parameters
        ----------
        daily_return : float
            Daily index return (e.g., 0.01 for 1%)
        """
        self.equity_value *= 1.0 + daily_return * self.beta

    def total_value(
        self,
        current_price: float,
        current_date: pd.Timestamp,
    ) -> float:
        """Compute total portfolio value.

        Parameters
        ----------
        current_price : float
            Current underlying price for option valuation
        current_date : pd.Timestamp
            Current date for option expiry checks

        Returns
        -------
        float
            Total portfolio value = equity + cash + options
        """
        option_value = sum(o.value(current_price, current_date) for o in self.options)
        return self.equity_value + self.cash + option_value

    def exercise_expired_options(
        self, current_price: float, current_date: pd.Timestamp
    ) -> None:
        """Auto-exercise expired in-the-money options and remove all expired.

        Called daily to realize option payoffs at expiry. In-the-money puts
        are exercised, converting intrinsic value to cash. All expired
        options are then removed from the portfolio.

        Parameters
        ----------
        current_price : float
            Current underlying price for payoff calculation
        current_date : pd.Timestamp
            Current date for expiry checks
        """
        expired: List[Option] = []
        for opt in self.options:
            expiry_ts = pd.Timestamp(opt.expiry)
            if current_date >= expiry_ts:
                # Realize payoff for ITM options (put: strike > current_price)
                payoff = opt.payoff(current_price)
                if payoff > 0:
                    self.cash += payoff
                expired.append(opt)

        # Remove all expired options
        self.options = [o for o in self.options if o not in expired]

    def check_early_exercise(
        self,
        current_price: float,  # noqa: ARG002
        current_date: pd.Timestamp,  # noqa: ARG002
        exercise_rule: Callable[..., bool],  # noqa: ARG002
        **kwargs: Any,  # noqa: ARG002
    ) -> int:
        """Early exercise disabled (European-style behavior).

        This project adopts European-style options for simplicity and clarity.
        Early exercise is not permitted; payoffs are realized only at expiry
        via `exercise_expired_options`.

        Parameters are accepted for API compatibility but ignored.

        Returns
        -------
        int
            Always 0; no options are exercised early.
        """
        return 0

    def record(self, date: datetime, total_value: float) -> None:
        """Record portfolio value at a given date.

        Parameters
        ----------
        date : datetime
            Date of the record
        total_value : float
            Portfolio value at this date
        """
        self.history.append({"Date": date, "Value": total_value})
