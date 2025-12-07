"""WRDS option data loading and encryption utilities.

This module provides functions to decrypt and load encrypted WRDS
OptionMetrics data for use in backtesting strategies.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import pandas as pd

try:
    from cryptography.fernet import Fernet

    CRYPTO_AVAILABLE = True
except ImportError:  # pragma: no cover
    CRYPTO_AVAILABLE = False


def load_encrypted_wrds_data(
    encrypted_path: Optional[str] = None, key: Optional[str] = None
) -> pd.DataFrame:
    """Load and decrypt WRDS option data.

    Parameters
    ----------
    encrypted_path : str, optional
        Path to encrypted data file. If None, uses default location
        (data/wrds_spx_options.enc)
    key : str, optional
        Encryption key. If None, reads from WRDS_DATA_KEY environment variable

    Returns
    -------
    pd.DataFrame
        Decrypted WRDS option data with columns:
        - date: Trading date
        - exdate: Expiration date
        - strike_price: Strike price in dollars
        - cp_flag: 'P' for puts
        - best_bid: Best bid price
        - best_offer: Best offer price
        - impl_volatility: Implied volatility
        - delta: Option delta
        - volume: Daily volume
        - open_interest: Open interest

    Raises
    ------
    ImportError
        If cryptography library not installed
    FileNotFoundError
        If encrypted file not found
    ValueError
        If decryption key not provided or decryption fails

    Examples
    --------
    >>> # Load with default paths and env var key
    >>> data = load_encrypted_wrds_data()
    >>> len(data)
    300000
    >>> # Load with custom key
    >>> data = load_encrypted_wrds_data(key="my-secret-key")
    """
    if not CRYPTO_AVAILABLE:  # pragma: no cover
        raise ImportError(
            "cryptography library not installed. Install with: pip install cryptography"
        )

    # Default encrypted file path
    if encrypted_path is None:
        project_root = Path(__file__).parent.parent.parent
        encrypted_path = str(project_root / "data" / "wrds_spx_options.enc")

    if not Path(encrypted_path).exists():
        raise FileNotFoundError(
            f"Encrypted WRDS data not found: {encrypted_path}\n"
            "Run scripts/download_wrds_data.py to download and encrypt data."
        )

    # Get decryption key
    if key is None:
        key = os.environ.get("WRDS_DATA_KEY")

    if not key:
        raise ValueError(
            "Decryption key not provided. Either:\n"
            "1. Set WRDS_DATA_KEY environment variable, or\n"
            '2. Pass key parameter: load_encrypted_wrds_data(key="...")'
        )

    # Decrypt data
    cipher = Fernet(key.encode())

    with open(encrypted_path, "rb") as f:
        ciphertext = f.read()

    try:
        plaintext = cipher.decrypt(ciphertext)
    except Exception as e:
        raise ValueError(
            f"Decryption failed: {e}\n"
            "Check that WRDS_DATA_KEY matches the original encryption key"
        ) from e

    # Load into DataFrame
    import gzip
    import io

    decompressed = gzip.decompress(plaintext)
    data = pd.read_csv(io.BytesIO(decompressed), low_memory=False)

    # Convert date columns to datetime
    data["date"] = pd.to_datetime(data["date"])
    data["exdate"] = pd.to_datetime(data["exdate"])

    return data


def load_encrypted_sp500_data(
    encrypted_path: Optional[str] = None, key: Optional[str] = None
) -> pd.DataFrame:
    """Load and decrypt WRDS S&P 500 index data.

    Parameters
    ----------
    encrypted_path : str, optional
        Path to encrypted data file. If None, uses default location
        (data/wrds_sp500.enc)
    key : str, optional
        Encryption key. If None, reads from WRDS_DATA_KEY environment variable

    Returns
    -------
    pd.DataFrame
        S&P 500 index data with columns including:
        - date: Trading date
        - open, high, low, close: OHLC prices
        - volume: Trading volume
        - return: Daily returns
    """
    if not CRYPTO_AVAILABLE:  # pragma: no cover
        raise ImportError(
            "cryptography library not installed. Install with: pip install cryptography"
        )

    if encrypted_path is None:
        project_root = Path(__file__).parent.parent.parent
        encrypted_path = str(project_root / "data" / "wrds_sp500.enc")

    if not Path(encrypted_path).exists():
        raise FileNotFoundError(f"Encrypted S&P 500 data not found: {encrypted_path}")

    if key is None:
        key = os.environ.get("WRDS_DATA_KEY")

    if not key:
        raise ValueError(
            "Decryption key not provided. Either:\n"
            "1. Set WRDS_DATA_KEY environment variable, or\n"
            '2. Pass key parameter: load_encrypted_sp500_data(key="...")'
        )

    cipher = Fernet(key.encode())
    with open(encrypted_path, "rb") as f:
        ciphertext = f.read()

    try:
        plaintext = cipher.decrypt(ciphertext)
    except Exception as e:
        raise ValueError(f"Decryption failed: {e}") from e

    import gzip
    import io

    decompressed = gzip.decompress(plaintext)
    data = pd.read_csv(io.BytesIO(decompressed))
    data["date"] = pd.to_datetime(data["date"])

    return data


def load_encrypted_vix_data(
    encrypted_path: Optional[str] = None, key: Optional[str] = None
) -> pd.DataFrame:
    """Load and decrypt WRDS VIX index data.

    Parameters
    ----------
    encrypted_path : str, optional
        Path to encrypted data file. If None, uses default location
        (data/wrds_vix.enc)
    key : str, optional
        Encryption key. If None, reads from WRDS_DATA_KEY environment variable

    Returns
    -------
    pd.DataFrame
        VIX index data with columns including:
        - date: Trading date
        - open, high, low, close: OHLC prices
    """
    if not CRYPTO_AVAILABLE:  # pragma: no cover
        raise ImportError(
            "cryptography library not installed. Install with: pip install cryptography"
        )

    if encrypted_path is None:
        project_root = Path(__file__).parent.parent.parent
        encrypted_path = str(project_root / "data" / "wrds_vix.enc")

    if not Path(encrypted_path).exists():
        raise FileNotFoundError(f"Encrypted VIX data not found: {encrypted_path}")

    if key is None:
        key = os.environ.get("WRDS_DATA_KEY")

    if not key:
        raise ValueError(
            "Decryption key not provided. Either:\n"
            "1. Set WRDS_DATA_KEY environment variable, or\n"
            '2. Pass key parameter: load_encrypted_vix_data(key="...")'
        )

    cipher = Fernet(key.encode())
    with open(encrypted_path, "rb") as f:
        ciphertext = f.read()

    try:
        plaintext = cipher.decrypt(ciphertext)
    except Exception as e:
        raise ValueError(f"Decryption failed: {e}") from e

    import gzip
    import io

    decompressed = gzip.decompress(plaintext)
    data = pd.read_csv(io.BytesIO(decompressed))
    data["date"] = pd.to_datetime(data["date"])

    return data


def load_encrypted_treasury_data(
    encrypted_path: Optional[str] = None, key: Optional[str] = None
) -> pd.DataFrame:
    """Load and decrypt FRED 3-month Treasury rate data.

    Parameters
    ----------
    encrypted_path : str, optional
        Path to encrypted data file. If None, uses default location
        (data/fred_treasury.enc)
    key : str, optional
        Encryption key. If None, reads from WRDS_DATA_KEY environment variable

    Returns
    -------
    pd.DataFrame
        Treasury rate data with columns:
        - observation_date: Date
        - DTB3: 3-month Treasury bill rate (annualized %)
    """
    if not CRYPTO_AVAILABLE:  # pragma: no cover
        raise ImportError(
            "cryptography library not installed. Install with: pip install cryptography"
        )

    if encrypted_path is None:
        project_root = Path(__file__).parent.parent.parent
        encrypted_path = str(project_root / "data" / "fred_treasury.enc")

    if not Path(encrypted_path).exists():
        raise FileNotFoundError(f"Encrypted Treasury data not found: {encrypted_path}")

    if key is None:
        key = os.environ.get("WRDS_DATA_KEY")

    if not key:
        raise ValueError(
            "Decryption key not provided. Either:\n"
            "1. Set WRDS_DATA_KEY environment variable, or\n"
            '2. Pass key parameter: load_encrypted_treasury_data(key="...")'
        )

    cipher = Fernet(key.encode())
    with open(encrypted_path, "rb") as f:
        ciphertext = f.read()

    try:
        plaintext = cipher.decrypt(ciphertext)
    except Exception as e:
        raise ValueError(f"Decryption failed: {e}") from e

    import gzip
    import io

    decompressed = gzip.decompress(plaintext)
    data = pd.read_csv(io.BytesIO(decompressed))
    data["observation_date"] = pd.to_datetime(data["observation_date"])

    return data


def get_wrds_data_info(data: pd.DataFrame) -> dict:
    """Get summary statistics about WRDS option data.

    Parameters
    ----------
    data : pd.DataFrame
        WRDS option data from load_encrypted_wrds_data()

    Returns
    -------
    dict
        Dictionary with data statistics:
        - total_rows: Total number of rows
        - date_range: (start_date, end_date)
        - unique_dates: Number of unique trading dates
        - avg_strikes_per_date: Average number of strikes per date
        - strike_range: (min_strike, max_strike)

    Examples
    --------
    >>> data = load_encrypted_wrds_data()
    >>> info = get_wrds_data_info(data)
    >>> info['date_range']
    (Timestamp('1999-01-04'), Timestamp('2025-12-31'))
    """
    unique_dates = data["date"].nunique()
    return {
        "total_rows": len(data),
        "date_range": (data["date"].min(), data["date"].max()),
        "unique_dates": unique_dates,
        "avg_strikes_per_date": len(data) / unique_dates if unique_dates > 0 else 0.0,
        "strike_range": (data["strike_price"].min(), data["strike_price"].max()),
    }
