# WRDS Data Quick Start

## For Team Members / CI/CD

The encrypted WRDS data is stored in **GitHub Releases** (not in Git) to avoid repository bloat.

### 1. Download Encrypted Data

```bash
# Downloads all .enc files from GitHub Release
python scripts/download_release_data.py
```

This downloads ~1.2GB from: https://github.com/cmu-21393-f25-group-D/options-hedge/releases/tag/data-v1.0.0

### 2. Get Decryption Key

Ask a team member for the `WRDS_DATA_KEY` value, or get it from GitHub Secrets.

```bash
# Set environment variable (macOS/Linux)
export WRDS_DATA_KEY="<key-from-team-member>"

# Or add to ~/.zshrc for persistence
echo 'export WRDS_DATA_KEY="<key>"' >> ~/.zshrc
source ~/.zshrc
```

### 3. Use in Code

```python
from options_hedge.wrds_data import load_encrypted_wrds_data

# Automatically decrypts using WRDS_DATA_KEY env var
data = load_encrypted_wrds_data()
print(f"Loaded {len(data):,} option records")
```

## For Original Data Download (Already Done)

This section is only if you need to re-download from WRDS (requires 1-day access pass):

### Get WRDS 1-Day Pass
2. **Downloads ~300K rows** (takes 2-5 minutes)
3. **Encrypts data** automatically
4. **Prints encryption key** - **COPY THIS!**

### After Download Completes

```bash
# The script will show:
🔑 ENCRYPTION KEY (COPY THIS!):
==================================================================
gAAAAABh4a3bKxYZ... [LONG STRING]
==================================================================

# Copy that entire key!
```

### Add to GitHub

1. Go to: https://github.com/cmu-21393-f25-group-D/options-hedge/settings/secrets/actions
2. Click "New repository secret"
3. Name: `WRDS_DATA_KEY`
4. Value: Paste the key
5. Click "Add secret"

### Commit the Data

```bash
# Verify only .enc file shows up
git status

# Should see: data/wrds_spx_options.enc
# Should NOT see: data/wrds_spx_options.csv or .csv.gz

# Commit
git add data/wrds_spx_options.enc
git commit -m "Add encrypted WRDS SPX option data (1999-2025)"
git push
```

### Verify It Works

```bash
# Set your encryption key
export WRDS_DATA_KEY="<paste-key-here>"

# Test it
python -c "
from options_hedge.wrds_data import load_encrypted_wrds_data
data = load_encrypted_wrds_data()
print(f'✓ Loaded {len(data):,} options')
print(f'✓ Date range: {data[\"date\"].min()} to {data[\"date\"].max()}')
"
```

Expected output:
```
✓ Loaded 300,000 options
✓ Date range: 1999-01-04 to 2025-12-31
```

## That's It!

Total time: ~30 minutes

Questions? See `docs/WRDS_ACCESS_CHECKLIST.md` for detailed steps.
