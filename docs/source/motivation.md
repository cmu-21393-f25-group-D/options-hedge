# Project Motivation

## What is Portfolio Insurance?

**Portfolio insurance** is a risk management strategy that uses financial derivatives (in our case, put options) to limit losses from declining asset prices. Think of it like home insurance for your investment portfolio:

- You pay a premium (the cost of the options)
- If nothing bad happens (market goes up), you lose the premium but your portfolio gains value
- If disaster strikes (market crashes), the insurance pays out to cover your losses

By strategically purchasing put options on the S&P 500 index, we can create a "floor" that limits maximum portfolio losses while allowing participation in market gains.

### How It Works

Just as you insure your home against fire or theft, portfolio insurance protects your investments against market crashes. The key difference: you're using financial derivatives (options) rather than traditional insurance contracts.

**A put option** gives you the right (but not obligation) to sell an asset at a predetermined price (the "strike price"). If the market crashes below that price, your put options increase in value, offsetting losses in your portfolio. If the market goes up, you simply don't exercise the options—the only cost is the premium you paid upfront.

## The Retirement Crisis

### A Growing Challenge

The United States is experiencing an unprecedented demographic shift. According to the Population Reference Bureau, "the number of Americans ages 65 and older is projected to nearly double from 52 million in 2018 to 95 million by 2060."[^1] This wave represents the largest generation of retirees in American history, controlling trillions of dollars in retirement savings.

This demographic transformation creates an urgent financial challenge: **how can millions of retirees preserve wealth while maintaining purchasing power over increasingly longer retirements?**

### Why This Problem Is Escalating

Three converging trends make this challenge more critical than ever:

1. **Unprecedented scale**: The Baby Boomer generation represents 73 million Americans born between 1946-1964, all approaching or in retirement. This is not just a generational blip—it's a fundamental reshaping of the economic landscape.

2. **Longer lifespans**: Advances in healthcare mean people are living longer than ever before. A 65-year-old today can expect to live another 20-30+ years, meaning retirement portfolios must sustain decades of withdrawals. This extended timeframe amplifies both the sequence-of-returns risk and the cumulative impact of inflation.

3. **Persistent inflation risk**: Recent years have demonstrated that high inflation cycles remain a threat. Retirees can't simply move to cash or bonds without risking their purchasing power over multiple decades. With the Fed targeting 2% inflation, even "moderate" inflation will cut purchasing power in half over a 35-year retirement.

**The stakes are enormous**: Traditional asset allocation strategies (like the "60/40 portfolio" or the "4% rule") were designed for different demographic and economic conditions. With this demographic tsunami and trillions of dollars at risk, we need smarter, more adaptive solutions that provide downside protection without sacrificing growth potential.

[^1]: Population Reference Bureau. "Fact Sheet: Aging in the United States." PRB, 2019. <https://www.prb.org/resources/fact-sheet-aging-in-the-united-states/>

### The Traditional Dilemma

Retirees traditionally face a difficult trade-off when managing their portfolios:

#### Option 1: Stay in Stocks

**Advantages:**

- Growth potential to keep pace with inflation
- Historical long-term returns of ~10% annually
- Participation in economic growth

**Risks:**

- Catastrophic losses right when income stops
- Sequence-of-returns risk: a market crash early in retirement can permanently impair financial security
- Volatility that's psychologically difficult to endure on a fixed income

#### Option 2: Move to Bonds

**Advantages:**

- Capital preservation
- Predictable income streams
- Lower volatility

**Risks:**

- Minimal returns in today's low interest-rate environment
- Inflation risk: purchasing power erosion over 20-30 year retirement
- Opportunity cost of missing stock market gains

### The Sequence-of-Returns Problem

Perhaps the most significant risk facing retirees is the **sequence-of-returns risk**. Consider two retirees with identical portfolios:

- **Retiree A** experiences a 40% market crash in year 1 of retirement
- **Retiree B** experiences the same crash 10 years into retirement

Even if both experience identical average returns over their retirement, Retiree A will likely run out of money first. Why? Because they're forced to sell stocks at depressed prices to fund living expenses, locking in losses and reducing the capital base for future growth.

This is the retirement nightmare: working your entire life to build a nest egg, only to see it decimated right when you need it most.

## Why Traditional Solutions Fall Short

### The 60/40 Portfolio

The classic "60% stocks, 40% bonds" allocation is designed to balance growth and stability. However:

- In today's low interest-rate environment, the 40% bond allocation provides minimal returns
- The 60% stock allocation still exposes retirees to significant downside risk
- This static allocation doesn't adapt to changing market conditions

### Target-Date Funds

These funds automatically shift to more conservative allocations as retirement approaches. But:

- The shift to bonds means missing out on potential stock gains
- They don't provide explicit downside protection
- The one-size-fits-all approach may not match individual risk tolerance

### Annuities

Annuities provide guaranteed income but:

- High fees significantly reduce returns
- Lock up capital with limited liquidity
- Don't provide inflation protection in many cases
- Expose retirees to counterparty risk

## Portfolio Insurance: A Better Approach

### The Core Idea

What if we could create a "floor" for portfolio losses while maintaining full participation in upside gains? This is the promise of portfolio insurance using put options.

**Put options** give the holder the right (but not the obligation) to sell an asset at a predetermined price. For a portfolio invested in S&P 500 index funds, we can purchase put options that:

1. **Set a floor**: Guarantee the portfolio won't fall below a certain value
2. **Preserve upside**: Allow full participation if markets rise
3. **Provide flexibility**: Can be customized to different protection levels and time horizons

### Why Optimization Matters

The challenge: **put options cost money**. The premium paid for options reduces portfolio returns.

This is where optimization comes in. Instead of buying expensive at-the-money puts, we can:

- Identify the most cost-effective combination of puts at different strike prices
- Balance protection across multiple time horizons
- Minimize total cost while ensuring adequate protection

Our optimization model finds the **cheapest** combination of put options that guarantees protection against a specified range of market scenarios.

### Our Research Questions

This project addresses two key questions using operations research:

1. **"What is the optimal protection level?"** - Determining the right balance between downside protection and cost. What maximum loss percentage makes sense for retirees given their financial situation, risk tolerance, and time horizon?

2. **"What is the cheapest way to achieve that protection?"** - Finding the most cost-effective combination of put options to guarantee a portfolio won't lose more than a specified percentage over a given period.

**The optimization model:**

- **Minimizes**: Total cost of purchasing options
- **While ensuring**: Portfolio is protected against a range of potential market scenarios
- **Allows**: Full participation in market upside
- **Determines**: The optimal protection level that balances safety and affordability

By solving both questions, we create a comprehensive framework that doesn't just optimize option selection, but also helps retirees make informed decisions about their protection strategy.

## Real-World Impact

### The Scale of the Problem

- Over 10,000 Baby Boomers retire every day in the United States
- Total U.S. retirement assets exceed $35 trillion
- Even small improvements in portfolio efficiency can have enormous impact

### Who Benefits?

This project has applications for:

1. **Individual retirees** seeking cost-effective downside protection
2. **Financial advisors** looking to optimize client portfolios
3. **Institutional investors** managing pension funds and endowments
4. **Researchers** studying risk management and portfolio optimization

## Project Goals

Through this project, we aim to:

1. **Develop a mathematical optimization model** for cost-effective portfolio insurance
2. **Integrate real market data** from financial data providers
3. **Create practical tools** that can be used by retirees and financial professionals
4. **Contribute to the field** of financial optimization and risk management

By combining operations research techniques with modern financial engineering, we can help address one of the most pressing challenges facing millions of Americans entering retirement.
