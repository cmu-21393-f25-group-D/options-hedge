"""Re-encrypt WRDS data files with a new Fernet key.

This script:
1. Decrypts existing data files with the old key
2. Re-encrypts them with the new key
3. Computes SHA256 checksums for the new files
4. Outputs the checksums for updating download_release_data.py

Usage:
    export OLD_WRDS_DATA_KEY="<old-key>"  # Optional
    python scripts/reencrypt_wrds_data.py --new-key <new-key>
"""

import argparse
import hashlib
import os
from pathlib import Path

from cryptography.fernet import Fernet


def compute_sha256(filepath: Path) -> str:
    """Compute SHA256 checksum of a file."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def decrypt_file(encrypted_path: Path, key: str) -> bytes:
    """Decrypt a file with Fernet."""
    cipher = Fernet(key.encode())
    with open(encrypted_path, "rb") as f:
        ciphertext = f.read()
    plaintext: bytes = cipher.decrypt(ciphertext)
    return plaintext


def encrypt_file(plaintext: bytes, output_path: Path, key: str) -> None:
    """Encrypt data and write to file."""
    cipher = Fernet(key.encode())
    ciphertext = cipher.encrypt(plaintext)
    with open(output_path, "wb") as f:
        f.write(ciphertext)
    print(f"✓ Encrypted {output_path.name} ({len(ciphertext):,} bytes)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Re-encrypt WRDS data files")
    parser.add_argument("--new-key", required=True, help="New Fernet key (44 chars)")
    parser.add_argument(
        "--old-key",
        help="Old Fernet key (from env OLD_WRDS_DATA_KEY)",
    )
    args = parser.parse_args()

    # Validate new key
    if len(args.new_key) != 44:
        raise ValueError(f"Invalid key length: {len(args.new_key)} (expected 44)")

    # File paths
    data_dir = Path(__file__).parent.parent / "data"
    files = [
        "wrds_spx_options.enc",
        "wrds_sp500.enc",
        "wrds_vix.enc",
        "fred_treasury.enc",
    ]

    print("=" * 80)
    print("RE-ENCRYPTING WRDS DATA FILES")
    print("=" * 80)

    # Get old key if provided
    old_key = args.old_key or os.environ.get("OLD_WRDS_DATA_KEY")

    checksums = {}

    for filename in files:
        encrypted_path = data_dir / filename
        temp_path = data_dir / f"{filename}.tmp"

        print(f"\nProcessing {filename}...")

        if not encrypted_path.exists():
            print(f"  ⚠️  File not found: {encrypted_path}")
            continue

        # If old key provided, decrypt and re-encrypt
        if old_key:
            print("  Decrypting with old key...")
            plaintext = decrypt_file(encrypted_path, old_key)
            print(f"  Decrypted: {len(plaintext):,} bytes")

            print("  Encrypting with new key...")
            encrypt_file(plaintext, temp_path, args.new_key)

            # Replace original file
            temp_path.replace(encrypted_path)
        else:
            # Assume files need re-encryption but no old key
            print("  ⚠️  No old key - skipping re-encryption")
            print("  Set OLD_WRDS_DATA_KEY to decrypt and re-encrypt")
            continue

        # Compute checksum
        checksum = compute_sha256(encrypted_path)
        checksums[filename] = checksum
        print(f"  SHA256: {checksum}")

    # Output checksums for updating download_release_data.py
    print("\n" + "=" * 80)
    print("NEW CHECKSUMS FOR download_release_data.py")
    print("=" * 80)
    print("\nFILES = {")
    for filename in files:
        if filename in checksums:
            print(f'    "{filename}": "{checksums[filename]}",')
    print("}")

    print("\n" + "=" * 80)
    print("NEXT STEPS:")
    print("=" * 80)
    print(f"1. Save your new key: {args.new_key}")
    print("2. Update scripts/download_release_data.py with:")
    print('   - RELEASE_TAG = "data-v1.1.0"')
    print("   - FILES dict with new checksums (shown above)")
    print("3. Create new GitHub Release 'data-v1.1.0' with re-encrypted files")
    print("4. Update GitHub secret WRDS_DATA_KEY with new key")
    print("5. Test CI workflow")


if __name__ == "__main__":
    main()
