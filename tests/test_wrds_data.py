"""Tests for WRDS data loading and encryption utilities."""

from __future__ import annotations

import gzip
import io
from pathlib import Path

import pandas as pd
import pytest
from cryptography.fernet import Fernet, InvalidToken

from options_hedge.wrds_data import (
    get_wrds_data_info,
    load_encrypted_spx_options_data,
    load_encrypted_wrds_data,
)


@pytest.fixture
def sample_wrds_data() -> pd.DataFrame:
    """Create sample WRDS option data for testing."""
    return pd.DataFrame(
        {
            "date": pd.to_datetime(
                ["2020-01-02", "2020-01-02", "2020-01-03", "2020-01-03"]
            ),
            "exdate": pd.to_datetime(
                ["2020-03-20", "2020-06-19", "2020-03-20", "2020-06-19"]
            ),
            "strike_price": [3500.0, 3600.0, 3500.0, 3600.0],
            "cp_flag": ["P", "P", "P", "P"],
            "best_bid": [50.0, 60.0, 52.0, 62.0],
            "best_offer": [52.0, 62.0, 54.0, 64.0],
            "impl_volatility": [0.20, 0.21, 0.19, 0.20],
            "delta": [-0.30, -0.35, -0.29, -0.34],
            "volume": [100, 50, 120, 60],
            "open_interest": [1000, 500, 1100, 550],
        }
    )


@pytest.fixture
def encrypted_test_file(
    tmp_path: Path, sample_wrds_data: pd.DataFrame
) -> tuple[Path, str]:
    """Create an encrypted test file."""
    # Generate encryption key
    key = Fernet.generate_key()
    cipher = Fernet(key)

    # Compress and encrypt data
    csv_buffer = io.BytesIO()
    sample_wrds_data.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)

    compressed = gzip.compress(csv_buffer.read())
    encrypted = cipher.encrypt(compressed)

    # Write to temp file
    enc_file = tmp_path / "test_options.enc"
    with open(enc_file, "wb") as f:
        f.write(encrypted)

    return enc_file, key.decode()


class TestLoadEncryptedWRDSData:
    """Tests for load_encrypted_wrds_data function."""

    def test_load_with_valid_key(self, encrypted_test_file: tuple[Path, str]) -> None:
        """Test loading with valid encryption key."""
        enc_file, key = encrypted_test_file
        data = load_encrypted_wrds_data(encrypted_path=str(enc_file), key=key)

        assert isinstance(data, pd.DataFrame)
        assert len(data) == 4
        assert "date" in data.columns
        assert "strike_price" in data.columns
        assert pd.api.types.is_datetime64_any_dtype(data["date"])
        assert pd.api.types.is_datetime64_any_dtype(data["exdate"])

    def test_load_missing_file(self) -> None:
        """Test error when file doesn't exist."""
        with pytest.raises(FileNotFoundError, match="Encrypted WRDS data not found"):
            load_encrypted_wrds_data(
                encrypted_path="/nonexistent/path.enc", key="fake-key"
            )

    def test_load_missing_key(
        self, encrypted_test_file: tuple[Path, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test error when encryption key not provided."""
        enc_file, _ = encrypted_test_file
        monkeypatch.delenv("WRDS_DATA_KEY", raising=False)

        with pytest.raises(ValueError, match="Decryption key not provided"):
            load_encrypted_wrds_data(encrypted_path=str(enc_file))

    def test_load_invalid_key(self, encrypted_test_file: tuple[Path, str]) -> None:
        """Test error with wrong encryption key."""
        enc_file, _ = encrypted_test_file
        wrong_key = Fernet.generate_key().decode()

        with pytest.raises(ValueError, match="Decryption failed"):
            load_encrypted_wrds_data(encrypted_path=str(enc_file), key=wrong_key)

    def test_load_from_env_var(
        self, encrypted_test_file: tuple[Path, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test loading key from environment variable."""
        enc_file, key = encrypted_test_file
        monkeypatch.setenv("WRDS_DATA_KEY", key)

        data = load_encrypted_wrds_data(encrypted_path=str(enc_file))
        assert len(data) == 4

    def test_load_with_default_path(
        self,
        tmp_path: Path,
        sample_wrds_data: pd.DataFrame,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test loading from default path."""
        # Create test file at expected default location
        # Mock project root to point to tmp_path
        import options_hedge.wrds_data as wrds_module

        original_file = wrds_module.__file__

        # Create data directory
        data_dir = tmp_path / "data"
        data_dir.mkdir()

        # Generate and save encrypted file
        key = Fernet.generate_key()
        cipher = Fernet(key)

        csv_buffer = io.BytesIO()
        sample_wrds_data.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)

        compressed = gzip.compress(csv_buffer.read())
        encrypted = cipher.encrypt(compressed)

        enc_file = data_dir / "wrds_spx_options.enc"
        with open(enc_file, "wb") as f:
            f.write(encrypted)

        # Mock __file__ to make it find our test file
        mock_file = str(tmp_path / "src" / "options_hedge" / "wrds_data.py")
        monkeypatch.setattr(wrds_module, "__file__", mock_file)
        monkeypatch.setenv("WRDS_DATA_KEY", key.decode())

        # Should load from default path
        data = load_encrypted_wrds_data()
        assert len(data) == 4

        # Restore
        monkeypatch.setattr(wrds_module, "__file__", original_file)

    def test_data_structure(self, encrypted_test_file: tuple[Path, str]) -> None:
        """Test loaded data has correct structure."""
        enc_file, key = encrypted_test_file
        data = load_encrypted_wrds_data(encrypted_path=str(enc_file), key=key)

        # Check required columns
        required_cols = [
            "date",
            "exdate",
            "strike_price",
            "cp_flag",
            "best_bid",
            "best_offer",
        ]
        for col in required_cols:
            assert col in data.columns

        # Check data types
        assert data["strike_price"].dtype == float
        assert data["best_bid"].dtype == float

        # Check date parsing
        assert data["date"].min() == pd.Timestamp("2020-01-02")
        assert data["exdate"].max() == pd.Timestamp("2020-06-19")


class TestGetWRDSDataInfo:
    """Tests for get_wrds_data_info function."""

    def test_basic_stats(self, sample_wrds_data: pd.DataFrame) -> None:
        """Test basic data statistics."""
        info = get_wrds_data_info(sample_wrds_data)

        assert info["total_rows"] == 4
        assert info["unique_dates"] == 2
        assert info["avg_strikes_per_date"] == 2.0

    def test_date_range(self, sample_wrds_data: pd.DataFrame) -> None:
        """Test date range calculation."""
        info = get_wrds_data_info(sample_wrds_data)

        start, end = info["date_range"]
        assert start == pd.Timestamp("2020-01-02")
        assert end == pd.Timestamp("2020-01-03")

    def test_strike_range(self, sample_wrds_data: pd.DataFrame) -> None:
        """Test strike price range."""
        info = get_wrds_data_info(sample_wrds_data)

        min_strike, max_strike = info["strike_range"]
        assert min_strike == 3500.0
        assert max_strike == 3600.0

    def test_empty_dataframe(self) -> None:
        """Test with empty DataFrame."""
        empty_df = pd.DataFrame(columns=["date", "exdate", "strike_price", "cp_flag"])
        empty_df["date"] = pd.to_datetime(empty_df["date"])

        info = get_wrds_data_info(empty_df)
        assert info["total_rows"] == 0

    def test_large_dataset_stats(self) -> None:
        """Test statistics with larger dataset."""
        # Create larger sample
        dates = pd.date_range("2020-01-01", "2020-12-31", freq="D")
        data = pd.DataFrame(
            {
                "date": dates.repeat(10),  # 10 strikes per date
                "strike_price": list(range(3000, 3010)) * len(dates),
            }
        )

        info = get_wrds_data_info(data)

        assert info["total_rows"] == len(dates) * 10
        assert info["unique_dates"] == len(dates)
        assert info["avg_strikes_per_date"] == 10.0
        assert info["strike_range"] == (3000, 3009)

    def test_mixed_cp_flags(self) -> None:
        """Test data with both puts and calls."""
        data = pd.DataFrame(
            {
                "date": pd.to_datetime(
                    ["2020-01-02", "2020-01-02", "2020-01-02", "2020-01-02"]
                ),
                "strike_price": [3500.0, 3600.0, 3500.0, 3600.0],
                "cp_flag": ["P", "P", "C", "C"],
            }
        )

        info = get_wrds_data_info(data)
        assert info["total_rows"] == 4


class TestLoadEncryptedWRDSDataEdgeCases:
    """Additional edge case tests for encrypted data loading."""

    def test_load_with_env_var_key(
        self,
        encrypted_test_file: tuple[Path, str],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Test loading key from environment variable."""
        enc_file, key = encrypted_test_file
        monkeypatch.setenv("WRDS_DATA_KEY", key)

        # Should work without explicit key parameter
        data = load_encrypted_wrds_data(encrypted_path=str(enc_file))
        assert isinstance(data, pd.DataFrame)
        assert len(data) == 4

    def test_corrupt_encrypted_file(self, tmp_path: Path) -> None:
        """Test handling of corrupted encrypted file."""
        corrupt_file = tmp_path / "corrupt.enc"
        with open(corrupt_file, "wb") as f:
            f.write(b"this is not valid encrypted data")

        key = Fernet.generate_key().decode()

        # Decryption errors
        with pytest.raises((InvalidToken, ValueError, pd.errors.ParserError)):
            load_encrypted_wrds_data(encrypted_path=str(corrupt_file), key=key)

    def test_empty_encrypted_file(self, tmp_path: Path) -> None:
        """Test handling of empty encrypted file."""
        empty_file = tmp_path / "empty.enc"
        empty_file.touch()

        key = Fernet.generate_key().decode()

        with pytest.raises((InvalidToken, ValueError)):  # Invalid token
            load_encrypted_wrds_data(encrypted_path=str(empty_file), key=key)


class TestLoadEncryptedSPXOptionsData:
    """Tests for load_encrypted_spx_options_data function."""

    @pytest.fixture
    def sample_spx_options_data(self) -> pd.DataFrame:
        """Create sample SPX options data for testing."""
        return pd.DataFrame(
            {
                "date": pd.to_datetime(
                    ["2020-01-02", "2020-01-02", "2020-01-03", "2020-01-03"]
                ),
                "exdate": pd.to_datetime(
                    ["2020-03-20", "2020-06-19", "2020-03-20", "2020-06-19"]
                ),
                "strike_price": [3500.0, 3600.0, 3500.0, 3600.0],
                "cp_flag": ["P", "P", "C", "C"],
                "best_bid": [50.0, 60.0, 52.0, 62.0],
                "best_offer": [52.0, 62.0, 54.0, 64.0],
                "volume": [100, 50, 120, 60],
                "open_interest": [1000, 500, 1100, 550],
            }
        )

    @pytest.fixture
    def encrypted_spx_file(
        self, tmp_path: Path, sample_spx_options_data: pd.DataFrame
    ) -> tuple[Path, str]:
        """Create an encrypted SPX options test file."""
        # Generate encryption key
        key = Fernet.generate_key()
        cipher = Fernet(key)

        # Compress and encrypt data
        csv_buffer = io.BytesIO()
        sample_spx_options_data.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)

        compressed = gzip.compress(csv_buffer.read())
        encrypted = cipher.encrypt(compressed)

        # Write to temp file
        enc_file = tmp_path / "test_spx_options.enc"
        with open(enc_file, "wb") as f:
            f.write(encrypted)

        return enc_file, key.decode()

    def test_load_spx_with_valid_key(
        self, encrypted_spx_file: tuple[Path, str]
    ) -> None:
        """Test loading SPX options with valid encryption key."""
        enc_file, key = encrypted_spx_file
        data = load_encrypted_spx_options_data(encrypted_path=str(enc_file), key=key)

        assert isinstance(data, pd.DataFrame)
        assert len(data) == 4
        assert "date" in data.columns
        assert "exdate" in data.columns
        assert "strike_price" in data.columns
        assert "cp_flag" in data.columns
        assert "best_bid" in data.columns
        assert "best_offer" in data.columns
        assert pd.api.types.is_datetime64_any_dtype(data["date"])
        assert pd.api.types.is_datetime64_any_dtype(data["exdate"])

    def test_load_spx_missing_file(self) -> None:
        """Test error when SPX options file doesn't exist."""
        with pytest.raises(
            FileNotFoundError, match="Encrypted SPX options data not found"
        ):
            load_encrypted_spx_options_data(
                encrypted_path="/nonexistent/spx.enc", key="fake-key"
            )

    def test_load_spx_missing_key(
        self, encrypted_spx_file: tuple[Path, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test error when SPX options encryption key not provided."""
        enc_file, _ = encrypted_spx_file
        monkeypatch.delenv("WRDS_DATA_KEY", raising=False)

        with pytest.raises(ValueError, match="Decryption key not provided"):
            load_encrypted_spx_options_data(encrypted_path=str(enc_file))

    def test_load_spx_invalid_key(self, encrypted_spx_file: tuple[Path, str]) -> None:
        """Test error with wrong SPX options encryption key."""
        enc_file, _ = encrypted_spx_file
        wrong_key = Fernet.generate_key().decode()

        with pytest.raises(ValueError, match="Decryption failed"):
            load_encrypted_spx_options_data(encrypted_path=str(enc_file), key=wrong_key)

    def test_load_spx_with_env_key(
        self, encrypted_spx_file: tuple[Path, str], monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test loading SPX options using environment variable key."""
        enc_file, key = encrypted_spx_file
        monkeypatch.setenv("WRDS_DATA_KEY", key)

        data = load_encrypted_spx_options_data(encrypted_path=str(enc_file))

        assert isinstance(data, pd.DataFrame)
        assert len(data) == 4

    def test_load_spx_corrupt_file(self, tmp_path: Path) -> None:
        """Test handling of corrupted SPX options file."""
        corrupt_file = tmp_path / "corrupt.enc"
        corrupt_file.write_bytes(b"not encrypted data")

        key = Fernet.generate_key().decode()

        # Decryption errors
        with pytest.raises((InvalidToken, ValueError, pd.errors.ParserError)):
            load_encrypted_spx_options_data(encrypted_path=str(corrupt_file), key=key)

    def test_load_spx_empty_file(self, tmp_path: Path) -> None:
        """Test handling of empty SPX options file."""
        empty_file = tmp_path / "empty.enc"
        empty_file.touch()

        key = Fernet.generate_key().decode()

        with pytest.raises((InvalidToken, ValueError)):
            load_encrypted_spx_options_data(encrypted_path=str(empty_file), key=key)

    def test_load_spx_data_types(self, encrypted_spx_file: tuple[Path, str]) -> None:
        """Test that SPX options data has correct types after loading."""
        enc_file, key = encrypted_spx_file
        data = load_encrypted_spx_options_data(encrypted_path=str(enc_file), key=key)

        # Check datetime conversion
        assert pd.api.types.is_datetime64_any_dtype(data["date"])
        assert pd.api.types.is_datetime64_any_dtype(data["exdate"])

        # Check numeric types
        assert pd.api.types.is_numeric_dtype(data["strike_price"])
        assert pd.api.types.is_numeric_dtype(data["best_bid"])
        assert pd.api.types.is_numeric_dtype(data["best_offer"])

        # Check string types
        assert data["cp_flag"].dtype == object
