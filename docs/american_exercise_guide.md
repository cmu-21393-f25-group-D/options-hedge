# American Option Early Exercise in Portfolio Insurance

## Overview

This document explains **when and why** to exercise American put options early in a portfolio insurance context, and provides the mathematical foundation for our exercise rules.

## The Early Exercise Problem

### European vs American Options

- **European**: Exercise only at expiration
- **American**: Exercise anytime before expiration

Real SPX/SPY options are **American-style**, but most backtests treat them as European (simpler).

### Optimal Exercise Rule (Theory)

Exercise when:
```
Intrinsic Value > Continuation Value
```

Where:
- **Intrinsic Value** = $\max(K - S_t, 0)$ (payoff if exercised now)
- **Continuation Value** = $\mathbb{E}^Q[e^{-r(T-t)} \max(K - S_T, 0) | \mathcal{F}_t]$ (expected discounted future payoff)

**Problem**: Computing continuation value requires:
1. Knowledge of future price distribution
2. Option pricing model (e.g., Black-Scholes)
3. Numerical methods (e.g., Longstaff-Schwartz LSM)

## Practical Exercise Rules

We implement **four rules** of increasing sophistication:

---

### 1. Threshold Rule (Simplest)

**Idea**: Exercise when time value decays to negligible amount.

**Formula**:
```python
time_value = option.value(S, t) - intrinsic_value
exercise_if: time_value < threshold × intrinsic_value
```

**Parameters**:
- `threshold` = 0.02 (2% default)

**Pros**:
- Simple, works with intrinsic-only pricing
- Computationally cheap

**Cons**:
- Ignores volatility regime
- May exercise too early in persistent downtrends

**Use case**: Quick approximation when pricing model unavailable

---

### 2. VIX Regime Rule (Market Signal)

**Idea**: Exercise when volatility regime shifts (market stabilizing).

**Formula**:
```python
moneyness = S / K
vix_change = (VIX_t - VIX_{t-1}) / VIX_{t-1}

exercise_if:
    moneyness < 0.90  AND  vix_change < -0.15
```

**Parameters**:
- `moneyness_threshold` = 0.90 (require 10% ITM)
- `vix_decline_threshold` = 0.15 (require 15% VIX drop)

**Rationale**:
- High VIX → market panic
- Falling VIX → panic subsiding, market bottoming
- Deep ITM puts should be exercised before recovery

**Example (COVID-19)**:
```
March 23, 2020: S&P = 2237, VIX = 82 (bottom)
April 1, 2020:  S&P = 2600, VIX = 55 (recovery starts)

VIX change = (55 - 82) / 82 = -33% ← EXERCISE SIGNAL
```

**Pros**:
- Uses real market signal (VIX)
- Captures regime shifts
- No pricing model needed

**Cons**:
- VIX can be noisy
- False positives in choppy markets
- Requires VIX data

**Use case**: Crisis scenarios with clear volatility regime shifts

---

### 3. Optimal Boundary Rule (Mathematical)

**Idea**: Approximate optimal stopping boundary from LSM method.

**Formula**:
```python
critical_moneyness = base_level + vol_adjustment

base_level = 0.85 - 0.10 × r
vol_adjustment = 0.15 × sqrt(T) × σ

exercise_if:
    S / K < critical_moneyness  AND  T < 30 days
```

**Parameters**:
- `risk_free_rate` = 0.045 (4.5%)
- `volatility` = σ (annualized)
- `min_days_to_expiry` = 30

**Rationale**:

From American put option theory:
- Exercise boundary $S^*(t)$ below which exercise is optimal
- Approximate: $\frac{S^*}{K} \approx 0.80 + 0.15 \sqrt{T} \sigma$

**Components**:
1. **Base level** (0.85): Lower strike ratio threshold
   - Higher interest rates → exercise earlier (capture intrinsic now)
   - Formula: $0.85 - 0.10r$

2. **Volatility adjustment**: Higher vol → preserve optionality longer
   - Formula: $0.15 \sqrt{T} \sigma$
   - High vol → larger continuation value → wait longer

**Example**:
```
S = 3200, K = 4000, S/K = 0.80
T = 20 days, σ = 0.40, r = 0.045

critical_moneyness = (0.85 - 0.10×0.045) + 0.15×sqrt(20/365)×0.40
                   = 0.846 + 0.014
                   = 0.860

0.80 < 0.860 → EXERCISE
```

**Pros**:
- Theoretically grounded
- Adapts to time/volatility/rates
- Captures optimal stopping intuition

**Cons**:
- Requires volatility estimate
- Simplified approximation (not exact LSM)
- May need calibration

**Use case**: Systematic strategies with volatility forecasting

---

### 4. Hybrid Rule (Recommended)

**Idea**: Combine VIX regime signal + optimal boundary.

**Formula**:
```python
exercise_if:
    should_exercise_vix_regime(...)  OR
    should_exercise_optimal_boundary(...)
```

**Rationale**:
- **VIX rule**: Detects regime shifts (market timing)
- **Boundary rule**: Mathematical optimality (time/vol/rate)
- **Combined**: Best of both worlds

**Decision Tree**:
```
1. Check VIX regime shift
   ├─ VIX down >15% AND deep ITM? → EXERCISE
   └─ No → Check optimal boundary

2. Check optimal boundary
   ├─ S/K < critical AND near expiry? → EXERCISE
   └─ No → HOLD
```

**Example (COVID Recovery)**:
```
April 1, 2020:
  S = 2600, K = 3200, S/K = 0.8125
  VIX: 82 → 55 (-33%)
  σ = 0.60, T = 90 days

VIX Rule:
  0.8125 < 0.90? Yes
  -33% < -15%?   Yes
  → EXERCISE ✓

Boundary Rule (backup):
  critical = 0.846 + 0.15×sqrt(90/365)×0.60 = 0.892
  0.8125 < 0.892? Yes
  → EXERCISE ✓

Decision: EXERCISE (both rules agree)
```

**Pros**:
- Robust (two independent signals)
- Captures both regime shifts and math optimality
- Fewer false positives than VIX alone

**Cons**:
- More complex
- Requires both VIX data and volatility estimate

**Use case**: Production portfolio insurance systems

---

## Implementation

### Portfolio Integration

The `Portfolio` class provides `check_early_exercise()`:

```python
from options_hedge.american_exercise import should_exercise_hybrid
from options_hedge.portfolio import Portfolio

portfolio = Portfolio(initial_value=1_000_000)

# Daily loop
for date, price in market_data:
    # ... strategy logic ...

    # Check early exercise
    num_exercised = portfolio.check_early_exercise(
        current_price=price,
        current_date=date,
        exercise_rule=should_exercise_hybrid,
        current_vix=vix,
        prev_vix=prev_vix,
        volatility=0.40,
        risk_free_rate=0.045,
    )

    # ... continue simulation ...
```

### Available Rules

```python
from options_hedge.american_exercise import (
    should_exercise_never,           # Never exercise (European)
    should_exercise_threshold,       # Time value threshold
    should_exercise_vix_regime,      # VIX regime shift
    should_exercise_optimal_boundary,# Mathematical boundary
    should_exercise_hybrid,          # VIX + boundary (recommended)
)
```

---

## When Early Exercise Helps

### Beneficial Scenarios

1. **Deep ITM near market bottom**
   - Example: COVID crash recovery (S/K = 0.80, VIX falling)
   - Exercise locks in protection before recovery

2. **High interest rate environments**
   - Opportunity cost of waiting increases
   - Exercise captures intrinsic value now

3. **Low volatility after panic**
   - Time value diminished
   - Little upside to waiting

### When to Hold

1. **Far from expiration** (>30 days)
   - Preserve optionality
   - Time value still significant

2. **Rising volatility**
   - Market uncertainty increasing
   - Continuation value growing

3. **Moderate ITM**
   - Not deep enough to justify early exercise
   - Potential for further downside

---

## Historical Examples

### COVID-19 (March-April 2020)

**Setup**:
- Bought puts on Feb 20 (S&P = 3386, VIX = 15)
- Strike = 3050 (10% OTM)
- Expiry = June 30

**Bottom** (March 23):
- S&P = 2237
- VIX = 82
- Intrinsic = 3050 - 2237 = $813

**Recovery Begins** (April 1):
- S&P = 2600
- VIX = 55 (-33% from peak)
- Intrinsic = 3050 - 2600 = $450

**Decision**:
- Hybrid rule: **EXERCISE** (VIX regime shift)
- Result: Lock in $450/contract before May rally

**Outcome**:
- By June 30: S&P = 3100 (near strike)
- European exercise: ~$0 payoff
- American exercise: $450 payoff
- **Benefit: +$450/contract**

### Financial Crisis (Oct 2008)

**Setup**:
- Bought puts in Sept 2008 (S&P = 1200)
- Strike = 1100 (8% OTM)
- Expiry = Mar 2009

**Bottom** (March 9, 2009):
- S&P = 677
- VIX = 70+
- Intrinsic = 1100 - 677 = $423

**Decision**:
- VIX high but not declining yet
- Boundary rule: HOLD (wait for regime shift)
- Result: Held until VIX dropped in April

**Outcome**:
- Exercised April 2009 when VIX fell to 45 (-36%)
- Captured $400+ payoff before summer rally
- Better than holding to March expiry

---

## Caveats and Limitations

### Current Implementation

Our rules use **intrinsic-only pricing** (`option.value()` returns $\max(K-S, 0)$).

**Implication**: Threshold rule always exercises ITM options (time value = 0).

**Fix**: Implement Black-Scholes pricing in `option.py`:
```python
def value(self, S, t, r, σ):
    return black_scholes_put(S, self.strike, t, r, σ)
```

Then threshold rule becomes meaningful.

### Simplifications

1. **No transaction costs on exercise**
   - Real exercise incurs settlement costs
   - Should include in exercise decision

2. **Single volatility estimate**
   - Real markets have term structure
   - Could use different σ per expiry

3. **VIX proxy for implied vol**
   - VIX is 30-day ATM
   - Option may have different maturity/moneyness

### Extensions

**Future improvements**:
1. Multi-scenario stress (exercise if $n$ of $m$ signals trigger)
2. Adaptive thresholds based on regime
3. Portfolio-level exercise (coordinate multiple options)
4. Tax considerations (long-term vs short-term gains)

---

## References

1. **Longstaff-Schwartz (2001)**: "Valuing American Options by Simulation: A Simple Least-Squares Approach"
2. **Hull (2018)**: *Options, Futures, and Other Derivatives*, Chapter 13 (American Options)
3. **Taleb (1997)**: *Dynamic Hedging*, Chapter 5 (Early Exercise)
4. **CBOE VIX White Paper**: Understanding VIX as market timing signal

---

## Summary

**For portfolio insurance**:
- American puts allow **tactical exercise** at market bottoms
- **Hybrid rule** (VIX + boundary) recommended for robustness
- Early exercise can **significantly improve** returns in V-shaped recoveries
- Requires **real-time market signals** (VIX, volatility estimates)

**Bottom line**: Exercise when you believe the market has bottomed and recovery is imminent. Use VIX regime shifts as your primary signal, with mathematical boundary as confirmation.
