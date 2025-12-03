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


@dataclass()
class Market:
    """Download and store daily OHLCV data and returns for a ticker.

    Fetches historical market data from Yahoo Finance and computes daily
    returns for portfolio simulation. Validates data download to ensure
    successful data retrieval.

    Parameters
    ----------
    ticker : str, optional
        Yahoo Finance ticker symbol (default: '^GSPC' for S&P 500 index)
    start : str, optional
        Start date in 'YYYY-MM-DD' format (default: '2018-01-01')
    end : str, optional
        End date in 'YYYY-MM-DD' format (default: '2025-01-01')

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

    Notes
    -----
    The class automatically computes daily returns on initialization:
    Returns[t] = (Close[t] - Close[t-1]) / Close[t-1]

    First day's return is filled with 0.0 (no previous price).
    """

    ticker: str = DEFAULT_TICKER
    start: str = DEFAULT_START_DATE
    end: str = DEFAULT_END_DATE
    # If True, also download VIX (^VIX) and expose per-date values
    fetch_vix: bool = False
    data: pd.DataFrame = field(init=False)
    vix_data: Optional[pd.DataFrame] = field(init=False, default=None)
    _vix_series: Optional[pd.Series] = field(init=False, default=None)

    def __post_init__(self) -> None:  # pragma: no cover
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
            return float(self._vix_series.loc[date].iloc[0])
        # Use previous available date
        prior_dates = self._vix_series.index[self._vix_series.index <= date]
        if len(prior_dates) == 0:
            raise ValueError(f"No VIX data available on or before {date}.")
        return float(self._vix_series.loc[prior_dates[-1]].iloc[0])
