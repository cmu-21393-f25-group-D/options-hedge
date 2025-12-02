"""Unit tests for Market data module with mocked yfinance."""

from unittest.mock import patch

import pandas as pd
import pytest

from options_hedge.market import Market


@pytest.fixture
def mock_yf_data() -> pd.DataFrame:
    """Create mock yfinance DataFrame."""
    dates = pd.date_range("2024-01-01", periods=5, freq="D")
    return pd.DataFrame(
        {
            "Open": [100, 101, 99, 100, 102],
            "High": [102, 103, 101, 102, 104],
            "Low": [99, 100, 98, 99, 101],
            "Close": [101, 102, 100, 101, 103],
            "Volume": [1000, 1100, 900, 1000, 1200],
        },
        index=dates,
    )


def test_market_initialization_with_mock(
    mock_yf_data: pd.DataFrame,
) -> None:
    """Test Market initialization with mocked yfinance download."""
    with patch("options_hedge.market.yf.download") as mock_download:
        mock_download.return_value = mock_yf_data.copy()

        market = Market(ticker="SPY", start="2024-01-01", end="2024-01-05")

        # Verify yfinance was called with correct parameters
        mock_download.assert_called_once_with(
            "SPY", start="2024-01-01", end="2024-01-05", auto_adjust=False
        )

        # Verify Returns column was added
        assert "Returns" in market.data.columns  # type: ignore[attr-defined]
        assert len(market.data) == 5  # type: ignore[arg-type]

        # First return should be 0.0 (no previous day)
        first_return = market.data["Returns"].iloc[0]  # type: ignore[attr-defined]
        assert first_return == 0.0


def test_market_returns_calculation(
    mock_yf_data: pd.DataFrame,
) -> None:
    """Test that returns are calculated correctly."""
    with patch("options_hedge.market.yf.download") as mock_download:
        mock_download.return_value = mock_yf_data.copy()

        market = Market()

        # Calculate expected returns
        expected_return_day2 = (102 - 101) / 101
        actual = market.data["Returns"].iloc[1]  # type: ignore[attr-defined]

        assert (
            pytest.approx(actual, abs=1e-6)  # type: ignore[arg-type]
            == expected_return_day2
        )


def test_get_price(mock_yf_data: pd.DataFrame) -> None:
    """Test get_price method returns correct value."""
    with patch("options_hedge.market.yf.download") as mock_download:
        mock_download.return_value = mock_yf_data.copy()

        market = Market()
        dates = list(market.data.index)  # type: ignore[attr-defined,arg-type]

        price = market.get_price(dates[0])  # type: ignore[arg-type]
        assert price == 101.0


def test_get_returns(mock_yf_data: pd.DataFrame) -> None:
    """Test get_returns method returns Series."""
    with patch("options_hedge.market.yf.download") as mock_download:
        mock_download.return_value = mock_yf_data.copy()

        market = Market()
        returns = market.get_returns()

        assert isinstance(returns, pd.Series)
        assert len(returns) == 5
        assert returns.iloc[0] == 0.0


def test_market_with_default_parameters(
    mock_yf_data: pd.DataFrame,
) -> None:
    """Test Market uses default ticker and dates."""
    with patch("options_hedge.market.yf.download") as mock_download:
        mock_download.return_value = mock_yf_data.copy()

        _ = Market()

        # Should use defaults from constants
        mock_download.assert_called_once()
        call_kwargs = mock_download.call_args[1]  # type: ignore[index]
        assert call_kwargs["auto_adjust"] is False


def test_market_get_price_missing_date(mock_yf_data: pd.DataFrame) -> None:
    """Test that get_price raises KeyError for dates not in index."""
    with patch("options_hedge.market.yf.download") as mock_download:
        mock_download.return_value = mock_yf_data.copy()

        market = Market()
        missing_date = pd.Timestamp("2025-01-10")  # Not in 5-day range
        with pytest.raises(KeyError):
            market.get_price(missing_date)


def test_market_returns_first_day_is_zero(
    mock_yf_data: pd.DataFrame,
) -> None:
    """Test that first day's return is filled with 0.0."""
    with patch("options_hedge.market.yf.download") as mock_download:
        mock_download.return_value = mock_yf_data.copy()

        market = Market()
        returns = market.get_returns()
        # First return should be 0.0 (filled)
        assert returns.iloc[0] == 0.0


def test_market_returns_pct_change(mock_yf_data: pd.DataFrame) -> None:
    """Test daily returns calculation is correct."""
    with patch("options_hedge.market.yf.download") as mock_download:
        mock_download.return_value = mock_yf_data.copy()

        market = Market()
        # Second day: (102 - 101) / 101 ≈ 0.00990099
        assert pytest.approx(
            market.data["Returns"].iloc[1],  # type: ignore[attr-defined]
            rel=1e-4,
        ) == pytest.approx(0.00990099, rel=1e-4)
        # Third day: (100 - 102) / 102 ≈ -0.0196078
        assert pytest.approx(
            market.data["Returns"].iloc[2],  # type: ignore[attr-defined]
            rel=1e-4,
        ) == pytest.approx(-0.0196078, rel=1e-4)
