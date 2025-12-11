#!/usr/bin/env python3
"""Test WRDS encryption key from environment variable."""

import os
import sys
from pathlib import Path

try:
    from cryptography.fernet import Fernet
except ImportError:
    print("ERROR: cryptography library not installed")
    sys.exit(1)


def main() -> None:
    """Test WRDS_DATA_KEY environment variable."""
    key = os.environ.get("WRDS_DATA_KEY")

    print("=" * 80)
    print("WRDS_DATA_KEY Environment Variable Test")
    print("=" * 80)

    if key is None:
        print("❌ WRDS_DATA_KEY environment variable is NOT set")
        sys.exit(1)

    print("✓ WRDS_DATA_KEY is set")
    print(f"  Length: {len(key)} characters")
    print(f"  First 10 chars: {key[:10]}...")
    print(f"  Last 10 chars: ...{key[-10:]}")
    print(f"  Has leading whitespace: {key != key.lstrip()}")
    print(f"  Has trailing whitespace: {key != key.rstrip()}")

    # Test if it's a valid Fernet key
    try:
        cipher = Fernet(key.encode())
        print("✓ Valid Fernet key format")
    except ValueError as e:
        print(f"❌ Invalid Fernet key: {e}")
        sys.exit(1)

    # Test decryption on smallest file
    test_file = Path("data/fred_treasury.enc")
    if not test_file.exists():
        print(f"⚠️  Test file not found: {test_file}")
        print("   Skipping decryption test")
        return

    try:
        with open(test_file, "rb") as f:
            ciphertext = f.read()
        plaintext = cipher.decrypt(ciphertext)
        print(f"✓ Successfully decrypted {test_file.name} ({len(plaintext)} bytes)")
        print("\n🎉 All tests passed! WRDS_DATA_KEY is correctly configured.")
    except ValueError as e:
        print(f"❌ Decryption failed: {e}")
        print("   The key is set but cannot decrypt the data files.")
        print("   This means the key value is incorrect.")
        sys.exit(1)


if __name__ == "__main__":
    main()
