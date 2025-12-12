from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, cast

import pandas as pd
import yfinance as yf  # type: ignore[import-untyped]

# Default market data parameters
DEFAULT_TICKER = "^GSPC"  # S&P 500 index
"""Default ticker: S&P 500 index (most common benchmark for US equities)."""

DEFAULT_START_DATE = "2018-01-01"
"""Default start date: 7 years of history for strategy backtesting."""

DEFAULT_END_DATE = "2025-01-01"
"""Default end date: Current as of project development."""

DEFAULT_FILL_VALUE = 0.0
"""Fill value for first day's return (no previous price to compare)."""

try:
    from .wrds_data import (
        load_encrypted_sp500_data,
        load_encrypted_spx_options_data,
        load_encrypted_treasury_data,
        load_encrypted_vix_data,
    )

    WRDS_AVAILABLE = True
except ImportError:  # pragma: no cover
    WRDS_AVAILABLE = False

try:
    from .option_pricer import OptionPricer

    OPTION_PRICER_AVAILABLE = True
except ImportError:  # pragma: no cover
    OPTION_PRICER_AVAILABLE = False


@dataclass()
class Market:
    """Download and store daily OHLCV data and returns for a ticker.

    Fetches historical market data from Yahoo Finance or WRDS encrypted data
    and computes daily returns for portfolio simulation. Validates data
    download to ensure successful data retrieval.

    Parameters
    ----------
    ticker : str, optional
        Yahoo Finance ticker symbol (default: '^GSPC' for S&P 500 index)
    start : str, optional
        Start date in 'YYYY-MM-DD' format (default: '2018-01-01')
    end : str, optional
        End date in 'YYYY-MM-DD' format (default: '2025-01-01')
    use_wrds : bool, optional
        If True, use WRDS encrypted data instead of Yahoo Finance
        (default: False)
    fetch_vix : bool, optional
        If True, also download VIX data (default: False)

    Attributes
    ----------
    ticker : str
        Ticker symbol
    start : str
        Start date
    end : str
        End date
    data : pd.DataFrame
        Downloaded OHLCV data with computed 'Returns' column

    Raises
    ------
    ValueError
        If data download fails or returns empty DataFrame

    Methods
    -------
    get_price(date)
        Get closing price for a specific date
    get_returns()
        Get daily returns as a Series
    get_vix(date)
        Get VIX value for a specific date (if fetch_vix=True)
    get_risk_free_rate(date)
        Get risk-free rate for a specific date (if use_wrds=True)

    Notes
    -----
    The class automatically computes daily returns on initialization:
    Returns[t] = (Close[t] - Close[t-1]) / Close[t-1]

    First day's return is filled with 0.0 (no previous price).

    When use_wrds=True, loads encrypted S&P 500, VIX, and Treasury data
    from WRDS OptionMetrics. Requires WRDS_DATA_KEY environment variable.
    """

    ticker: str = DEFAULT_TICKER
    start: str = DEFAULT_START_DATE
    end: str = DEFAULT_END_DATE
    use_wrds: bool = False
    # If True, also download VIX (^VIX) and expose per-date values
    fetch_vix: bool = False
    data: pd.DataFrame = field(init=False)
    vix_data: Optional[pd.DataFrame] = field(init=False, default=None)
    treasury_data: Optional[pd.DataFrame] = field(init=False, default=None)
    pricer: Optional[OptionPricer] = field(init=False, default=None)
    _vix_series: Optional[pd.Series] = field(init=False, default=None)
    _treasury_series: Optional[pd.Series] = field(init=False, default=None)

    def __post_init__(self) -> None:  # pragma: no cover
        if self.use_wrds and WRDS_AVAILABLE:
            # Load WRDS encrypted data
            try:
                sp500_raw = load_encrypted_sp500_data()
                vix_raw = load_encrypted_vix_data()
                treasury_raw = load_encrypted_treasury_data()

                # Filter by date range
                start_dt = pd.to_datetime(self.start)
                end_dt = pd.to_datetime(self.end)

                sp500 = sp500_raw[
                    (sp500_raw["date"] >= start_dt) & (sp500_raw["date"] <= end_dt)
                ].copy()

                if sp500.empty:
                    raise ValueError(
                        f"No S&P 500 data in range {self.start} to {self.end}"
                    )

                # Set date as index and rename columns to match yfinance format
                sp500 = sp500.set_index("date")
                sp500 = sp500.rename(
                    columns={
                        "open": "Open",
                        "high": "High",
                        "low": "Low",
                        "close": "Close",
                        "volume": "Volume",
                    }
                )

                # Add Returns column
                sp500["Returns"] = (
                    sp500["Close"].pct_change().fillna(DEFAULT_FILL_VALUE)
                )

                self.data = sp500

                # Load VIX data
                vix = vix_raw[
                    (vix_raw["date"] >= start_dt) & (vix_raw["date"] <= end_dt)
                ].copy()
                if not vix.empty:
                    vix = vix.set_index("date")
                    self.vix_data = vix
                    # Forward-fill and align to main data index
                    aligned = self.vix_data.reindex(self.data.index).ffill()
                    self._vix_series = aligned["close"].astype(float)
                    self.fetch_vix = True  # Mark as available

                # Load Treasury data
                treasury = treasury_raw[
                    (treasury_raw["observation_date"] >= start_dt)
                    & (treasury_raw["observation_date"] <= end_dt)
                ].copy()
                if not treasury.empty:
                    treasury = treasury.set_index("observation_date")
                    self.treasury_data = treasury
                    # Forward-fill and align to main data index
                    aligned_treasury = self.treasury_data.reindex(
                        self.data.index
                    ).ffill()
                    # Convert from annual percentage to decimal
                    self._treasury_series = (aligned_treasury["DTB3"] / 100.0).astype(
                        float
                    )

            except Exception as e:
                print(f"⚠️  Failed to load WRDS data: {e}")
                print("   Falling back to Yahoo Finance...")
                self.use_wrds = False
                self._load_yfinance_data()

            # Try to load SPX options data for OptionPricer (separate try block)
            if self.use_wrds and OPTION_PRICER_AVAILABLE:
                try:
                    options_raw = load_encrypted_spx_options_data()
                    # Filter to date range
                    start_dt = pd.to_datetime(self.start)
                    end_dt = pd.to_datetime(self.end)
                    options_filtered = options_raw[
                        (options_raw["date"] >= start_dt)
                        & (options_raw["date"] <= end_dt)
                    ]
                    # Instantiate pricer with WRDS data
                    self.pricer = OptionPricer(
                        wrds_data=options_filtered, use_wrds=True
                    )
                except Exception as e:
                    print(f"⚠️  Failed to load SPX options data: {e}")
                    print("   OptionPricer will not be available")
                    self.pricer = None
                self._load_yfinance_data()
        else:
            self._load_yfinance_data()

    def _load_yfinance_data(self) -> None:  # pragma: no cover
        """Load data from Yahoo Finance (fallback or default)."""
        # Download primary market data
        downloaded_data = yf.download(  # type: ignore[no-untyped-call]
            self.ticker,
            start=self.start,
            end=self.end,
            auto_adjust=False,
        )

        if downloaded_data is None or downloaded_data.empty:
            raise ValueError(
                f"Failed to download data for {self.ticker} "
                f"from {self.start} to {self.end}"
            )

        self.data = downloaded_data
        returns = self.data["Close"].pct_change()
        # Fill first day's return with 0.0
        tmp_returns = returns.fillna(DEFAULT_FILL_VALUE)  # type: ignore[misc]
        filled_returns = cast(pd.Series, tmp_returns)
        self.data["Returns"] = filled_returns

        # Optionally download VIX index and align dates
        if self.fetch_vix:
            vix_download = yf.download(  # type: ignore[no-untyped-call]
                "^VIX",
                start=self.start,
                end=self.end,
                auto_adjust=False,
            )
            if vix_download is not None and not vix_download.empty:
                self.vix_data = vix_download
                # Forward-fill non-trading days; reindex to main data index
                aligned = self.vix_data.reindex(self.data.index).ffill()
                # Close column used as VIX value
                self._vix_series = aligned["Close"].astype(float)
            else:
                # Leave vix_data as None if download failed
                self.vix_data = None
                self._vix_series = None

    def get_price(self, date: pd.Timestamp) -> float:  # pragma: no cover
        """Get closing price for a specific date.

        Parameters
        ----------
        date : pd.Timestamp
            Date to retrieve price for

        Returns
        -------
        float
            Closing price at the given date

        Raises
        ------
        KeyError
            If date not in index (e.g., weekend, holiday, out of range)
        """
        value = self.data.loc[date, "Close"]  # type: ignore[index]
        return float(value)  # type: ignore[arg-type]

    def get_returns(self) -> pd.Series:  # pragma: no cover
        """Get daily returns as a Series.

        Returns
        -------
        pd.Series
            Daily returns indexed by date
        """
        return pd.Series(self.data["Returns"])  # explicit series

    def get_vix(self, date: pd.Timestamp) -> float:  # pragma: no cover
        """Get VIX value for a specific date.

        Falls back to nearest previous available value if exact date not
        present (e.g., holiday). Raises ValueError if VIX data was not
        fetched or no value available prior to date.

        Parameters
        ----------
        date : pd.Timestamp
            Date to retrieve VIX for.

        Returns
        -------
        float
            VIX index value.
        """
        if self._vix_series is None:
            raise ValueError("VIX data not fetched (fetch_vix=False).")
        if date in self._vix_series.index:
            val = self._vix_series.loc[date]
            # Handle both scalar and Series return from loc
            return float(val.iloc[0] if hasattr(val, "iloc") else val)
        # Use previous available date
        prior_dates = self._vix_series.index[self._vix_series.index <= date]
        if len(prior_dates) == 0:
            raise ValueError(f"No VIX data available on or before {date}.")
        val = self._vix_series.loc[prior_dates[-1]]
        return float(val.iloc[0] if hasattr(val, "iloc") else val)

    def get_risk_free_rate(self, date: pd.Timestamp) -> float:  # pragma: no cover
        """Get risk-free rate for a specific date.

        Returns 3-month Treasury rate as decimal (e.g., 0.02 = 2% annual).
        Falls back to nearest previous available value if exact date not
        present. Only available when use_wrds=True.

        Parameters
        ----------
        date : pd.Timestamp
            Date to retrieve risk-free rate for.

        Returns
        -------
        float
            Annualized risk-free rate as decimal (e.g., 0.02 = 2%).

        Raises
        ------
        ValueError
            If Treasury data not available (use_wrds=False).
        """
        if self._treasury_series is None:
            raise ValueError("Treasury data not available. Set use_wrds=True to load.")
        if date in self._treasury_series.index:
            return float(self._treasury_series.loc[date])
        # Use previous available date
        prior_dates = self._treasury_series.index[self._treasury_series.index <= date]
        if len(prior_dates) == 0:
            raise ValueError(f"No Treasury data available on or before {date}.")
        return float(self._treasury_series.loc[prior_dates[-1]])
