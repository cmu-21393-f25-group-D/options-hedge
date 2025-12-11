#!/usr/bin/env python3
"""Download encrypted data from GitHub Releases.

This script downloads encrypted WRDS data files from GitHub Releases
if they don't already exist locally. Validates integrity using SHA256
checksums.

Usage:
    python scripts/download_release_data.py
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from urllib.request import urlretrieve

# Release info
RELEASE_TAG = "data-v1.1.0"
REPO = "cmu-21393-f25-group-D/options-hedge"
BASE_URL = f"https://github.com/{REPO}/releases/download/{RELEASE_TAG}"

# Files to download with SHA256 checksums
FILES = {
    "wrds_spx_options.enc": (
        "5a5b87ff6e19faa541e9fc46ebf52eda65aa711b1f24f02237a8136b196632de"
    ),
    "wrds_sp500.enc": (
        "9437a7c19b1d73c06088be84ab1ad878d1165ed7dc697d9f21e7e6e84449927f"
    ),
    "wrds_vix.enc": (
        "f8de4bfc5980feabe58920464e6f66e017d4f33b33f2508b1e89c14f5e6e0e21"
    ),
    "fred_treasury.enc": (
        "9c364197cb1bb9335ec57386440fa0a8abff8946794f58394e5d0e41bf24440c"
    ),
}


def compute_sha256(filepath: Path) -> str:
    """Compute SHA256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        # Read in 64KB chunks for memory efficiency
        for chunk in iter(lambda: f.read(65536), b""):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


def verify_checksum(filepath: Path, expected_checksum: str) -> bool:
    """Verify file matches expected SHA256 checksum."""
    actual_checksum = compute_sha256(filepath)
    return actual_checksum == expected_checksum


def download_if_missing(filename: str, expected_checksum: str, dest_dir: Path) -> None:
    """Download file from release if it doesn't exist locally."""
    dest_path = dest_dir / filename

    if dest_path.exists():
        size_mb = dest_path.stat().st_size / (1024 * 1024)
        # Verify existing file
        if verify_checksum(dest_path, expected_checksum):
            print(f"✓ {filename} already exists ({size_mb:.2f} MB)")
            return
        else:
            print(f"⚠️  {filename} exists but checksum mismatch, re-downloading...")
            dest_path.unlink()

    url = f"{BASE_URL}/{filename}"
    print(f"📥 Downloading {filename} from GitHub Release...")
    print(f"   URL: {url}")

    try:
        urlretrieve(url, dest_path)
        size_mb = dest_path.stat().st_size / (1024 * 1024)

        # Verify downloaded file
        if not verify_checksum(dest_path, expected_checksum):
            print(f"❌ Checksum verification failed for {filename}")
            print(f"   Expected: {expected_checksum}")
            print(f"   Got:      {compute_sha256(dest_path)}")
            dest_path.unlink()
            sys.exit(1)

        print(f"✓ Downloaded {filename} ({size_mb:.2f} MB)")
        print(f"  Checksum verified: {expected_checksum[:16]}...")
    except Exception as e:
        print(f"❌ Failed to download {filename}: {e}")
        if dest_path.exists():
            dest_path.unlink()
        sys.exit(1)


def main() -> None:
    """Download all release data files."""
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data"
    data_dir.mkdir(exist_ok=True)

    print(f"Downloading encrypted data from release: {RELEASE_TAG}")
    print(f"Repository: {REPO}\n")

    for filename, checksum in FILES.items():
        download_if_missing(filename, checksum, data_dir)

    print("\n✅ All data files ready!")
    print("\n💡 Next step: Set WRDS_DATA_KEY environment variable to decrypt data")
    print("   See WRDS_QUICK_START.md for instructions")


if __name__ == "__main__":
    main()
