# LP Formulation Analysis: VIX-Adaptive Floor Strategy

## Executive Summary

This document analyzes the Linear Programming (LP) formulation for the VIX-Adaptive Floor options hedging strategy and proposes improvements for OR II class project.

**TL;DR**: The current LP formulation is mathematically correct but economically flawed. It buys cheap, ineffective options that expire worthless. We've implemented a risk-adjusted objective function to address this.

## Current LP Formulation

### Decision Variables
- `x_j ≥ 0`: Quantity of option j to purchase
- Options indexed by strike K_j and expiry T

### Objective Function
```
minimize: Σ(c_j * x_j)
```
where `c_j` = premium cost of option j

### Constraints
```
Σ(a_j * x_j) ≥ G     (coverage constraint)
x_j ≥ 0              (non-negativity)
```

where:
- `a_j` = payoff of option j at stress price: `max(K_j - S_stress, 0)`
- `G` = Gap = `max(V_target - V_unhedged, 0)`
- `V_target` = `r_floor * V_portfolio`
- `V_unhedged` = portfolio value at stress scenario
- `S_stress` = `S_0 * exp(z_α * σ * √T)` where `z_α` is the α-quantile

## Problems Identified

### Problem 1: Single-Scenario Stress Price ❌

**Issue**: LP assumes crash happens EXACTLY at option expiry (e.g., 90 days)

**Example (GFC Jan 2008)**:
- LP expects: S&P drops to $1107 (-23.5%) in 90 days  
- Reality: S&P was $1370 (-5.3%) in 90 days
- **Options expired worthless** (crash came later in Oct 2008)

**Impact**: 
- Bought protection for timing that didn't match reality
- $1,392 in premiums wasted
- Portfolio underperformed unhedged by $29K (-3%)

### Problem 2: Pure Cost Minimization Without Quality Penalty ❌

**Issue**: LP minimizes ONLY premium cost, ignoring protection quality

**LP Behavior**:
- Prefers many cheap deep OTM puts (low premium, low delta, low probability)
- Avoids expensive ATM puts (high premium, high delta, effective protection)

**Example**:
- 100 contracts at 30% OTM ($2 each = $200 total, delta=-0.15)
- vs 20 contracts at 10% OTM ($12 each = $240 total, delta=-0.45)
- **LP chooses first option** (saves $40) even though second is better protection

### Problem 3: Gap G = $0 in Many Scenarios ❌

**Issue**: With current parameters, unhedged value often exceeds floor target

**Diagnostic (Jan 2008, VIX=23.2, α=0.05)**:
```
r_floor: 0.826 (82.6% floor)
S_stress: $1197 (-17.3%)
V_unhedged at stress: $827,380
V_target: $826,400
Gap G: $0 ← NO GAP!
```

**Result**: LP buys **zero options** because no protection needed mathematically

**Why this happens**:
- α=0.05 (2-sigma) expects -17% to -25% crash
- Floor targets 80-85% of portfolio  
- If crash is only -17%, unhedged portfolio at $827K already above $826K target
- Mathematically correct, but economically wrong (ignores path dependency, timing)

### Problem 4: No Path Dependency ❌

**Issue**: LP assumes European-style terminal payoff only

**Reality**: 
- American puts can exercise early if profitable
- Volatility path matters for option value
- LP model: `payoff = max(K - S_final, 0)`
- Reality: Options gain value along the path down

## Proposed Solutions

### Solution 1: Multi-Scenario Robust Optimization ⭐⭐⭐

**Formulation**:
```
Decision variables: x_j ≥ 0
Objective: minimize Σ(c_j * x_j)
Constraints: Σ(a_j^k * x_j) ≥ G_k  ∀k ∈ scenarios
```

where scenarios include:
- Immediate crash (-20% in 30 days)
- Gradual decline (-30% over 90 days)  
- Delayed crash (flat 60 days, then -25%)
- No crash (sideways)

**Benefits**:
- ✅ Forces options to work across MULTIPLE paths
- ✅ Avoids timing-specific protection
- ✅ More robust to reality vs model mismatch

**Drawbacks**:
- More constraints → more expensive LP (still polynomial time)
- Need to define scenario probabilities

**Implementation Complexity**: Medium (add K scenarios → K constraints)

### Solution 2: Risk-Adjusted Cost Minimization ⭐⭐⭐⭐⭐ (IMPLEMENTED)

**Formulation**:
```
Decision variables: 
  x_j ≥ 0 (option quantities)
  s ≥ 0   (slack/shortfall)

Objective: minimize Σ(c_j * x_j) + λ * s

Constraint: Σ(a_j * x_j) + s ≥ G
```

where:
- `s` = shortfall (uncovered gap)
- `λ` = risk penalty weight (e.g., λ=10 means $1 shortfall costs $10)

**Interpretation**:
- λ = 0: Pure cost minimization (current broken behavior)
- λ = 10: Willing to pay $10 in premiums to avoid $1 of uncovered risk
- λ → ∞: Must cover gap completely (hard constraint)

**Benefits**:
- ✅ Easy to implement (add 1 variable, change objective)
- ✅ Preserves LP structure (same solver, same complexity)
- ✅ Intuitive parameter (balance cost vs protection)
- ✅ Tunable via grid search

**Expected Behavior**:
- Small λ: May leave gap partially uncovered to save cost
- Large λ: Over-protects to avoid penalty
- Optimal λ: Balances cost vs quality

**Implementation Complexity**: LOW ✅ (Already implemented in code)

### Solution 3: CVaR-Based Protection ⭐⭐⭐

**Formulation**:
```
minimize: Σ(c_j * x_j)
subject to: CVaR_α[loss] ≤ max_loss
```

where CVaR = average loss in worst α% scenarios

**Benefits**:
- ✅ Protects against tail average, not just threshold
- ✅ More sophisticated risk measure

**Drawbacks**:
- Requires scenario generation
- More complex objective

**Implementation Complexity**: High

### Solution 4: Delta-Weighted Objective ⭐⭐

**Formulation**:
```
minimize: Σ(c_j / delta_j * x_j)
```

where delta_j = option sensitivity to underlying price

**Benefits**:
- ✅ Prefers high-delta options (better protection)
- ✅ Simple to implement

**Drawbacks**:
- Requires computing deltas
- Doesn't address timing/path issues

**Implementation Complexity**: Medium

## Recommendation for OR II Project

### Primary Recommendation: Solution 2 (Risk-Adjusted Cost) ✅

**Why this is best for OR II**:

1. **Pedagogical Value**: 
   - Shows how objective function design affects solution quality
   - Demonstrates soft vs hard constraints
   - Explores Pareto frontier (cost vs coverage)

2. **Technical Merit**:
   - Still a Linear Program (preserves theoretical properties)
   - Easy sensitivity analysis (vary λ)
   - Clear economic interpretation

3. **Practical Impact**:
   - Addresses the core problem (cheap ineffective options)
   - Tunable via grid search
   - Works with existing infrastructure

### Implementation Steps

1. ✅ **Add slack variable** to LP formulation
2. ✅ **Modify objective** to include risk penalty
3. ✅ **Update constraint** to allow shortfall
4. **Grid search λ** ∈ {0, 1, 2, 5, 10, 20, 50, 100}
5. **Compare out-of-sample** performance across regimes
6. **Analyze trade-off** curve: cost vs protection quality

### Expected Results

**With λ=0 (current)**:
- Buys cheap deep OTM puts  
- Low cost ($1-2K)
- Poor protection
- Underperforms unhedged by -3%

**With λ=10-20 (proposed)**:
- Buys moderate OTM puts (10-20% strikes)
- Higher cost ($3-5K)
- Better protection
- **Expected**: Outperforms unhedged by +2-5% in crisis

**With λ=100+ (over-protective)**:
- Buys ATM/near-money puts
- Very high cost ($10K+)
- Excellent protection but not cost-effective
- May underperform due to drag

### Metrics to Report

1. **Out-of-sample performance** across GFC, COVID, Dot-com
2. **Sharpe ratio** improvement vs unhedged
3. **Max drawdown** reduction
4. **Cost-benefit ratio**: (protection value) / (premium paid)
5. **Pareto frontier**: Plot cost vs protection for different λ

## Alternative: Multi-Scenario Approach (Solution 1)

If more complexity is desired for OR II project:

### Scenario Generation

**Baseline scenarios** (K=4):
1. Fast crash: -25% in 30 days
2. Slow grind: -35% over 90 days
3. Delayed shock: Flat 60d, then -20%
4. Sideways: ±5% over 90 days

**Advanced** (K=10-20): Monte Carlo paths from GBM

### Formulation
```
minimize: Σ(c_j * x_j)
subject to: Σ(a_j^k * x_j) ≥ G_k  ∀k=1..K
            x_j ≥ 0
```

**Complexity**: O(n*K) where n=options, K=scenarios

## Theoretical Analysis

### Why Current LP Fails

The LP is solving a **surrogate problem**:
- **True objective**: Maximize terminal wealth across all possible paths
- **LP objective**: Minimize cost to reach floor in ONE scenario

This is a **model-risk** problem:
- Reality ≠ single lognormal shock
- Crashes have fat tails, path dependency, regime changes
- LP optimizes for model, not reality

### Correct Framing

Options hedging is fundamentally a **stochastic program**:
```
max E[U(W_T)]  subject to  E[loss | crisis] ≤ threshold
```

where U = utility function, W_T = terminal wealth

Our LP is a **deterministic approximation** via:
1. Single scenario (α-quantile)
2. Linear objective (ignores risk aversion)
3. Terminal payoff (ignores path)

**Risk-adjusted LP** moves toward correct formulation by penalizing shortfall.

## Conclusion

The current LP formulation demonstrates a classic OR pitfall: **optimizing the wrong objective**. The model is mathematically correct but economically wrong.

**For OR II project**, implementing **Solution 2 (Risk-Adjusted Cost)** provides:
- ✅ Clear problem statement
- ✅ Theoretical justification  
- ✅ Empirical testing framework
- ✅ Sensitivity analysis opportunities
- ✅ Real-world impact

**Key insight**: Sometimes the "optimal" solution to a model is suboptimal in reality. Model formulation matters more than solution algorithm.

## References

- Rockafellar & Uryasev (2000): "Optimization of CVaR"
- Ben-Tal & Nemirovski (2002): "Robust Optimization"
- Hull (2018): "Options, Futures, and Other Derivatives" (Ch. 19: Greeks)

---

**File**: `docs/LP_FORMULATION_ANALYSIS.md`  
**Date**: December 2, 2025  
**Course**: OR II  
**Topic**: Linear Programming, Portfolio Optimization, Financial Engineering
