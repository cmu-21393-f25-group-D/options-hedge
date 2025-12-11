# Mathematical Formulations: Linear Programming for Portfolio Insurance

**Authors:** Akhil Karra, Zoe Xu, Vivaan Shroff
**Course:** CMU 21-393 (Operations Research II)
**Last Updated:** December 11, 2025

---

## Executive Summary

This document provides mathematical formulations of two linear programming approaches for portfolio hedging using S&P 500 (SPX) put options. Both methods minimize premium costs while providing downside protection, but differ fundamentally in their constraint structures and protection guarantees.

**Important Limitations:**
- These are **educational models** demonstrating OR techniques, not production-ready investment tools
- Black-Scholes option pricing with simplified assumptions
- Scenario-based approaches use historical volatility (not forward-looking)
- Transaction costs modeled as simple proportional to premium
- No consideration of early exercise, dividend adjustments, or discrete rebalancing frictions

---

## 1. VIX-Ladder LP: Adaptive Budgeting with Strike Diversification

### 1.1 Mathematical Formulation

**Decision Variables:**
$$x_j \in \mathbb{R}_+ \quad \forall j \in \mathcal{J}$$

where $x_j$ represents the number of put option contracts to purchase for strike $K_j$.

**Objective Function:**
$$\min \sum_{j \in \mathcal{J}} c_j (1 + \tau) x_j$$

where:
- $c_j$ = premium cost per contract for option $j$
- $\tau$ = transaction cost rate (bid-ask spread, typically 1-5%)
- $\mathcal{J}$ = set of available put options

**Constraints:**

1. **VIX-Responsive Budget Constraint:**
$$\sum_{j \in \mathcal{J}} c_j (1 + \tau) x_j \leq B(V_0, \text{VIX}, \beta)$$

where the adaptive budget is:
$$B(V_0, \text{VIX}, \beta) = V_0 \cdot b \cdot \left(\frac{\text{VIX}}{20}\right) \cdot \max(1.0, \beta)$$

- $V_0$ = current portfolio value
- $b$ = base budget multiplier (typically 1% = 0.01)
- VIX = CBOE Volatility Index (market fear gauge)
- $\beta$ = portfolio systematic risk vs. S&P 500

**Intuition:** When VIX = 20 (historical average) and β = 1.0, budget = 1% of portfolio. Budget scales linearly with volatility and systematic risk.

2. **Strike Ladder Diversification Constraints:**

Define strike rungs based on out-of-the-money (OTM) percentage:
$$\text{OTM}_j = \frac{S_0 - K_j}{S_0}$$

For each rung $r \in \{1, 2, 3, 4\}$ with bounds $[\text{OTM}^r_{\min}, \text{OTM}^r_{\max}]$:
$$\sum_{j : \text{OTM}_j \in [\text{OTM}^r_{\min}, \text{OTM}^r_{\max}]} c_j (1 + \tau) x_j \geq \phi_r \cdot B(V_0, \text{VIX}, \beta)$$

**Default ladder allocations:**
- Rung 1: 5-15% OTM → $\phi_1 = 0.05$ (5% of budget)
- Rung 2: 15-25% OTM → $\phi_2 = 0.15$ (15% of budget)
- Rung 3: 25-40% OTM → $\phi_3 = 0.30$ (30% of budget)
- Rung 4: 40%+ OTM → $\phi_4 = 0.50$ (50% of budget)

**Rationale:** Diversifies protection across multiple crash scenarios. Deep OTM puts (40%+) provide catastrophic protection at low cost.

3. **Non-negativity:**
$$x_j \geq 0 \quad \forall j \in \mathcal{J}$$

### 1.2 Implementation Details

**Option Universe Construction:**
- Query WRDS OptionMetrics for available SPX puts
- Filter: expiry within target window (typically 90 days)
- Strikes: 5% OTM to 80% OTM in 5% increments
- Premium: Use mid-price = (best_bid + best_offer) / 2

**LP Solver:**
```python
import gurobipy as gp

# Create model
m = gp.Model("vix_ladder_lp")
m.setParam('OutputFlag', 0)

# Decision variables
x = m.addVars(len(options), lb=0.0, name="x")

# Objective: minimize total cost
m.setObjective(
    gp.quicksum(opt.premium * (1 + tau) * x[j] for j, opt in enumerate(options)),
    gp.GRB.MINIMIZE
)

# Budget constraint
m.addConstr(
    gp.quicksum(opt.premium * (1 + tau) * x[j] for j, opt in enumerate(options))
    <= budget
)

# Ladder constraints (one per rung)
for rung_idx, (otm_min, otm_max, frac) in enumerate(ladder_allocations):
    rung_opts = [j for j, opt in enumerate(options)
                 if otm_min <= compute_otm(opt.strike, S0) < otm_max]
    if rung_opts:
        m.addConstr(
            gp.quicksum(options[j].premium * (1 + tau) * x[j] for j in rung_opts)
            >= frac * budget
        )

# Solve
m.optimize()
```

### 1.3 Strengths

1. Budget automatically scales with VIX → hedges more during volatile periods
2. Ladder constraints ensure diversification across crash magnitudes
3. Small LP (typically 15-20 variables, 5-6 constraints)
4. VIX/20 normalization based on historical average

### 1.4 Current Limitations & Known Issues

**Mathematical Simplifications:**

1. Unlike Fixed Floor LP, we don't explicitly constrain maximum drawdown in the formulation. Theoretically, the VIX-adaptive budgeting and ladder diversification should provide graduated protection, but realistically the formulation is underconstrained—there's no mathematical guarantee on worst-case losses.
2. The 5%/15%/30%/50% split is heuristic, not optimized
3. Assumes linear relationship between VIX and hedge needs (empirically questionable)
4. Budget set at hedge initiation, not dynamically adjusted intra-period

**Pricing Assumptions:**

1. **Black-Scholes Framework:** Assumes continuous trading and frictionless markets in the option pricing itself (though we separately model transaction costs via (1 + τ) in the LP)
2. **Single Vol Surface:** Uses implied volatility from options, but surface may be stale or inconsistent
3. **No Skew Modeling:** Ignores volatility smile/skew (OTM puts typically more expensive than BS predicts)

**Empirical Performance:**

- **Marginal Improvement:** With 1% budget, only 0.2-0.5% better than unhedged in backtest
- **Premium Drag:** Monthly rebalancing with 1% budget ≈ 12% annual drag on returns
- **Not Crash-Proof:** Still lost 9-10% in Dot-Com, 20% in GFC (vs 10%, 21% unhedged)

---

## 2. Fixed Floor LP: Guaranteed Loss Limit

### 2.1 Mathematical Formulation

**Decision Variables:**
$$x_j \in \mathbb{R}_+ \quad \forall j \in \mathcal{J}$$

**Objective Function:**
$$\min \sum_{j \in \mathcal{J}} c_j (1 + \tau) x_j$$

**Constraints:**

1. **Floor Guarantee (Scenario-Based):**

For each scenario $s \in \mathcal{S}$ (crash, mild, up):
$$V_0 \cdot (1 + r_s) + \sum_{j \in \mathcal{J}} x_j \cdot \max(K_j - S_0(1 + r_s), 0) \geq (1 - L) \cdot V_0$$

where:
- $r_s$ = portfolio return in scenario $s$
- $L$ = maximum acceptable loss (e.g., 0.20 = 20% max loss)
- $S_0(1 + r_s)$ = spot price after scenario $s$ (assuming perfect correlation)

**Scenario Definition:**
$$\mathcal{S} = \{\text{crash}, \text{mild}, \text{up}\}$$

Example calibration (based on historical volatility $\sigma_{\text{daily}}$):
- Crash: $r_{\text{crash}} = -2\sigma_{\text{daily}} \sqrt{252}$ (2-sigma downside, annualized)
- Mild: $r_{\text{mild}} = -1\sigma_{\text{daily}} \sqrt{252}$ (1-sigma downside)
- Up: $r_{\text{up}} = +1\sigma_{\text{daily}} \sqrt{252}$ (1-sigma upside)

2. **Non-negativity:**
$$x_j \geq 0 \quad \forall j \in \mathcal{J}$$

### 2.2 Key Differences from VIX-Ladder

| Aspect | VIX-Ladder LP | Fixed Floor LP |
|--------|---------------|----------------|
| **Objective** | Minimize cost within budget | Minimize cost subject to floor |
| **Protection Type** | Adaptive, no guarantee | Deterministic, provable floor |
| **Constraints** | Budget + ladder diversification | Scenario-based floor |
| **Budget** | Exogenous (VIX-based) | Endogenous (LP determines) |
| **Complexity** | $O(n + k)$ constraints ($k$ rungs) | $O(n + \|\mathcal{S}\|)$ constraints |
| **Use Case** | Volatility management | Regulatory/risk limits |

### 2.3 Strengths

1. **Provable Floor:** Mathematically guarantees $V_T \geq (1 - L) \cdot V_0$ under scenarios
2. **Cost-Optimal:** Finds cheapest hedge meeting floor constraint
3. **Scenario Flexibility:** Can test extreme scenarios beyond historical

### 2.4 Current Limitations & Known Issues

**Mathematical Weaknesses:**
1. **Scenario Dependence:** Floor only guaranteed for tested scenarios (real crash could be worse)
2. **Perfect Correlation Assumption:** Assumes portfolio moves exactly with S&P 500 (good for our simulations, needs tweaking for different portfolios)
3. **Single-Period:** No consideration of dynamic trading or path-dependence
4. **Discrete Scenarios:** Continuous distribution approximated by 3-5 points

**Empirical Findings:**
- **Not Hedging in Practice:** LP often finds trivial solution $x_j = 0$ (no hedging)
- **Floor Never Binding:** In backtests, market never dropped enough to trigger floor
- **Scenario Miscalibration:** Historical volatility underestimates tail risk

**Why the Floor Constraint Doesn't Bind:**

The floor constraint is:
$$V_0 \cdot (1 + r_{\text{crash}}) + \sum_j x_j \cdot \max(K_j - S_0(1 + r_{\text{crash}}), 0) \geq 0.8 V_0$$

For 20% floor with $r_{\text{crash}} = -2\sigma \sqrt{252}$:
- If $\sigma_{\text{daily}} = 0.015$ (1.5%), then $r_{\text{crash}} \approx -0.48$ (48% loss)
- This is a **very extreme scenario** (4.5 sigma crash if annualized vol = 24%)
- In Dot-Com (2000-2003), actual loss was only ~10%
- In GFC (2008-2009), actual loss was ~21%

**Result:** LP finds that even without hedging, portfolio won't hit floor in tested scenarios → optimal solution is $x_j = 0$ (don't hedge).

### 2.5 Proposed Improvements

**Immediate Fixes:**
1. **More Realistic Scenarios:** Use quantile-based scenarios from empirical distribution
   - 95th percentile: -25% (1-year horizon from rolling window)
   - 99th percentile: -40% (worst year in sample)
2. **Tighter Floor:** Reduce $L$ to 10-15% (more binding constraint)
3. **Robustness Constraint:** Add worst-case scenario or CVaR constraint

---

## 3. Baseline Strategies (Non-LP)

For comparison, we also implement simpler strategies:

### 3.1 Quarterly Protective Put

**Rule:** Every 90 days, buy 3-month ATM put covering full portfolio

**Cost:** Approximately 2-3% quarterly (8-12% annual drag)

**Protection:** Complete downside protection until next rebalancing, but expensive

### 3.2 Conditional Hedging

**Rule:** Only hedge when:
1. Cumulative drawdown > threshold (e.g., -10%)
2. **OR** volatility spike > multiplier × historical vol (e.g., 2× baseline)

**Cost:** Variable, typically 0-5% annually depending on triggers

**Protection:** Reactive, not preventive (already lost $ when triggered)

---

## 4. Empirical Validation: 26 Years of Real Data

### 4.1 Data Sources

**WRDS OptionMetrics (1996-2025):**
- 22.4 million SPX option observations
- Fields: strike_price, best_bid, best_offer, impl_volatility, delta, gamma, vega
- Daily frequency, end-of-day quotes

**WRDS CRSP (1999-2025):**
- S&P 500 daily returns
- Risk-free rate (3-month Treasury)

**FRED (Federal Reserve Economic Data):**
- VIX Index (daily)
- 3-month Treasury rates (daily)

### 4.2 Backtest Methodology

**Test Periods:**
1. **Dot-Com Bubble (1999-2003):** Slow, multi-year decline (-49% peak-to-trough)
2. **Global Financial Crisis (2007-2009):** Fast, severe crash (-57% peak-to-trough)
3. **COVID-19 Crash (2019-2021):** Fastest crash in history (-34% in 1 month)

**Simulation Framework:**
- Initial portfolio: $1,000,000
- Rebalancing: 7 days (weekly) or 30 days (monthly)
- Transaction costs: 1% of premium (institutional rates)
- Option universe: Refresh daily from WRDS
- Position sizing: Full portfolio hedging (β = 1.0)

### 4.3 Key Results (Summary)

**VIX-Ladder LP (1% budget, monthly rebalancing):**
- Dot-Com: -9.4% (vs -9.6% unhedged) ✅ Marginal improvement
- GFC: -20.3% (vs -20.5% unhedged) ✅ Marginal improvement
- COVID: +54.4% (vs +56.4% unhedged) ✅ 98% upside capture

**Fixed Floor LP (20% floor):**
- Dot-Com: -9.6% (identical to unhedged) ❌ Not hedging
- GFC: -20.5% (identical to unhedged) ❌ Not hedging
- COVID: +56.4% (identical to unhedged) ❌ Not hedging

**Interpretation:**
- VIX-Ladder provides **modest, consistent protection** at low cost
- Fixed Floor **does not hedge** due to scenario miscalibration
- Both strategies suffer from **premium drag** (reduces upside in bull markets)

### 4.4 Honest Assessment

**What Works:**
- LP framework successfully minimizes costs given constraints
- VIX-adaptive budgeting responds to market conditions
- Ladder diversification creates graduated protection

**What Doesn't Work:**
- **Not crash-proof:** Still lost 20% in GFC (vs 21% unhedged)
- **Marginal benefits:** Only 0.2% improvement is not economically significant
- **Premium drag:** ~1% annual cost reduces long-term compound returns
- **Fixed Floor LP broken:** Scenarios too extreme, doesn't hedge in practice

**Why Could the Performance Be Modest?**
We have a few ideas:
1. **Budget Constraint Binds:** 1% budget insufficient for strong protection
2. **Strikes Too Cheap:** Deep OTM puts offer little actual downside protection
3. **Rebalancing Frequency:** Monthly rebalancing leaves gaps in protection
4. **Transaction Costs:** 1% costs reduce net benefit of hedging
