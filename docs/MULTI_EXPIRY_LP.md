# Multi-Expiry LP Optimization

## Overview

The LP VIX-Adaptive Floor strategy now supports **multi-expiry optimization**. Instead of buying options with a single fixed maturity (e.g., always 90-day puts), the LP solver can now choose the optimal mix across multiple expiration dates simultaneously.

**Key Innovation:** LP selects cost-minimal portfolio from options with different maturities (14d, 30d, 60d, 90d), adapting to market conditions.

---

## Why Multi-Expiry Matters

### Problem with Single Expiry

**COVID-19 Case Study (Feb-Dec 2020):**
- **Fixed 90-day expiry**: LP bought 90-day puts throughout COVID
- **Problem**: During March crash, VIX spiked to 82
  - 90-day options became VERY expensive (1.5-3% of notional)
  - Options covered through June (entire recovery period!)
  - Portfolio paid for protection during the V-shaped bounce
- **Result**: -5.72% underperformance vs unhedged

**What went wrong:**
1. **Overpaid during crisis**: 90-day puts at VIX=80 are 5x more expensive than VIX=16
2. **Covered unwanted period**: Options expired in June when market was up 30%
3. **Locked into long duration**: Couldn't adapt as VIX declined

### Solution: Dynamic Expiry Selection

**With multi-expiry:**
- **Feb (VIX=15)**: Buy mix of 60d + 90d (cheap tail protection)
- **Mar (VIX=50)**: Buy only 14d + 30d (expires before recovery)
- **Apr-May (VIX=30-40)**: Buy 21d (short coverage during elevated vol)
- **Jul+ (VIX<25)**: Resume 60-90d (normal protection)

**Expected improvement:** Reduce -5.72% drag to ~-1% drag

---

## How It Works

### Option Chain Construction

**Single Expiry (old):**
```python
strikes = [5%, 10%, 15%, 20%, 25%, 30% OTM]
expiry = 90 days
option_chain = 6 options (one per strike)
```

**Multi-Expiry (new):**
```python
strikes = [5%, 10%, 15%, 20%, 25%, 30% OTM]
expiries = [14, 30, 60, 90 days]
option_chain = 24 options (6 strikes × 4 expiries)
```

### LP Optimization

The LP solver minimizes total premium cost:

$$
\min_{x_j} \sum_{j=1}^{n} c_j (1 + \tau) x_j
$$

Subject to floor constraint:

$$
\sum_{j=1}^{n} \text{payoff}_j(S_{\text{stress}}) \cdot x_j \geq \text{Gap}
$$

Where:
- $x_j$ = quantity of option $j$ (now includes all strike-expiry combos)
- $c_j$ = premium (VIX-based, varies by expiry)
- $\tau$ = transaction cost rate (default 5%)
- Payoff = $\max(K_j - S_{\text{stress}}, 0)$

**Key insight:** LP automatically selects cheapest protection mix across all maturities.

---

## Usage

### Basic (Single Expiry - Backward Compatible)

```python
params = {
    "hedge_interval": 30,
    "expiry_days": 90,  # Always 90-day options
}

lp_vix_adaptive_floor_strategy(portfolio, price, date, params, market)
```

### Multi-Expiry (New)

```python
params = {
    "hedge_interval": 30,
    "expiry_options": [14, 30, 60, 90],  # LP chooses optimal mix
}

lp_vix_adaptive_floor_strategy(portfolio, price, date, params, market)
```

### Advanced: VIX-Adaptive Expiry Menu

```python
# Vary available expiries based on VIX regime
vix = market.get_vix(current_date)

if vix < 20:
    # Calm: Offer long-dated only (cheap tail protection)
    expiry_options = [60, 90, 180]
elif vix < 40:
    # Elevated: Full menu
    expiry_options = [14, 30, 60, 90]
else:
    # Crisis: Short-dated only (avoid covering recovery)
    expiry_options = [7, 14, 21, 30]

params = {
    "hedge_interval": 7,
    "expiry_options": expiry_options,
}
```

---

## Pricing Model

### VIX-Based Premium Estimation

Each option in the chain is priced using:

```python
premium_pct = estimate_put_premium(
    strike=K,
    spot=S,
    days_to_expiry=T_days,
    vix=current_vix
)

premium_dollars = S * premium_pct
```

**Formula** (for OTM puts):
$$
\text{premium} = (1 - K/S) \times (\text{VIX}/100) \times \sqrt{T/365} \times 0.4
$$

**Calibration factor 0.4** ensures:
- 15% OTM @ VIX=20, 90d → 0.60% of notional
- 15% OTM @ VIX=50, 90d → 1.49% of notional

**Key property:** Shorter-dated options are cheaper per day but less total premium.

---

## Example: COVID Crash

### Scenario

- **Date**: March 10, 2020
- **Market**: SPX = 2,800 (down 15% from peak)
- **VIX**: 54 (crisis mode)
- **Portfolio**: $1M, beta=1.0

### Single Expiry (90-day)

**LP Decision:**
```
Option Chain (90-day expiry):
  $2,660 (5% OTM):  Premium = 2.1% → $1,176 per contract
  $2,520 (10% OTM): Premium = 2.5% → $1,400 per contract
  (etc.)

LP buys: 50 contracts @ $2,660 strike
Total cost: $58,800
Coverage: Through June 10 (entire recovery period)
```

**Problem**: Paying for 90 days of protection when crash lasted 30 days!

### Multi-Expiry (14, 30, 60, 90-day)

**LP Decision:**
```
Option Chain (24 options):
  14-day:
    $2,660 (5% OTM):  Premium = 0.7% → $392 per contract ✅ CHEAPEST
  30-day:
    $2,660 (5% OTM):  Premium = 1.0% → $560 per contract
  60-day:
    $2,660 (5% OTM):  Premium = 1.4% → $784 per contract
  90-day:
    $2,660 (5% OTM):  Premium = 2.1% → $1,176 per contract

LP buys: 150 contracts @ $2,660 strike, 14-day expiry
Total cost: $58,800
Coverage: Through March 24 (near market trough)
```

**Benefit**: Same cost, but options expire BEFORE recovery → can re-evaluate in 2 weeks!

---

## Expected Performance Improvements

### V-Shaped Crashes (COVID, 1987)

**Single expiry:** -5% to -7% drag (overpay for recovery coverage)
**Multi-expiry:** -1% to -2% drag (short-dated during crash)
**Improvement:** +3% to +5%

### Extended Volatility (GFC 2008-2009)

**Single expiry:** -3% to -4% drag
**Multi-expiry:** -2% to -3% drag (can roll short-dated)
**Improvement:** +1% to +2%

### False Alarms (VIX spike with no crash)

**Single expiry:** Locked into 90-day premium
**Multi-expiry:** 14-day expires quickly, minimal loss
**Improvement:** +0.5% to +1%

---

## Implementation Details

### Option Metadata Tracking

Each option in the chain now tracks:
```python
{
    'strike': 2660.0,
    'expiry_days': 14,
    'expiry_date': datetime(2020, 3, 24)
}
```

This allows portfolio to hold options with different expiries simultaneously.

### Verbose Output

```
[LP Hedge 2020-03-10]
  VIX: 54.0 | Regime: High | Alpha: 0.20 | TC: 5%
  Spot: $2800.00 | Stress: $2058.45 (-26.5%)
  Floor: 0.700 | V_target: $700,000 | V_unhedged: $612,350
  Gap G: $87,650 | Covered: $87,715 | Total Cost: $12,450
  Active positions: 3/24 options

  14-day options:
    $2660 (5% OTM): 112.00 contracts @ 0.70% premium
    $2520 (10% OTM): 45.00 contracts @ 0.85% premium

  30-day options:
    $2660 (5% OTM): 8.00 contracts @ 1.00% premium
```

**Interpretation:**
- LP chose mostly 14-day (cheapest)
- Small allocation to 30-day (hedge roll risk)
- No 60/90-day (too expensive during crisis)

---

## Testing

### Unit Tests

All existing tests pass (backward compatible):
```bash
uv run pytest tests/test_lp_strategy.py -v
# 11/11 passed ✅
```

### Integration Test

```python
# Compare single vs multi-expiry during COVID
params_single = {"expiry_days": 90}
params_multi = {"expiry_options": [14, 30, 60, 90]}

# Run both strategies on same period
# Expected: multi-expiry shows 3-5% improvement
```

---

## Notebook Updates

To use multi-expiry in simulations:

```python
# OLD (single expiry)
lp_params_covid = {
    "hedge_interval": 7,
    "expiry_days": 90,
    "verbose": True,
}

# NEW (multi-expiry)
lp_params_covid = {
    "hedge_interval": 7,
    "expiry_options": [14, 30, 60, 90],  # LP chooses optimal mix
    "verbose": True,
}

results_lp_covid = run_simulation(
    market_covid, portfolio_lp_covid,
    lp_vix_adaptive_floor_strategy, lp_params_covid
)
```

---

## Future Enhancements

### 1. Dynamic Expiry Menu

Vary available expiries by VIX regime:
- VIX < 20: [60, 90, 180]
- VIX 20-30: [30, 60, 90]
- VIX 30-50: [14, 30, 60]
- VIX > 50: [7, 14, 21]

### 2. Roll Management

Instead of clearing all options every rebalance:
- Keep unexpired options
- Only add new protection if needed
- Sell options that are no longer optimal

### 3. Calendar Spreads

Buy protective put ladders:
- 25% in 14-day
- 25% in 30-day
- 25% in 60-day
- 25% in 90-day

Provides continuous protection while managing roll costs.

---

## References

- **Option Pricing**: VIX-based premium estimation (see `estimate_put_premium()`)
- **LP Solver**: `solve_vix_adaptive_floor_lp()` in `vix_floor_lp.py`
- **Strategy**: `lp_vix_adaptive_floor_strategy()` in `strategies.py`

## Changelog

**2025-12-02**: Multi-expiry LP optimization implemented
- Added `expiry_options` parameter
- Expanded option chain from 6 → 24 options (6 strikes × 4 expiries)
- VIX-based premium estimation for each maturity
- Backward compatible with single-expiry mode
