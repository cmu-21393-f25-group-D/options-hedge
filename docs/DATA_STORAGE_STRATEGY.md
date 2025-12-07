# WRDS Data Storage Strategy

## Decision: GitHub Releases (Not Git/LFS)

### Why This Approach?

**Problem:** 1.1GB encrypted file exceeds GitHub's 100MB limit for Git commits.

**Constraint:** Data must stay encrypted (WRDS licensing - proprietary academic data).

**Solution:** Store encrypted files in GitHub Releases, not in Git repository.

### Comparison of Options

| Option | Git Bloat | Cost | Setup | CI/CD | Our Choice |
|--------|-----------|------|-------|-------|------------|
| **Git Commit** | ❌ 1GB+ history | Free | Simple | Slow | ❌ Blocked by GitHub |
| **Git LFS** | ⚠️ Pointers only | $5/mo | Medium | Medium | ⚠️ Costs money |
| **GitHub Releases** | ✅ No bloat | Free | Simple | Fast | ✅ **CHOSEN** |
| **DVC + S3** | ✅ No bloat | ~$1/mo | Complex | Fast | ⚠️ Overkill for now |

### Implementation

**Storage:**
- Encrypted files (`.enc`) uploaded to GitHub Release assets
- Release tag: `data-v1.0.0`
- Free hosting up to 2GB per file
- No Git repository bloat

**Access:**
1. **Team members:** Run `python scripts/download_release_data.py`
2. **CI/CD:** Download in workflow from release URL
3. **Decryption:** Use `WRDS_DATA_KEY` from GitHub Secrets

**Files Structure:**
```
# In Git (code only, ~50KB)
.gitignore           # Ignores data/*.enc
scripts/download_release_data.py
scripts/decrypt_wrds_data.py
src/options_hedge/wrds_data.py

# In GitHub Release (data, ~1.2GB)
wrds_spx_options.enc  (1.1GB)
wrds_sp500.enc        (170KB)
wrds_vix.enc          (130KB)
fred_treasury.enc     (40KB)

# In GitHub Secrets
WRDS_DATA_KEY         (encryption key)
```

### CI/CD Integration

```yaml
# .github/workflows/test.yml
steps:
  - uses: actions/checkout@v4

  - name: Download encrypted data
    run: python scripts/download_release_data.py

  - name: Decrypt data
    env:
      WRDS_DATA_KEY: ${{ secrets.WRDS_DATA_KEY }}
    run: python scripts/decrypt_wrds_data.py

  - name: Run tests
    run: pytest

  - name: Execute notebook
    run: jupyter nbconvert --execute notebooks/simulate_portfolio.ipynb
```

### Advantages

✅ **No Git bloat:** Repository stays small (~50MB max)
✅ **Free:** GitHub Releases free for public repos
✅ **Simple:** Just download + decrypt
✅ **Fast CI:** Downloads only when needed
✅ **Secure:** Data encrypted, key in Secrets
✅ **Academic compliant:** WRDS data never exposed publicly

### Future Migration Path

If project scales:
- Move to **DVC + S3** for version control
- Keep encryption for compliance
- Same CI/CD pattern (download + decrypt)

### Data Licensing Note

**WRDS OptionMetrics data is proprietary** - only for academic research.
- ✅ Encryption prevents unauthorized access
- ✅ GitHub Secrets limit key distribution
- ✅ Complies with WRDS terms of service
- ❌ Never commit unencrypted CSV files to Git
