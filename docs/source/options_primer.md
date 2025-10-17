# Put Options Primer

This primer provides essential background on put options and how they're used for portfolio protection. Understanding these concepts is crucial for working with the optimization models in this project.

## What is a Put Option?

A **put option** is a financial contract that gives the buyer the **right, but not the obligation**, to sell an underlying asset at a predetermined price on or before a specific date.

### Key Components

- **Underlying asset**: The security the option contract is based on (e.g., S&P 500 index)
- **Strike price (K)**: The price at which you have the right to sell the underlying asset
- **Expiration date**: The last day the option can be exercised
- **Premium (C)**: The upfront cost to purchase the option contract
- **Contract size**: Number of shares covered by one contract (typically 100 for equity options)

### Contract Parties

- **Buyer (holder)**: Pays the premium and gets the right to sell at the strike price
- **Seller (writer)**: Receives the premium and is obligated to buy at the strike price if exercised

## Option Moneyness

The relationship between the strike price and current market price determines the option's "moneyness":

- **In-the-money (ITM)**: Strike price > Current market price
  - The option has intrinsic value
  - Example: S&P at 4,000, put strike at 4,200

- **At-the-money (ATM)**: Strike price ≈ Current market price
  - The option has minimal intrinsic value, mostly time value
  - Example: S&P at 4,000, put strike at 4,000

- **Out-of-the-money (OTM)**: Strike price < Current market price
  - The option has no intrinsic value, only time value
  - Example: S&P at 4,000, put strike at 3,600

### Value Components

An option's premium consists of two parts:

- **Intrinsic value**: `max(K - S, 0)` where S is the current market price
- **Time value**: Premium - Intrinsic value (represents uncertainty and time remaining)

## How Put Options Provide Protection

### The Insurance Analogy

A put option works like insurance for your portfolio:

1. **Pay premium upfront**: You buy the option contract
2. **Set your "deductible"**: The strike price determines your protection level
3. **Claim if needed**: Exercise the option if the market crashes below the strike
4. **Premium is sunk cost**: If the market rises, you let the option expire worthless

### Protective Put Example

**Setup:**

- Portfolio value: $1,000,000 in stocks
- Current S&P 500 level: 4,500
- Buy put option with strike: 4,050 (10% below current level)
- Premium paid: $30,000
- Expiration: 1 year

#### Scenario 1: Market crashes 30% to 3,150

- Stock portfolio value: $700,000
- Put option payoff per contract: $(4,050 - 3,150) = $900$
- Number of contracts: $\frac{\$1,000,000}{4,500 \times 100} \approx 2.22$ (rounded down to 2 contracts for whole contracts)
- Total payoff: $900 \times 2 = \$1,800$
- The put offsets most of the losses below the 4,050 level

#### Scenario 2: Market rises 20% to 5,400

- Stock portfolio value: $1,200,000
- Put option payoff: $0 (expires worthless)
- Net cost: $30,000 premium
- You still capture the upside, minus the insurance cost

#### Scenario 3: Market stays flat at 4,500

- Stock portfolio value: $1,000,000
- Put option payoff: $0
- Net cost: $30,000 premium
- This is the cost of protection you didn't need to use

## Portfolio Beta and Hedging Requirements

### What is Beta?

**Beta (β)** measures how much a portfolio moves relative to the market (typically the S&P 500):

- **β = 1.0**: Portfolio moves in lockstep with the market
  - A 10% market decline → 10% portfolio decline

- **β > 1.0**: Portfolio is more volatile than the market
  - Example: β = 1.5 means a 10% market decline → 15% portfolio decline

- **β < 1.0**: Portfolio is less volatile than the market
  - Example: β = 0.7 means a 10% market decline → 7% portfolio decline

### Why Beta Matters for Hedging

Since put options are based on the S&P 500 index, but your portfolio may not perfectly track the index, you need to adjust the number of contracts based on beta.

**Number of put contracts needed:**

$$
N_{\text{puts}} = \frac{\text{Portfolio Value}}{\text{Index Value} \times \text{Contract Multiplier}} \times \beta
$$

Where:

- Portfolio Value = Total dollar value of your portfolio
- Index Value = Current S&P 500 level
- Contract Multiplier = 100 (standard for S&P 500 index options)
- β = Portfolio beta relative to S&P 500

### Beta Hedging Examples

#### Example 1: Portfolio matches the market (β = 1.0)

- Portfolio value: $1,000,000
- S&P 500 level: 4,500
- Beta: 1.0

$$
N_{\text{puts}} = \frac{1,000,000}{4,500 \times 100} \times 1.0 = 2.22 \approx 2 \text{ contracts}
$$

#### Example 2: Aggressive growth portfolio (β = 1.5)

- Portfolio value: $1,000,000
- S&P 500 level: 4,500
- Beta: 1.5 (portfolio is 50% more volatile)

$$
N_{\text{puts}} = \frac{1,000,000}{4,500 \times 100} \times 1.5 = 3.33 \approx 3 \text{ contracts}
$$

You need more puts because your portfolio drops faster than the market.

#### Example 3: Conservative portfolio (β = 0.6)

- Portfolio value: $1,000,000
- S&P 500 level: 4,500
- Beta: 0.6 (portfolio is 40% less volatile)

$$
N_{\text{puts}} = \frac{1,000,000}{4,500 \times 100} \times 0.6 = 1.33 \approx 1 \text{ contract}
$$

You need fewer puts because your portfolio drops slower than the market.

### Implications for Portfolio Insurance

The beta-adjusted hedging approach means:

1. **High-beta portfolios** (aggressive, growth-focused):
   - Need more put contracts
   - Higher insurance costs
   - But also have greater downside risk to protect against

2. **Low-beta portfolios** (conservative, value-focused):
   - Need fewer put contracts
   - Lower insurance costs
   - Less downside risk to begin with

3. **Diversified portfolios** (β ≈ 1.0):
   - Hedge ratio close to 1:1
   - Straightforward calculation

### Important Note on Basis Risk

Using S&P 500 puts to hedge a portfolio with β ≠ 1.0 introduces **basis risk**:

- The hedge may not perfectly offset losses if your portfolio's actual movements diverge from the beta prediction
- Beta is estimated from historical data and can change over time
- During market stress, correlations can change (stocks may become more correlated)

Despite this imperfection, beta-adjusted hedging with index options is standard practice because:

- Index options are liquid and cost-effective
- Beta provides a reasonable first-order approximation
- It's far more practical than hedging each individual stock

## Strike Price Selection

When choosing put options for protection, the strike price determines the trade-off between cost and coverage:

### Out-of-the-Money (OTM) Puts

- **Lower strikes** (e.g., 10-15% below market)
- **Cheaper premiums** → lower insurance cost
- **Catastrophic protection only** → only pays off in severe crashes
- Analogous to high-deductible insurance

### At-the-Money (ATM) Puts

- **Strike near current market price**
- **Higher premiums** → expensive insurance
- **Immediate protection** → pays off for any market decline
- Analogous to low-deductible insurance

### Multi-Strike Strategies

Rather than buying a single strike, sophisticated strategies use multiple puts:

- Combine OTM puts (cheap, severe crash protection)
- With ATM or slightly OTM puts (moderate crash protection)
- Creates layered protection at optimized cost

This is where mathematical optimization becomes valuable—finding the best combination of strikes, expirations, and contract quantities to achieve a protection goal at minimum cost.

## Summary

**Key Takeaways:**

1. **Put options** give you the right to sell at a predetermined price, providing downside protection
2. **Option moneyness** (ITM/ATM/OTM) determines the premium cost and protection level
3. **Beta** measures portfolio volatility relative to the market and determines how many puts you need
4. **Beta-adjusted hedging**: $N_{\text{puts}} = \frac{\text{Portfolio Value}}{\text{Index Value} \times 100} \times \beta$
5. **Strike selection** involves a cost-coverage tradeoff that can be optimized

Understanding these fundamentals is essential for analyzing portfolio insurance strategies and working with the optimization models in this project.
