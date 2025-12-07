# Your WRDS Access Day Checklist

## 🎯 Goal
Download and encrypt SPX option data from WRDS during your one-day access window.

## ✅ Pre-Flight Checklist

### Before You Start
- [ ] You have WRDS credentials (username/password from library)
- [ ] You have 30-60 minutes available
- [ ] You have stable internet connection
- [ ] You have disk space (~50 MB free)

### Install Dependencies
```bash
# Install WRDS client and encryption library
pip install wrds cryptography pandas

# Verify installations
python -c "import wrds; print('✓ WRDS OK')"
python -c "import cryptography; print('✓ Crypto OK')"
```

## 📥 Step 1: Download Data (15-20 minutes)

```bash
# Run download script
python scripts/download_wrds_data.py
```

### What to Expect:
1. **WRDS Login Prompt**: Enter your credentials
2. **Download Progress**: 2-5 minutes depending on connection
3. **Data Validation**: Script checks for missing values, date ranges
4. **Encryption**: Automatic AES-256 encryption
5. **Key Generation**: **COPY THIS KEY!** You'll need it next

### Expected Output:
```
==================================================================
✅ SUCCESS!
==================================================================

📦 Files created:
   1. data/wrds_spx_options.enc (commit this)
   2. data/wrds_spx_options.csv.gz (reference only, in .gitignore)

🔑 ENCRYPTION KEY (COPY THIS!):
==================================================================
gAAAAABh4a3bKxYZ... [LONG BASE64 STRING]
==================================================================
```

**⚠️ CRITICAL**: Copy the entire encryption key NOW! Store it somewhere safe (password manager, secure note).

## 🔐 Step 2: Add GitHub Secret (2 minutes)

1. **Go to GitHub**:
   - Navigate to: `https://github.com/cmu-21393-f25-group-D/options-hedge`
   - Click: **Settings** (top menu)
   - Click: **Secrets and variables** → **Actions** (left sidebar)
   - Click: **New repository secret** (green button)

2. **Add Secret**:
   - Name: `WRDS_DATA_KEY`
   - Secret: Paste the encryption key from Step 1
   - Click: **Add secret**

3. **Verify**: You should see `WRDS_DATA_KEY` in the secrets list

## 📤 Step 3: Commit Encrypted Data (5 minutes)

```bash
# Check git status (verify only .enc shows up)
git status

# You should see:
#   Untracked files:
#     data/wrds_spx_options.enc
#
# You should NOT see:
#   data/wrds_spx_options.csv
#   data/wrds_spx_options.csv.gz

# If you see .csv files, they're in .gitignore (correct!)
# Only the .enc file should be tracked

# Add encrypted file
git add data/wrds_spx_options.enc

# Commit
git commit -m "Add encrypted WRDS SPX option data (1999-2025)

- Downloaded from WRDS OptionMetrics IvyDB US
- Contains ~300K SPX put option records
- Period: 1999-01-04 to 2025-12-31
- Encrypted with AES-256 for license compliance
- Decryption key stored in GitHub secret WRDS_DATA_KEY"

# Push to your branch
git push origin feature/integrate-lp-fixed-floor
```

## ✅ Step 4: Verify Setup (5 minutes)

### Local Test
```bash
# Set environment variable
export WRDS_DATA_KEY="<paste-your-key>"

# Test decryption
python scripts/decrypt_wrds_data.py

# Expected output: ✓ Decrypted to data/wrds_spx_options.csv.gz (XX.XX MB)

# Test data loading
python -c "
from options_hedge.wrds_data import load_encrypted_wrds_data
data = load_encrypted_wrds_data()
print(f'✓ Loaded {len(data):,} option records')
print(f'✓ Date range: {data[\"date\"].min()} to {data[\"date\"].max()}')
"

# Expected output:
# ✓ Loaded 300,000 option records
# ✓ Date range: 1999-01-04 to 2025-12-31
```

### Test OptionPricer
```bash
python -c "
from options_hedge.option_pricer import OptionPricer
import pandas as pd

pricer = OptionPricer(use_wrds=True)
stats = pricer.get_stats()
print(f'Mode: {stats[\"mode\"]}')
print(f'WRDS rows: {stats[\"wrds_rows\"]:,}')
print(f'Date range: {stats[\"wrds_date_range\"]}')

# Test actual pricing
premium = pricer.get_put_premium(
    strike=3500,
    spot=4000,
    date=pd.Timestamp('2020-03-01'),
    expiry=pd.Timestamp('2020-06-01'),
    vix=30.0
)
print(f'✓ Sample premium: {premium:.2%}')
"
```

## 🎉 Success Criteria

You're done when:
- [ ] `data/wrds_spx_options.enc` exists and is committed
- [ ] GitHub secret `WRDS_DATA_KEY` is set
- [ ] Local decryption test passes
- [ ] OptionPricer loads and prices options
- [ ] All output shows ~300K records

## 🆘 Troubleshooting

### "Connection refused" or "Authentication failed"
**Problem**: Can't connect to WRDS
**Solution**:
1. Check internet connection
2. Verify WRDS credentials (try logging in to wrds-www.wharton.upenn.edu)
3. Contact library if account expired

---

### "No data returned" or "Empty DataFrame"
**Problem**: SQL query returned 0 rows
**Solution**:
1. Check date range in script (should be 1999-2025)
2. Verify ticker is 'SPX' not 'SPY'
3. WRDS database might be down - try again later

---

### "Permission denied" when committing
**Problem**: Can't push to repository
**Solution**:
1. Make sure you're on your feature branch: `git checkout feature/integrate-lp-fixed-floor`
2. If main branch is protected, create new branch: `git checkout -b add-wrds-data`

---

### "Decryption failed" after committing
**Problem**: Wrong key or corrupted file
**Solution**:
1. Verify you copied the ENTIRE key (should be ~100+ characters)
2. Check for extra spaces or newlines in GitHub secret
3. Re-run download script if needed

## 📊 What You've Accomplished

After completing these steps:

✅ **Data**: 300,000+ real option prices from 26 years of market history
✅ **Compliance**: Encrypted data meets WRDS academic license terms
✅ **Collaboration**: Team can use data without needing WRDS access
✅ **CI/CD**: GitHub Actions can run backtests with real data
✅ **Research**: Publishable results using professional-grade data

## 🚀 Next Steps (After WRDS Access)

Once data is committed, you can:

1. **Update strategies** to use WRDS data (optional)
2. **Run backtests** with real option prices
3. **Compare results** between WRDS and synthetic pricing
4. **Analyze** how LP feasibility changes with real data

See `docs/WRDS_IMPLEMENTATION_SUMMARY.md` for integration examples.

---

**Questions?**
- Technical: See `docs/WRDS_SETUP.md`
- Process: See `docs/WRDS_INTEGRATION_PLAN.md`
- Data issues: Check WRDS documentation or contact support

**Time estimate**: ~30 minutes total if everything goes smoothly

Good luck! 🍀
