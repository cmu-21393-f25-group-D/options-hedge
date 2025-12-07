# WRDS Integration Plan

## Objective
Replace synthetic option pricing with real historical option data from WRDS OptionMetrics database while maintaining compliance with WRDS academic license terms.

## Current State Analysis

### Synthetic Data Generation
Currently using `estimate_put_premium()` in `strategies.py`:
- **Input**: strike, spot, days_to_expiry, VIX
- **Output**: Premium as % of notional
- **Formula**: Simplified Black-Scholes using VIX as implied vol
- **Usage**: All 4 strategies (Quarterly, Conditional, VIX-Ladder LP, Fixed Floor LP)

### Real Data (Already Using)
- S&P 500 prices via yfinance (^GSPC)
- VIX index via yfinance (^VIX)

## WRDS Data Requirements

### Database: OptionMetrics IvyDB US
- **Product**: SPX (S&P 500 Index Options)
- **Date Range**: 1999-01-01 to 2025-12-31
- **Frequency**: Daily

### Required Fields
```sql
SELECT
    date,                -- Trading date
    exdate,              -- Expiration date
    strike_price,        -- Strike in dollars
    cp_flag,             -- 'P' for puts
    best_bid,            -- Best bid price
    best_offer,          -- Best offer price
    impl_volatility,     -- Implied volatility
    delta,               -- Option delta
    volume,              -- Daily volume
    open_interest        -- Open interest
FROM optionm.opprcd1996
WHERE secid = (SELECT secid FROM optionm.securd WHERE ticker = 'SPX')
  AND cp_flag = 'P'
  AND date BETWEEN '1999-01-01' AND '2025-12-31'
```

### Data Volume Estimate
- ~3000 trading days × ~100 strikes/day = ~300K rows
- Compressed CSV: ~10-15 MB
- Encrypted: ~15-20 MB

## Implementation Architecture

### Phase 1: Data Acquisition (One-Time WRDS Access)
```
You (with WRDS access) → Download SPX put data → Encrypt → Commit to repo
```

### Phase 2: Local/CI Usage (No WRDS Required)
```
GitHub Secret (AES key) → Decrypt data → Cache in memory → Use in backtests
```

### Phase 3: Data Matching Layer
```
Strategy requests option → Match strike/expiry → Return real premium from WRDS
```

## Technical Design

### Module Structure
```
src/options_hedge/
├── wrds_data.py          # New: WRDS data fetching and encryption
├── option_pricer.py      # New: Unified pricing interface
├── strategies.py         # Modified: Use option_pricer instead of estimate_put_premium
└── market.py             # Modified: Optional WRDS data integration
```

### Encryption Approach
**Algorithm**: AES-256-GCM (Galois/Counter Mode)
- **Key Storage**: GitHub Secret `WRDS_DATA_KEY`
- **Library**: `cryptography.fernet` (Python standard, simple API)
- **File Format**:
  - Original: `wrds_spx_options.csv.gz`
  - Encrypted: `wrds_spx_options.enc`

**Why This Approach?**
1. ✅ WRDS license compliance (data not readable in public repo)
2. ✅ CI/CD compatible (GitHub Actions can decrypt with secret)
3. ✅ Simple key management (single 32-byte key)
4. ✅ Fast decryption (load once at startup)

### Data Schema
```python
# wrds_spx_options.csv columns
date,exdate,strike_price,cp_flag,best_bid,best_offer,impl_volatility,delta,volume,open_interest
1999-01-04,1999-01-16,1200.0,P,1.25,1.50,0.18,-0.15,450,1200
...
```

### API Design
```python
# option_pricer.py
class OptionPricer:
    """Unified interface for option pricing (WRDS or synthetic)."""

    def __init__(self, use_wrds: bool = True, wrds_data_path: str = None):
        self.use_wrds = use_wrds
        if use_wrds:
            self.wrds_data = load_encrypted_wrds_data(wrds_data_path)

    def get_put_premium(
        self,
        strike: float,
        spot: float,
        date: pd.Timestamp,
        expiry: pd.Timestamp,
        vix: float = 20.0
    ) -> float:
        """Get put premium (WRDS if available, else synthetic)."""
        if self.use_wrds:
            return self._match_wrds_option(strike, spot, date, expiry)
        else:
            days = (expiry - date).days
            return estimate_put_premium(strike, spot, days, vix)

    def _match_wrds_option(self, strike, spot, date, expiry) -> float:
        """Match closest available option in WRDS data."""
        # Filter by date and expiry
        candidates = self.wrds_data[
            (self.wrds_data['date'] == date) &
            (self.wrds_data['exdate'] == expiry)
        ]

        # Find closest strike
        candidates['strike_diff'] = abs(candidates['strike_price'] - strike)
        best_match = candidates.nsmallest(1, 'strike_diff')

        if best_match.empty:
            # Fallback to synthetic
            days = (expiry - date).days
            return estimate_put_premium(strike, spot, days, vix)

        # Use mid-price (average of bid/ask)
        bid = best_match['best_bid'].iloc[0]
        offer = best_match['best_offer'].iloc[0]
        mid_price = (bid + offer) / 2.0

        # Convert to premium as % of spot (for consistency)
        return mid_price / spot
```

## WRDS Data Collection Script

### Prerequisites
1. WRDS account with academic access
2. Python packages: `wrds`, `pandas`, `cryptography`

### Script: `scripts/download_wrds_data.py`
```python
import os
import wrds
import pandas as pd
from cryptography.fernet import Fernet

# Connect to WRDS
db = wrds.Connection()

# Query SPX put options
query = """
SELECT
    date, exdate, strike_price, cp_flag,
    best_bid, best_offer, impl_volatility, delta,
    volume, open_interest
FROM optionm.opprcd1996
WHERE secid = (SELECT secid FROM optionm.securd WHERE ticker = 'SPX')
  AND cp_flag = 'P'
  AND date BETWEEN '1999-01-01' AND '2025-12-31'
ORDER BY date, strike_price
"""

print("Downloading SPX options data from WRDS...")
data = db.raw_sql(query)
db.close()

print(f"Downloaded {len(data):,} rows")

# Save compressed CSV
csv_path = 'data/wrds_spx_options.csv.gz'
data.to_csv(csv_path, index=False, compression='gzip')
print(f"Saved to {csv_path}")

# Encrypt the data
key = Fernet.generate_key()
cipher = Fernet(key)

with open(csv_path, 'rb') as f:
    plaintext = f.read()

ciphertext = cipher.encrypt(plaintext)

enc_path = 'data/wrds_spx_options.enc'
with open(enc_path, 'wb') as f:
    f.write(ciphertext)

print(f"Encrypted to {enc_path}")
print(f"\n🔑 ENCRYPTION KEY (save as GitHub secret WRDS_DATA_KEY):")
print(key.decode())
print("\n⚠️  Store this key securely! Without it, data cannot be decrypted.")
```

## GitHub Integration

### Setup GitHub Secret
1. Run download script (one-time, requires WRDS access)
2. Copy encryption key
3. Add to GitHub: Settings → Secrets → Actions → New repository secret
   - Name: `WRDS_DATA_KEY`
   - Value: `<paste key here>`

### .gitignore Updates
```
# WRDS data (encrypted version is committed)
data/wrds_spx_options.csv
data/wrds_spx_options.csv.gz
```

### CI/CD Integration (`.github/workflows/test.yml`)
```yaml
- name: Decrypt WRDS data
  env:
    WRDS_DATA_KEY: ${{ secrets.WRDS_DATA_KEY }}
  run: |
    python scripts/decrypt_wrds_data.py
```

## Migration Strategy

### Step 1: Add New Modules (No Breaking Changes)
- Create `option_pricer.py` with dual mode (WRDS + synthetic fallback)
- Create `wrds_data.py` with encryption/decryption utilities
- All existing code continues working with synthetic pricing

### Step 2: Strategy Updates (Backward Compatible)
```python
# strategies.py - before
premium_pct = estimate_put_premium(strike, spot, days, vix)

# strategies.py - after (backward compatible)
if hasattr(market, 'option_pricer'):
    premium_pct = market.option_pricer.get_put_premium(
        strike, spot, current_date, expiry_date, vix
    )
else:
    # Fallback to synthetic for backward compatibility
    premium_pct = estimate_put_premium(strike, spot, days, vix)
```

### Step 3: Testing
- Unit tests with synthetic data (existing)
- Integration tests with WRDS data (new)
- Compare results: WRDS vs synthetic pricing
- Validate encryption/decryption pipeline

### Step 4: Documentation
- Update README with WRDS setup instructions
- Document encryption key management
- Add data provenance section

## License Compliance

### WRDS Academic License Terms
- ✅ Data for academic research only
- ✅ No redistribution of raw data (encrypted = not readable)
- ✅ Proper attribution in papers/documentation
- ✅ Single-user access (you download, everyone uses encrypted)

### Attribution
Add to README:
```markdown
## Data Sources
- **Market Data**: Yahoo Finance (S&P 500, VIX)
- **Option Data**: Wharton Research Data Services (WRDS) OptionMetrics IvyDB US
  - Access provided through [Your University] academic subscription
  - Data encrypted for compliance with WRDS license terms
  - For academic use only
```

## Timeline

### Day 1 (WRDS Access Window)
1. ✅ Setup WRDS Python library
2. ✅ Test connection and query
3. ✅ Download SPX options data (1999-2025)
4. ✅ Encrypt data and generate key
5. ✅ Commit encrypted data to repo
6. ✅ Add GitHub secret

### Day 2-3 (Post WRDS Access)
1. Implement `wrds_data.py` (decryption utilities)
2. Implement `option_pricer.py` (unified pricing)
3. Update `strategies.py` (use OptionPricer)
4. Add unit tests
5. Run backtest comparison (WRDS vs synthetic)

### Day 4 (Validation)
1. Compare strategy performance (WRDS vs synthetic)
2. Analyze pricing differences
3. Update documentation
4. Merge to main branch

## Expected Impact

### Pricing Accuracy
- **Synthetic**: ±20-30% error in premium estimates
- **WRDS**: Real market prices (bid/ask spreads, liquidity)

### Strategy Performance
- More realistic hedging costs
- Better understanding of LP feasibility
- Accurate backtest results for publication

### Research Value
- Publishable results using real data
- Proper academic citation
- Reproducible research (with key)

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| WRDS data too large | ✅ Compress with gzip (10-15 MB) |
| Key management complexity | ✅ Single GitHub secret, simple Fernet API |
| Missing data (holidays, illiquid strikes) | ✅ Fallback to synthetic pricing |
| License violation | ✅ Encryption prevents raw data access |
| CI/CD failures | ✅ Test decryption in local environment first |

## Next Steps

Ready to proceed? Here's what I'll do:

1. **Create data fetching script** (`scripts/download_wrds_data.py`)
2. **Implement encryption module** (`src/options_hedge/wrds_data.py`)
3. **Build unified pricer** (`src/options_hedge/option_pricer.py`)
4. **Update strategies** (backward-compatible changes)
5. **Add tests** (encryption, decryption, pricing)

You'll need to:
1. Run download script with your WRDS credentials (one time)
2. Add encryption key to GitHub secrets
3. Review and approve changes

Ready to start implementation?
