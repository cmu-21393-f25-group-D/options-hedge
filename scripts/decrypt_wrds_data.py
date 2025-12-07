#!/usr/bin/env python3
"""Decrypt WRDS option data for local development or CI/CD.

This script decrypts the encrypted WRDS data file using the key
stored in the WRDS_DATA_KEY environment variable.

Usage:
    # Local development
    export WRDS_DATA_KEY="<your-key>"
    python scripts/decrypt_wrds_data.py

    # CI/CD (GitHub Actions)
    env:
      WRDS_DATA_KEY: ${{ secrets.WRDS_DATA_KEY }}
    run: python scripts/decrypt_wrds_data.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from cryptography.fernet import Fernet
except ImportError:
    print("❌ cryptography library not installed. Install with:")
    print("   pip install cryptography")
    sys.exit(1)


def decrypt_wrds_data(
    key: bytes,
    encrypted_path: Path | None = None,
    output_path: Path | None = None,
) -> Path:
    """Decrypt WRDS data file.

    Args:
        key: Encryption key (from environment variable)
        encrypted_path: Path to encrypted file
        output_path: Path for decrypted output

    Returns:
        Path to decrypted file
    """
    if encrypted_path is None:
        encrypted_path = project_root / "data" / "wrds_spx_options.enc"

    if output_path is None:
        output_path = project_root / "data" / "wrds_spx_options.csv.gz"

    if not encrypted_path.exists():
        raise FileNotFoundError(
            f"Encrypted file not found: {encrypted_path}\n"
            "Have you downloaded and committed the WRDS data?"
        )

    print(f"🔓 Decrypting {encrypted_path.relative_to(project_root)}...")

    cipher = Fernet(key)

    with open(encrypted_path, "rb") as f:
        ciphertext = f.read()

    try:
        plaintext = cipher.decrypt(ciphertext)
    except Exception as e:
        raise ValueError(
            f"Decryption failed: {e}\n"
            "Check that WRDS_DATA_KEY matches the original encryption key"
        ) from e

    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(plaintext)

    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"✓ Decrypted to {output_path.relative_to(project_root)} ({size_mb:.2f} MB)")

    return output_path


def main() -> None:
    """Main execution flow."""
    # Get encryption key from environment
    key_str = os.environ.get("WRDS_DATA_KEY")

    if not key_str:
        print("❌ WRDS_DATA_KEY environment variable not set")
        print("\nUsage:")
        print("  export WRDS_DATA_KEY='<your-key>'")
        print("  python scripts/decrypt_wrds_data.py")
        sys.exit(1)

    try:
        key = key_str.encode()
        decrypt_wrds_data(key)
        print("✅ Decryption successful")
    except Exception as e:
        print(f"❌ Decryption failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
