from dataclasses import dataclass

import pandas as pd
import yfinance as yf  # type: ignore[import-not-found]


@dataclass()
class Market:
    """Download and store daily OHLCV data and returns for a ticker.

    Parameters
    ----------
    ticker: str
        Yahoo Finance ticker symbol (default: S&P 500 index '^GSPC').
    start: str
        Start date (YYYY-MM-DD).
    end: str
        End date (YYYY-MM-DD).
    """

    ticker: str = "^GSPC"
    start: str = "2018-01-01"
    end: str = "2025-01-01"

    def __post_init__(self) -> None:
        data = yf.download(
            self.ticker,
            start=self.start,
            end=self.end,
            auto_adjust=False,
        )
        data["Returns"] = data["Close"].pct_change().fillna(0.0)
        self.data = data

    def get_price(self, date: pd.Timestamp) -> float:
        return float(self.data.loc[date, "Close"])

    def get_returns(self) -> pd.Series:
        return self.data["Returns"]
