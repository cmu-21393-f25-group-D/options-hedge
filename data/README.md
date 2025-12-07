# WRDS Option Data

This directory contains encrypted WRDS OptionMetrics data for backtesting.

## Files

- `wrds_spx_options.enc` - Encrypted SPX option data (safe to commit)
- `wrds_spx_options.csv.gz` - Decrypted data (in .gitignore, do NOT commit)

## Setup

See [WRDS_SETUP.md](../docs/WRDS_SETUP.md) for complete instructions.

## Quick Start

```bash
# Set decryption key
export WRDS_DATA_KEY="<key-from-maintainer>"

# Decrypt data (optional, automatic when using OptionPricer)
python scripts/decrypt_wrds_data.py
```

## Data Provenance

- **Source**: WRDS OptionMetrics IvyDB US
- **Period**: January 1999 - December 2025
- **Product**: SPX put options
- **Records**: ~300,000 option-days
- **License**: Academic use only (encrypted for compliance)

## For Data Providers

If you have WRDS access and need to download fresh data:

```bash
pip install wrds cryptography pandas
python scripts/download_wrds_data.py
```

This will generate a new `wrds_spx_options.enc` file and encryption key.
