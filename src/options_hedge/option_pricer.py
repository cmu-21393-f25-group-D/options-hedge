"""Unified option pricing interface supporting WRDS data and synthetic pricing.

This module provides the OptionPricer class which can use either:
1. Real historical option data from WRDS (when available)
2. Synthetic VIX-based Black-Scholes pricing (fallback)
"""

from __future__ import annotations

from datetime import timedelta
from typing import Optional

import pandas as pd

from .strategies import estimate_put_premium

# Matching tolerances for WRDS data
DEFAULT_STRIKE_TOLERANCE = 0.05  # 5% tolerance for strike matching
DEFAULT_EXPIRY_TOLERANCE_DAYS = 7  # 1 week tolerance for expiry matching


class OptionPricer:
    """Unified interface for option pricing (WRDS or synthetic).

    Provides a consistent API for retrieving put option premiums,
    with automatic fallback from WRDS data to synthetic pricing.

    Parameters
    ----------
    use_wrds : bool, optional
        Whether to use WRDS data (default: False)
    wrds_data : pd.DataFrame, optional
        Pre-loaded WRDS data. If None and use_wrds=True, will attempt
        to load from encrypted file
    strike_tolerance : float, optional
        Maximum relative difference for strike matching (default: 0.05 = 5%)
    expiry_tolerance_days : int, optional
        Maximum days difference for expiry matching (default: 7)

    Attributes
    ----------
    use_wrds : bool
        Whether WRDS data is being used
    wrds_data : pd.DataFrame or None
        Loaded WRDS option data
    strike_tolerance : float
        Strike matching tolerance
    expiry_tolerance_days : int
        Expiry matching tolerance

    Methods
    -------
    get_put_premium(strike, spot, date, expiry, vix)
        Get put premium (WRDS if available, else synthetic)

    Examples
    --------
    >>> # Synthetic pricing (default)
    >>> pricer = OptionPricer()
    >>> premium = pricer.get_put_premium(
    ...     strike=3500, spot=4000,
    ...     date=pd.Timestamp('2020-03-01'),
    ...     expiry=pd.Timestamp('2020-06-01'),
    ...     vix=30.0
    ... )

    >>> # WRDS pricing
    >>> from options_hedge.wrds_data import load_encrypted_wrds_data
    >>> wrds_data = load_encrypted_wrds_data()
    >>> pricer = OptionPricer(use_wrds=True, wrds_data=wrds_data)
    >>> premium = pricer.get_put_premium(
    ...     strike=3500, spot=4000,
    ...     date=pd.Timestamp('2020-03-01'),
    ...     expiry=pd.Timestamp('2020-06-01'),
    ...     vix=30.0
    ... )
    """

    def __init__(
        self,
        use_wrds: bool = False,
        wrds_data: Optional[pd.DataFrame] = None,
        strike_tolerance: float = DEFAULT_STRIKE_TOLERANCE,
        expiry_tolerance_days: int = DEFAULT_EXPIRY_TOLERANCE_DAYS,
    ) -> None:
        """Initialize option pricer."""
        self.use_wrds = use_wrds
        self.strike_tolerance = strike_tolerance
        self.expiry_tolerance_days = expiry_tolerance_days
        self.wrds_data: Optional[pd.DataFrame]

        if use_wrds:
            if wrds_data is None:
                # Try to load from encrypted file
                try:
                    from .wrds_data import load_encrypted_wrds_data

                    self.wrds_data = load_encrypted_wrds_data()
                except (ImportError, FileNotFoundError, ValueError) as e:
                    print(
                        f"⚠️  Failed to load WRDS data: {e}\n"
                        "   Falling back to synthetic pricing"
                    )
                    self.use_wrds = False
                    self.wrds_data = None
            else:
                self.wrds_data = wrds_data
        else:
            self.wrds_data = None

    def get_put_premium(
        self,
        strike: float,
        spot: float,
        date: pd.Timestamp,
        expiry: pd.Timestamp,
        vix: float = 20.0,
    ) -> float:
        """Get put option premium as percentage of spot price.

        Parameters
        ----------
        strike : float
            Strike price in dollars
        spot : float
            Current spot price in dollars
        date : pd.Timestamp
            Current date (option purchase date)
        expiry : pd.Timestamp
            Option expiration date
        vix : float, optional
            VIX level for synthetic pricing fallback (default: 20.0)

        Returns
        -------
        float
            Premium as fraction of spot price (e.g., 0.02 = 2% of notional)

        Notes
        -----
        - If WRDS data available: Uses real market prices (bid/ask midpoint)
        - If no match found: Falls back to synthetic pricing
        - Always returns synthetic pricing if use_wrds=False
        """
        if self.use_wrds and self.wrds_data is not None:
            premium = self._match_wrds_option(strike, spot, date, expiry)
            if premium is not None:
                return premium

        # Fallback to synthetic pricing
        days = (expiry - date).days
        return estimate_put_premium(strike, spot, days, vix)

    def _match_wrds_option(
        self,
        strike: float,
        spot: float,
        date: pd.Timestamp,
        expiry: pd.Timestamp,
    ) -> Optional[float]:
        """Match closest available option in WRDS data.

        Parameters
        ----------
        strike : float
            Desired strike price
        spot : float
            Current spot price
        date : pd.Timestamp
            Current date
        expiry : pd.Timestamp
            Desired expiration date

        Returns
        -------
        float or None
            Premium as % of spot if match found, None otherwise
        """
        if self.wrds_data is None:
            return None

        # Filter by date (exact match required)
        date_filtered = self.wrds_data[self.wrds_data["date"] == date]

        if date_filtered.empty:
            return None

        # Filter by expiry (within tolerance)
        expiry_min = expiry - timedelta(days=self.expiry_tolerance_days)
        expiry_max = expiry + timedelta(days=self.expiry_tolerance_days)
        expiry_filtered = date_filtered[
            (date_filtered["exdate"] >= expiry_min)
            & (date_filtered["exdate"] <= expiry_max)
        ]

        if expiry_filtered.empty:
            return None

        # Find closest strike (within tolerance)
        strike_min = strike * (1 - self.strike_tolerance)
        strike_max = strike * (1 + self.strike_tolerance)
        strike_filtered = expiry_filtered[
            (expiry_filtered["strike_price"] >= strike_min)
            & (expiry_filtered["strike_price"] <= strike_max)
        ]

        if strike_filtered.empty:
            return None

        # Find best match (closest strike)
        strike_filtered = strike_filtered.copy()
        strike_filtered["strike_diff"] = abs(strike_filtered["strike_price"] - strike)
        best_match = strike_filtered.nsmallest(1, "strike_diff")

        # Calculate mid-price (average of bid/ask)
        bid = best_match["best_bid"].iloc[0]
        offer = best_match["best_offer"].iloc[0]
        mid_price = (bid + offer) / 2.0

        # Convert to premium as % of spot (for consistency with synthetic)
        premium_pct = mid_price / spot

        return float(premium_pct)

    def get_available_strikes(
        self,
        date: pd.Timestamp,
        spot: float,
        expiry: pd.Timestamp,
        cp_flag: str = "P",
    ) -> list[float]:
        """Get available strike prices from WRDS data for a given date/expiry.

        Parameters
        ----------
        date : pd.Timestamp
            Current date
        spot : float
            Current spot price (for filtering OTM strikes)
        expiry : pd.Timestamp
            Option expiration date
        cp_flag : str, optional
            'P' for puts, 'C' for calls (default: 'P')

        Returns
        -------
        list[float]
            List of available strike prices as ratios of spot
            (e.g., [0.90, 0.95, 1.00])
        """
        if not self.use_wrds or self.wrds_data is None:
            # Fallback: synthetic strikes at 5% intervals
            return [0.50, 0.60, 0.70, 0.80, 0.90, 0.95, 1.00]

        # Filter by date and option type
        date_filtered = self.wrds_data[
            (self.wrds_data["date"] == date) & (self.wrds_data["cp_flag"] == cp_flag)
        ]

        if date_filtered.empty:
            return [0.50, 0.60, 0.70, 0.80, 0.90, 0.95, 1.00]

        # Filter by expiry (within tolerance)
        expiry_min = expiry - timedelta(days=self.expiry_tolerance_days)
        expiry_max = expiry + timedelta(days=self.expiry_tolerance_days)
        expiry_filtered = date_filtered[
            (date_filtered["exdate"] >= expiry_min)
            & (date_filtered["exdate"] <= expiry_max)
        ]

        if expiry_filtered.empty:
            return [0.50, 0.60, 0.70, 0.80, 0.90, 0.95, 1.00]

        # Get unique strikes and convert to ratios
        strikes = expiry_filtered["strike_price"].unique()
        strike_ratios = sorted([float(k / spot) for k in strikes])

        # Filter for puts: only return strikes <= spot (OTM/ATM puts)
        if cp_flag == "P":
            strike_ratios = [k for k in strike_ratios if k <= 1.05]

        if len(strike_ratios) > 0:
            return strike_ratios
        else:
            return [0.50, 0.60, 0.70, 0.80, 0.90, 0.95, 1.00]

    def get_stats(self) -> dict:
        """Get statistics about option pricer configuration.

        Returns
        -------
        dict
            Dictionary with configuration and usage stats
        """
        stats = {
            "mode": "WRDS" if self.use_wrds else "Synthetic",
            "strike_tolerance": self.strike_tolerance,
            "expiry_tolerance_days": self.expiry_tolerance_days,
        }

        if self.use_wrds and self.wrds_data is not None:
            stats["wrds_rows"] = len(self.wrds_data)
            min_date = self.wrds_data["date"].min()
            max_date = self.wrds_data["date"].max()
            stats["wrds_date_range"] = f"{min_date} to {max_date}"

        return stats
