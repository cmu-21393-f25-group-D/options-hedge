"""Tests for unified option pricing interface."""

from __future__ import annotations

import pandas as pd
import pytest

from options_hedge.option_pricer import OptionPricer


@pytest.fixture
def sample_wrds_data():
    """Create sample WRDS data for testing."""
    return pd.DataFrame(
        {
            "date": pd.to_datetime(
                [
                    "2020-03-01",
                    "2020-03-01",
                    "2020-03-01",
                    "2020-03-02",
                ]
            ),
            "exdate": pd.to_datetime(
                [
                    "2020-06-19",
                    "2020-06-19",
                    "2020-09-18",
                    "2020-06-19",
                ]
            ),
            "strike_price": [3500.0, 3600.0, 3500.0, 3500.0],
            "cp_flag": ["P", "P", "P", "P"],
            "best_bid": [48.0, 58.0, 55.0, 50.0],
            "best_offer": [52.0, 62.0, 59.0, 54.0],
            "impl_volatility": [0.30, 0.32, 0.31, 0.29],
            "delta": [-0.40, -0.45, -0.42, -0.39],
        }
    )


class TestOptionPricerSynthetic:
    """Tests for synthetic (VIX-based) pricing mode."""

    def test_initialization_default(self):
        """Test default initialization uses synthetic pricing."""
        pricer = OptionPricer()

        assert pricer.use_wrds is False
        assert pricer.wrds_data is None
        assert pricer.strike_tolerance == 0.05
        assert pricer.expiry_tolerance_days == 7

    def test_get_put_premium_synthetic(self):
        """Test synthetic put premium calculation."""
        pricer = OptionPricer()

        premium = pricer.get_put_premium(
            strike=3500.0,
            spot=4000.0,
            date=pd.Timestamp("2020-03-01"),
            expiry=pd.Timestamp("2020-06-19"),
            vix=30.0,
        )

        assert isinstance(premium, float)
        assert premium > 0
        # Premium returned as fraction of spot (e.g., 0.02 = 2%)
        assert 0.001 < premium < 0.5  # Between 0.1% and 50%

    def test_synthetic_pricing_itm_vs_otm(self):
        """Test that ITM puts are more expensive than OTM."""
        pricer = OptionPricer()
        spot = 4000.0
        date = pd.Timestamp("2020-03-01")
        expiry = pd.Timestamp("2020-06-19")
        vix = 25.0

        # OTM (strike below spot for puts)
        otm_premium = pricer.get_put_premium(3500, spot, date, expiry, vix)

        # ATM
        atm_premium = pricer.get_put_premium(4000, spot, date, expiry, vix)

        # ITM (strike above spot for puts)
        itm_premium = pricer.get_put_premium(4500, spot, date, expiry, vix)

        assert itm_premium > atm_premium > otm_premium

    def test_synthetic_vix_impact(self):
        """Test that higher VIX increases premiums."""
        pricer = OptionPricer()
        strike = 3800.0
        spot = 4000.0
        date = pd.Timestamp("2020-03-01")
        expiry = pd.Timestamp("2020-06-19")

        low_vix = pricer.get_put_premium(strike, spot, date, expiry, vix=15.0)
        high_vix = pricer.get_put_premium(strike, spot, date, expiry, vix=40.0)

        assert high_vix > low_vix


class TestOptionPricerWRDS:
    """Tests for WRDS data pricing mode."""

    def test_initialization_with_wrds_data(self, sample_wrds_data):
        """Test initialization with WRDS data."""
        pricer = OptionPricer(use_wrds=True, wrds_data=sample_wrds_data)

        assert pricer.use_wrds is True
        assert pricer.wrds_data is not None
        assert len(pricer.wrds_data) == 4

    def test_initialization_wrds_auto_load_failure(self, monkeypatch):
        """Test graceful fallback when auto-loading WRDS data fails."""

        # Mock the import to raise an error
        def mock_load():
            raise FileNotFoundError("No encrypted data found")

        monkeypatch.setattr(
            "options_hedge.option_pricer.load_encrypted_wrds_data",
            mock_load,
            raising=False,
        )

        # Should fallback to synthetic without crashing
        pricer = OptionPricer(use_wrds=True)

        assert pricer.use_wrds is False
        assert pricer.wrds_data is None

    def test_wrds_exact_match(self, sample_wrds_data):
        """Test exact match in WRDS data."""
        pricer = OptionPricer(use_wrds=True, wrds_data=sample_wrds_data)

        premium = pricer.get_put_premium(
            strike=3500.0,
            spot=4000.0,
            date=pd.Timestamp("2020-03-01"),
            expiry=pd.Timestamp("2020-06-19"),
            vix=30.0,
        )

        # Should match midpoint: (48+52)/2 = 50, as fraction: 50/4000 = 0.0125
        assert premium == 0.0125

    def test_wrds_strike_tolerance(self, sample_wrds_data):
        """Test strike matching within tolerance."""
        pricer = OptionPricer(
            use_wrds=True,
            wrds_data=sample_wrds_data,
            strike_tolerance=0.05,
        )

        # 3525 is within 5% of 3500 (0.71% difference)
        premium = pricer.get_put_premium(
            strike=3525.0,
            spot=4000.0,
            date=pd.Timestamp("2020-03-01"),
            expiry=pd.Timestamp("2020-06-19"),
            vix=30.0,
        )

        # Should match 3500 strike: 50/4000 = 0.0125
        assert premium == 0.0125

    def test_wrds_expiry_tolerance(self, sample_wrds_data):
        """Test expiry matching within tolerance."""
        pricer = OptionPricer(
            use_wrds=True,
            wrds_data=sample_wrds_data,
            expiry_tolerance_days=7,
        )

        # 2020-06-20 is 1 day from 2020-06-19
        premium = pricer.get_put_premium(
            strike=3500.0,
            spot=4000.0,
            date=pd.Timestamp("2020-03-01"),
            expiry=pd.Timestamp("2020-06-20"),
            vix=30.0,
        )

        # Should match 2020-06-19 expiry: 50/4000 = 0.0125
        assert premium == 0.0125

    def test_wrds_fallback_to_synthetic(self, sample_wrds_data):
        """Test fallback to synthetic when no WRDS match."""
        pricer = OptionPricer(use_wrds=True, wrds_data=sample_wrds_data)

        # Date not in WRDS data
        premium = pricer.get_put_premium(
            strike=3500.0,
            spot=4000.0,
            date=pd.Timestamp("2021-01-01"),
            expiry=pd.Timestamp("2021-03-19"),
            vix=30.0,
        )

        # Should use synthetic pricing
        assert premium > 0

    def test_wrds_no_match_outside_tolerance(self, sample_wrds_data):
        """Test no match when strike outside tolerance."""
        pricer = OptionPricer(
            use_wrds=True,
            wrds_data=sample_wrds_data,
            strike_tolerance=0.01,  # 1% tolerance
        )

        # 3700 is ~5.7% from 3500, outside 1% tolerance
        premium = pricer.get_put_premium(
            strike=3700.0,
            spot=4000.0,
            date=pd.Timestamp("2020-03-01"),
            expiry=pd.Timestamp("2020-06-19"),
            vix=30.0,
        )

        # Should fallback to synthetic
        assert premium > 0

    def test_wrds_no_date_match(self, sample_wrds_data):
        """Test fallback when date not in WRDS data."""
        pricer = OptionPricer(use_wrds=True, wrds_data=sample_wrds_data)

        # Date not in data (2021 vs 2020)
        premium = pricer.get_put_premium(
            strike=3500.0,
            spot=4000.0,
            date=pd.Timestamp("2021-03-01"),
            expiry=pd.Timestamp("2021-06-19"),
            vix=30.0,
        )

        # Should use synthetic pricing
        assert premium > 0

    def test_wrds_no_expiry_match(self, sample_wrds_data):
        """Test fallback when expiry outside tolerance."""
        pricer = OptionPricer(
            use_wrds=True,
            wrds_data=sample_wrds_data,
            expiry_tolerance_days=1,
        )

        # Expiry far from any data (30 days away)
        premium = pricer.get_put_premium(
            strike=3500.0,
            spot=4000.0,
            date=pd.Timestamp("2020-03-01"),
            expiry=pd.Timestamp("2020-07-19"),  # 30 days from 2020-06-19
            vix=30.0,
        )

        # Should use synthetic
        assert premium > 0


class TestOptionPricerConfig:
    """Tests for pricer configuration and stats."""

    def test_get_stats_synthetic(self):
        """Test configuration info for synthetic mode."""
        pricer = OptionPricer()
        stats = pricer.get_stats()

        assert stats["mode"] == "Synthetic"
        assert stats["strike_tolerance"] == 0.05
        assert stats["expiry_tolerance_days"] == 7

    def test_get_stats_wrds(self, sample_wrds_data):
        """Test configuration info for WRDS mode."""
        pricer = OptionPricer(use_wrds=True, wrds_data=sample_wrds_data)
        stats = pricer.get_stats()

        assert stats["mode"] == "WRDS"
        assert stats["wrds_rows"] == 4
        assert "wrds_date_range" in stats

    def test_custom_tolerances(self):
        """Test custom tolerance settings."""
        pricer = OptionPricer(
            strike_tolerance=0.10,
            expiry_tolerance_days=14,
        )

        assert pricer.strike_tolerance == 0.10
        assert pricer.expiry_tolerance_days == 14

        stats = pricer.get_stats()
        assert stats["strike_tolerance"] == 0.10
        assert stats["expiry_tolerance_days"] == 14


class TestOptionPricerEdgeCases:
    """Tests for edge cases and error handling."""

    def test_default_vix_parameter(self):
        """Test default VIX value for synthetic pricing."""
        pricer = OptionPricer()

        # VIX has default value of 20.0
        premium = pricer.get_put_premium(
            strike=3500.0,
            spot=4000.0,
            date=pd.Timestamp("2020-03-01"),
            expiry=pd.Timestamp("2020-06-19"),
        )
        assert premium > 0

    def test_empty_wrds_data(self):
        """Test with empty WRDS DataFrame."""
        empty_df = pd.DataFrame(
            columns=[
                "date",
                "exdate",
                "strike_price",
                "best_bid",
                "best_offer",
            ]
        )
        empty_df["date"] = pd.to_datetime(empty_df["date"])
        empty_df["exdate"] = pd.to_datetime(empty_df["exdate"])

        pricer = OptionPricer(use_wrds=True, wrds_data=empty_df)

        # Should fallback to synthetic
        premium = pricer.get_put_premium(
            strike=3500.0,
            spot=4000.0,
            date=pd.Timestamp("2020-03-01"),
            expiry=pd.Timestamp("2020-06-19"),
            vix=30.0,
        )

        assert premium > 0

    def test_zero_strike_tolerance(self, sample_wrds_data):
        """Test with zero strike tolerance (exact match only)."""
        pricer = OptionPricer(
            use_wrds=True,
            wrds_data=sample_wrds_data,
            strike_tolerance=0.0,
        )

        # Exact match should work: 50/4000 = 0.0125
        exact = pricer.get_put_premium(
            strike=3500.0,
            spot=4000.0,
            date=pd.Timestamp("2020-03-01"),
            expiry=pd.Timestamp("2020-06-19"),
            vix=30.0,
        )
        assert exact == 0.0125

        # Near match should fallback to synthetic
        near = pricer.get_put_premium(
            strike=3501.0,
            spot=4000.0,
            date=pd.Timestamp("2020-03-01"),
            expiry=pd.Timestamp("2020-06-19"),
            vix=30.0,
        )
        # Should use synthetic (won't match WRDS exactly)
        assert near != 0.0125
