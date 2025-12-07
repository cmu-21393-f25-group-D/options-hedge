# WRDS Data Setup Guide

## Overview

This project uses real historical SPX (S&P 500 Index) option data from **WRDS OptionMetrics** to improve backtest accuracy. The data is encrypted to comply with WRDS academic license terms while allowing use in both local development and CI/CD environments.

## Quick Start (For Users)

If the encrypted data file already exists in the repository, you only need:

1. **Get the decryption key** from the project maintainer
2. **Set environment variable**:
   ```bash
   export WRDS_DATA_KEY="<key-provided-by-maintainer>"
   ```
3. **Use the OptionPricer** in your code:
   ```python
   from options_hedge.option_pricer import OptionPricer
   from options_hedge.wrds_data import load_encrypted_wrds_data

   # Load WRDS data
   wrds_data = load_encrypted_wrds_data()

   # Create pricer with WRDS data
   pricer = OptionPricer(use_wrds=True, wrds_data=wrds_data)

   # Get premium (automatically uses WRDS data)
   premium = pricer.get_put_premium(
       strike=3500,
       spot=4000,
       date=pd.Timestamp('2020-03-01'),
       expiry=pd.Timestamp('2020-06-01'),
       vix=30.0
   )
   ```

## Full Setup (For Data Providers)

If you have WRDS access and need to download/encrypt the data:

### Prerequisites

1. **WRDS Academic Access**: Obtain through your university library
2. **Install dependencies**:
   ```bash
   pip install wrds cryptography pandas
   ```

### Step 1: Download and Encrypt Data

```bash
# Run the download script (requires WRDS credentials)
python scripts/download_wrds_data.py
```

This script will:
1. Connect to WRDS (you'll be prompted for credentials)
2. Download SPX put options (1999-2025, ~300K rows)
3. Save compressed CSV (~10-15 MB)
4. Encrypt data with AES-256
5. Generate encryption key

**Expected output:**
```
==================================================================
WRDS SPX Options Data Download & Encryption
==================================================================

🔐 Connecting to WRDS (you may be prompted for credentials)...
✓ Connected to WRDS

📊 Downloading SPX put options from 1999-01-01 to 2025-12-31...
   (This may take 2-5 minutes depending on connection speed)
✓ Downloaded 300,000 rows
✓ WRDS connection closed

🔍 Data quality checks:
   Date range: 1999-01-04 to 2025-12-31
   Unique dates: 6,543
   Avg strikes per date: 45.8
   Strike range: $500 - $7000
   ✓ No missing values

💾 Saving compressed CSV to data/wrds_spx_options.csv.gz...
   ✓ Saved 12.34 MB

🔐 Generating encryption key...
   Encrypting data...
   ✓ Encrypted to data/wrds_spx_options.enc (12.45 MB)

==================================================================
✅ SUCCESS!
==================================================================

📦 Files created:
   1. data/wrds_spx_options.enc (commit this)
   2. data/wrds_spx_options.csv.gz (reference only, in .gitignore)

🔑 ENCRYPTION KEY (COPY THIS!):
==================================================================
gAAAAABh... (32-byte key)
==================================================================

📋 Next Steps:
1. ✅ Copy the encryption key above
2. ✅ Add to GitHub:
      Settings → Secrets and variables → Actions
      → New repository secret
      Name: WRDS_DATA_KEY
      Value: <paste key>
3. ✅ Commit encrypted file:
      git add data/wrds_spx_options.enc
      git commit -m 'Add encrypted WRDS option data'
4. ✅ Store key securely (without it, data cannot be decrypted!)

⚠️  IMPORTANT:
   - Keep the encryption key PRIVATE
   - Do NOT commit the .csv.gz file (it's in .gitignore)
   - The encrypted .enc file is safe to commit
   - This complies with WRDS academic license terms
```

### Step 2: Add GitHub Secret

1. Go to repository **Settings → Secrets and variables → Actions**
2. Click **New repository secret**
3. Name: `WRDS_DATA_KEY`
4. Value: Paste the encryption key from Step 1
5. Click **Add secret**

### Step 3: Commit Encrypted Data

```bash
# Verify .gitignore is configured correctly
git status  # Should show data/wrds_spx_options.enc as untracked
            # Should NOT show .csv or .csv.gz files

# Add encrypted file
git add data/wrds_spx_options.enc

# Commit
git commit -m "Add encrypted WRDS SPX option data (1999-2025)"

# Push
git push origin feature-branch-name
```

## CI/CD Integration (GitHub Actions)

The encrypted data is automatically decrypted in CI/CD:

```yaml
# .github/workflows/test.yml
jobs:
  test:
    steps:
      - uses: actions/checkout@v4

      - name: Decrypt WRDS data
        env:
          WRDS_DATA_KEY: ${{ secrets.WRDS_DATA_KEY }}
        run: |
          python scripts/decrypt_wrds_data.py

      - name: Run tests with WRDS data
        run: |
          pytest tests/
```

## Data Schema

The WRDS data contains the following columns:

| Column | Type | Description |
|--------|------|-------------|
| `date` | datetime | Trading date |
| `exdate` | datetime | Expiration date |
| `strike_price` | float | Strike price in dollars |
| `cp_flag` | str | 'P' for puts |
| `best_bid` | float | Best bid price |
| `best_offer` | float | Best offer price |
| `impl_volatility` | float | Implied volatility |
| `delta` | float | Option delta |
| `volume` | int | Daily volume |
| `open_interest` | int | Open interest |

## Usage Examples

### Example 1: Basic Usage (Synthetic Fallback)

```python
from options_hedge.option_pricer import OptionPricer
import pandas as pd

# Create pricer (tries WRDS, falls back to synthetic)
pricer = OptionPricer(use_wrds=True)

# Get premium
premium = pricer.get_put_premium(
    strike=3500,      # $3500 strike
    spot=4000,        # $4000 current price (12.5% OTM)
    date=pd.Timestamp('2020-03-01'),
    expiry=pd.Timestamp('2020-06-01'),  # 90 days
    vix=30.0          # VIX at 30 (high volatility)
)

print(f"Premium: {premium:.2%} of notional")
# Output: Premium: 2.50% of notional
```

### Example 2: Pre-load WRDS Data (Faster)

```python
from options_hedge.option_pricer import OptionPricer
from options_hedge.wrds_data import load_encrypted_wrds_data

# Load once at startup
wrds_data = load_encrypted_wrds_data()
print(f"Loaded {len(wrds_data):,} option records")

# Create pricer with pre-loaded data
pricer = OptionPricer(use_wrds=True, wrds_data=wrds_data)

# Use in backtesting loop (no repeated loads)
for date in trading_dates:
    premium = pricer.get_put_premium(...)
```

### Example 3: Custom Matching Tolerances

```python
# Strict matching (must be exact)
pricer = OptionPricer(
    use_wrds=True,
    strike_tolerance=0.01,      # 1% strike tolerance
    expiry_tolerance_days=3     # 3 days expiry tolerance
)

# Loose matching (for illiquid strikes)
pricer = OptionPricer(
    use_wrds=True,
    strike_tolerance=0.10,      # 10% strike tolerance
    expiry_tolerance_days=14    # 2 weeks expiry tolerance
)
```

### Example 4: Check Pricer Stats

```python
pricer = OptionPricer(use_wrds=True)
stats = pricer.get_stats()

print(stats)
# Output:
# {
#     'mode': 'WRDS',
#     'strike_tolerance': 0.05,
#     'expiry_tolerance_days': 7,
#     'wrds_rows': 300000,
#     'wrds_date_range': (Timestamp('1999-01-04'), Timestamp('2025-12-31'))
# }
```

## Troubleshooting

### Problem: "Encrypted file not found"

**Cause**: WRDS data not downloaded yet

**Solution**: Run `python scripts/download_wrds_data.py` (requires WRDS access)

---

### Problem: "Decryption failed"

**Cause**: Wrong encryption key

**Solution**:
1. Verify `WRDS_DATA_KEY` environment variable is set correctly
2. Check that key matches the one used during encryption
3. Contact data provider for correct key

---

### Problem: "No WRDS match found, using synthetic"

**Cause**: Requested option not in WRDS data (e.g., non-trading day, extreme strike)

**Solution**: This is expected behavior - pricer automatically falls back to synthetic pricing

---

### Problem: "Import error: cryptography not installed"

**Cause**: Missing dependency

**Solution**: `pip install cryptography`

---

## License Compliance

### WRDS Academic License Terms

✅ **Allowed**:
- Using data for academic research
- Encrypting data for version control
- Sharing encrypted data with collaborators
- Using in CI/CD with secret key management

❌ **Not Allowed**:
- Distributing raw data publicly
- Commercial use without license
- Sharing decryption key publicly
- Committing unencrypted .csv files

### Attribution

When using WRDS data in publications:

> Option price data provided by **WRDS OptionMetrics IvyDB US**, accessed through [Your University] academic subscription. Data encrypted for compliance with WRDS license terms.

## Data Provenance

- **Source**: Wharton Research Data Services (WRDS)
- **Database**: OptionMetrics IvyDB US
- **Product**: SPX (S&P 500 Index Options)
- **Type**: End-of-day put option prices
- **Period**: January 1999 - December 2025
- **Frequency**: Daily
- **Records**: ~300,000 option-days
- **Quality**: Cleaned, filtered for valid bid/ask spreads

## Security Notes

1. **Encryption**: AES-256-GCM via Python `cryptography.fernet`
2. **Key Storage**: GitHub Secrets (not in code)
3. **Access Control**: Repository collaborators only
4. **Audit Trail**: Git history tracks data changes
5. **Compliance**: WRDS terms require encrypted storage for shared repos

## FAQ

**Q: Why encrypt instead of just using .gitignore?**

A: WRDS license prohibits raw data distribution. Encryption ensures compliance while enabling collaboration and CI/CD.

**Q: Can I use a different encryption key?**

A: Yes, but all users must have the same key. Generate new key during download, store in GitHub secrets.

**Q: What happens if WRDS data is missing for a date?**

A: OptionPricer automatically falls back to synthetic VIX-based pricing. No errors thrown.

**Q: How do I update the WRDS data?**

A: Re-run `download_wrds_data.py` (requires WRDS access), commit new `.enc` file, update GitHub secret if key changed.

**Q: Can I use this with non-SPX options?**

A: Modify SQL query in `download_wrds_data.py` to fetch different tickers (e.g., 'SPY', 'QQQ'). Rest of pipeline works the same.

---

**Last Updated**: December 2025
**Maintainer**: [Your Name/Team]
**WRDS Access**: [Your University] Library
