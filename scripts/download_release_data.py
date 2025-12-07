#!/usr/bin/env python3
"""Download encrypted data from GitHub Releases.

This script downloads encrypted WRDS data files from GitHub Releases
if they don't already exist locally.

Usage:
    python scripts/download_release_data.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from urllib.request import urlretrieve

# Release info
RELEASE_TAG = "data-v1.0.0"
REPO = "cmu-21393-f25-group-D/options-hedge"
BASE_URL = f"https://github.com/{REPO}/releases/download/{RELEASE_TAG}"

# Files to download
FILES = [
    "wrds_spx_options.enc",
    "wrds_sp500.enc",
    "wrds_vix.enc",
    "fred_treasury.enc",
]


def download_if_missing(filename: str, dest_dir: Path) -> None:
    """Download file from release if it doesn't exist locally."""
    dest_path = dest_dir / filename

    if dest_path.exists():
        size_mb = dest_path.stat().st_size / (1024 * 1024)
        print(f"✓ {filename} already exists ({size_mb:.2f} MB)")
        return

    url = f"{BASE_URL}/{filename}"
    print(f"📥 Downloading {filename} from GitHub Release...")
    print(f"   URL: {url}")

    try:
        urlretrieve(url, dest_path)
        size_mb = dest_path.stat().st_size / (1024 * 1024)
        print(f"✓ Downloaded {filename} ({size_mb:.2f} MB)")
    except Exception as e:
        print(f"❌ Failed to download {filename}: {e}")
        sys.exit(1)


def main() -> None:
    """Download all release data files."""
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data"
    data_dir.mkdir(exist_ok=True)

    print(f"Downloading encrypted data from release: {RELEASE_TAG}")
    print(f"Repository: {REPO}\n")

    for filename in FILES:
        download_if_missing(filename, data_dir)

    print("\n✅ All data files ready!")
    print("\n💡 Next step: Set WRDS_DATA_KEY environment variable to decrypt data")
    print("   See WRDS_QUICK_START.md for instructions")


if __name__ == "__main__":
    main()
