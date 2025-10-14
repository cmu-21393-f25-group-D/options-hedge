# Portfolio Insurance Optimization

Welcome to our portfolio insurance project! We're building a modern solution to help retirees protect their portfolios from market crashes while maintaining growth potential.

## What is Portfolio Insurance?

**Portfolio insurance** is a risk management strategy that uses financial derivatives (in our case, put options) to limit losses from declining asset prices. Think of it like home insurance for your investment portfolio:

- You pay a premium (the cost of the options)
- If nothing bad happens (market goes up), you lose the premium but your portfolio gains value
- If disaster strikes (market crashes), the insurance pays out to cover your losses

By strategically purchasing put options on the S&P 500 index, we can create a "floor" that limits maximum portfolio losses while allowing participation in market gains.

## The Challenge

Upcoming retirees face a critical trade-off:

1. **Stay in stocks**: Maintain growth potential and inflation protection, but risk catastrophic losses right when income stops
2. **Move to bonds**: Preserve capital but earn minimal returns in today's low interest-rate environment

With Baby Boomers entering retirement en masse, trillions of dollars are at risk. Traditional asset allocation strategies may no longer provide adequate protection.

## Our Approach

We use operations research and optimization to answer: **"What is the cheapest combination of put options needed to guarantee a portfolio won't lose more than X% over a given period?"**

The optimization model:

- **Minimizes**: Total cost of purchasing options
- **While ensuring**: Portfolio is protected against a range of potential market scenarios
- **Allows**: Full participation in market upside

## Project Team

- Akhil Karra
- Zoe Xu
- Vivaan Shroff
- Wendy Wang

## Documentation Contents

```{tableofcontents}
```
