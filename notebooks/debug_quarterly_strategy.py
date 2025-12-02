"""Debug script to trace quarterly and conditional strategy behavior."""

from datetime import datetime
import pandas as pd
import sys

# Add src to path
sys.path.insert(0, '/Users/akhilkarra/ode/21393/options-hedge/src')

from options_hedge.market import Market
from options_hedge.portfolio import Portfolio
from options_hedge.strategies import (
    quarterly_protective_put_strategy,
    conditional_hedging_strategy,
)


def debug_quarterly_strategy(market_name: str, start: str, end: str):
    """Debug quarterly strategy to see why it shows 0% benefit."""
    
    print(f"\n{'='*80}")
    print(f"DEBUGGING QUARTERLY STRATEGY: {market_name}")
    print(f"{'='*80}\n")
    
    # Create market
    market = Market(ticker="^GSPC", start=start, end=end, fetch_vix=True)
    portfolio = Portfolio(initial_value=1_000_000, beta=1.0)
    
    # Strategy params
    params = {
        "hedge_interval": 90,
        "put_cost": 0.01,
        "strike_ratio": 0.9,
        "expiry_days": 90,
    }
    
    purchase_log = []
    exercise_log = []
    
    for i, (ts_date, row) in enumerate(market.data.iterrows()):
        price = float(row["Close"])
        daily_return = float(row["Returns"])
        
        # Update equity
        portfolio.update_equity(daily_return)
        
        # Check options before strategy
        options_before = len(portfolio.options)
        
        # Apply strategy
        quarterly_protective_put_strategy(
            portfolio, price, ts_date.to_pydatetime(), params, market
        )
        
        # Check if new option purchased
        options_after = len(portfolio.options)
        if options_after > options_before:
            new_option = portfolio.options[-1]
            purchase_log.append({
                'Date': ts_date,
                'Price': price,
                'Strike': new_option.strike,
                'Premium': new_option.premium,
                'Expiry': new_option.expiry,
                'OTM_%': (1 - new_option.strike / price) * 100,
            })
        
        # Check for exercised/expired options
        expired_count = sum(
            1 for opt in portfolio.options 
            if ts_date >= pd.Timestamp(opt.expiry)
        )
        
        if expired_count > 0:
            for opt in portfolio.options:
                if ts_date >= pd.Timestamp(opt.expiry):
                    intrinsic = max(opt.strike - price, 0)
                    exercise_log.append({
                        'Date': ts_date,
                        'Price': price,
                        'Strike': opt.strike,
                        'Premium_Paid': opt.premium,
                        'Intrinsic': intrinsic,
                        'Payoff': intrinsic * opt.quantity,
                        'Net': (intrinsic - opt.premium) * opt.quantity,
                        'ITM': intrinsic > 0,
                    })
        
        # Exercise expired options
        portfolio.exercise_expired_options(price, ts_date)
    
    # Summary
    print(f"Total options purchased: {len(purchase_log)}")
    print(f"Total options expired/exercised: {len(exercise_log)}")
    print(f"\nFinal portfolio value: ${portfolio.total_value(price, ts_date):,.0f}")
    print(f"Final return: {(portfolio.total_value(price, ts_date) / 1_000_000 - 1) * 100:.2f}%")
    
    # Show purchases
    if purchase_log:
        print(f"\n{'='*80}")
        print("OPTION PURCHASES")
        print(f"{'='*80}")
        for i, p in enumerate(purchase_log[:5], 1):  # First 5
            print(f"\n#{i}: {p['Date'].date()}")
            print(f"  Price: ${p['Price']:,.0f}")
            print(f"  Strike: ${p['Strike']:,.0f} ({p['OTM_%']:.1f}% OTM)")
            print(f"  Premium: ${p['Premium']:,.0f}")
            print(f"  Expiry: {p['Expiry'].date()}")
        
        if len(purchase_log) > 5:
            print(f"\n... and {len(purchase_log) - 5} more purchases")
    
    # Show exercises
    if exercise_log:
        print(f"\n{'='*80}")
        print("OPTION EXERCISES/EXPIRIES")
        print(f"{'='*80}")
        
        itm_count = sum(1 for e in exercise_log if e['ITM'])
        otm_count = sum(1 for e in exercise_log if not e['ITM'])
        total_payoff = sum(e['Payoff'] for e in exercise_log)
        total_cost = sum(e['Premium_Paid'] for e in exercise_log)
        
        print(f"\nSummary:")
        print(f"  ITM exercises: {itm_count}")
        print(f"  OTM expiries: {otm_count}")
        print(f"  Total payoffs: ${total_payoff:,.0f}")
        print(f"  Total premiums: ${total_cost:,.0f}")
        print(f"  Net P&L: ${total_payoff - total_cost:,.0f}")
        
        # Show ITM exercises
        itm_exercises = [e for e in exercise_log if e['ITM']]
        if itm_exercises:
            print(f"\nITM Exercises (first 5):")
            for e in itm_exercises[:5]:
                print(f"  {e['Date'].date()}: Strike ${e['Strike']:,.0f}, "
                      f"Price ${e['Price']:,.0f}, "
                      f"Payoff ${e['Payoff']:,.0f}, "
                      f"Net ${e['Net']:,.0f}")
    else:
        print(f"\n⚠️  NO OPTIONS WERE EXERCISED/EXPIRED!")
        print("This explains the 0% benefit - options were purchased but never realized.")
    
    return purchase_log, exercise_log


if __name__ == "__main__":
    # Debug dot-com crash
    debug_quarterly_strategy("Dot-Com Crash", "2000-01-01", "2003-01-01")
    
    # Debug GFC
    debug_quarterly_strategy("Financial Crisis", "2007-01-01", "2010-01-01")
    
    # Debug COVID
    debug_quarterly_strategy("COVID-19", "2019-11-01", "2020-12-31")
