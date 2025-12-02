"""Portfolio performance analysis with industry-standard metrics.

This module provides comprehensive portfolio performance evaluation tools,
including risk-adjusted return metrics, capture ratios, and drawdown analysis.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


class PortfolioAnalyzer:
    """Comprehensive portfolio performance analyzer with industry-standard metrics.
    
    Provides various risk and return metrics for comparing portfolio strategies
    against benchmarks, including Beta, Sortino Ratio, Calmar Ratio, and
    upside/downside capture ratios.
    
    Parameters
    ----------
    data : pd.DataFrame
        DataFrame with 'Date' column and value columns for each strategy
    benchmark_col : str, optional
        Name of the benchmark column (default: "Unhedged")
    risk_free_rate : float, optional
        Annualized risk-free rate for Sharpe/Sortino calculations (default: 0.0)
        
    Attributes
    ----------
    data : pd.DataFrame
        Original portfolio value data
    benchmark_col : str
        Benchmark column name
    rf : float
        Risk-free rate
    returns : pd.DataFrame
        Daily returns for all strategies
    benchmark_returns : pd.Series
        Daily returns for the benchmark
        
    Methods
    -------
    calculate_beta(strategy_col)
        Calculate systematic risk (Beta) vs benchmark
    calculate_capture_ratios(strategy_col)
        Calculate upside and downside capture ratios
    calculate_sortino(strategy_col)
        Calculate Sortino ratio (return vs downside deviation)
    calculate_calmar(strategy_col)
        Calculate Calmar ratio (return vs maximum drawdown)
    get_summary()
        Generate comprehensive summary table for all strategies
        
    Examples
    --------
    >>> data = pd.DataFrame({
    ...     'Date': pd.date_range('2020-01-01', periods=100),
    ...     'Strategy_A': np.random.randn(100).cumsum() + 100,
    ...     'Benchmark': np.random.randn(100).cumsum() + 100
    ... })
    >>> analyzer = PortfolioAnalyzer(data, benchmark_col='Benchmark')
    >>> summary = analyzer.get_summary()
    >>> print(summary)
    """
    
    def __init__(
        self,
        data: pd.DataFrame,
        benchmark_col: str = "Unhedged",
        risk_free_rate: float = 0.0
    ):
        self.data = data.copy()
        self.benchmark_col = benchmark_col
        self.rf = risk_free_rate
        
        # Compute returns
        self.returns = self.data.set_index("Date").pct_change().dropna()
        self.benchmark_returns = self.returns[benchmark_col]

    def calculate_beta(self, strategy_col: str) -> float:
        """Calculate Beta (systematic risk vs benchmark).
        
        Beta measures how much a strategy moves relative to the market.
        - Beta = 1.0: Moves with the market
        - Beta > 1.0: More volatile than market
        - Beta < 1.0: Less volatile than market
        
        Formula: β = Cov(R_strategy, R_market) / Var(R_market)
        
        Parameters
        ----------
        strategy_col : str
            Name of the strategy column
            
        Returns
        -------
        float
            Beta coefficient
            
        Examples
        --------
        >>> beta = analyzer.calculate_beta('Strategy_A')
        >>> print(f"Beta: {beta:.2f}")
        """
        cov_matrix = np.cov(self.returns[strategy_col], self.benchmark_returns)
        beta = cov_matrix[0, 1] / cov_matrix[1, 1]
        return float(beta)

    def calculate_capture_ratios(self, strategy_col: str) -> tuple[float, float]:
        """Calculate Upside and Downside Capture ratios.
        
        Measures how well a strategy captures market gains (upside) vs
        market losses (downside).
        - Upside > 100%: Outperforms in up markets
        - Downside < 100%: Loses less in down markets
        
        Parameters
        ----------
        strategy_col : str
            Name of the strategy column
            
        Returns
        -------
        tuple[float, float]
            (upside_capture, downside_capture) as percentages
            
        Examples
        --------
        >>> up, down = analyzer.calculate_capture_ratios('Strategy_A')
        >>> print(f"Up: {up:.1f}%, Down: {down:.1f}%")
        """
        up_market = self.benchmark_returns > 0
        down_market = self.benchmark_returns < 0

        bench_up_avg = self.benchmark_returns[up_market].mean()
        strat_up_avg = self.returns.loc[up_market, strategy_col].mean()
        
        bench_down_avg = self.benchmark_returns[down_market].mean()
        strat_down_avg = self.returns.loc[down_market, strategy_col].mean()

        up_capture = (
            (strat_up_avg / bench_up_avg) * 100 if bench_up_avg != 0 else np.nan
        )
        down_capture = (
            (strat_down_avg / bench_down_avg) * 100 if bench_down_avg != 0 else np.nan
        )
        
        return float(up_capture), float(down_capture)

    def calculate_sortino(self, strategy_col: str) -> float:
        """Calculate Sortino Ratio (return vs downside deviation).
        
        Like Sharpe ratio, but penalizes only downside volatility.
        Higher is better. Focuses on harmful volatility.
        
        Formula: Sortino = (CAGR - r_f) / σ_downside
        
        Parameters
        ----------
        strategy_col : str
            Name of the strategy column
            
        Returns
        -------
        float
            Sortino ratio
            
        Examples
        --------
        >>> sortino = analyzer.calculate_sortino('Strategy_A')
        >>> print(f"Sortino: {sortino:.2f}")
        """
        # Annualized return (CAGR)
        total_return = self.data[strategy_col].iloc[-1] / self.data[strategy_col].iloc[0]
        n_years = len(self.data) / 252  # Trading days per year
        cagr = total_return ** (1 / n_years) - 1
        
        # Downside standard deviation (annualized)
        neg_returns = self.returns.loc[self.returns[strategy_col] < 0, strategy_col]
        downside_std = neg_returns.std() * np.sqrt(252) if len(neg_returns) > 0 else 0
        
        if downside_std == 0:
            return np.nan
            
        return float((cagr - self.rf) / downside_std)

    def calculate_calmar(self, strategy_col: str) -> float:
        """Calculate Calmar Ratio (annualized return vs max drawdown).
        
        Measures return relative to worst drawdown. Higher is better.
        Useful for evaluating downside risk management.
        
        Formula: Calmar = CAGR / |Max Drawdown|
        
        Parameters
        ----------
        strategy_col : str
            Name of the strategy column
            
        Returns
        -------
        float
            Calmar ratio
            
        Examples
        --------
        >>> calmar = analyzer.calculate_calmar('Strategy_A')
        >>> print(f"Calmar: {calmar:.2f}")
        """
        # Annualized return
        total_return = self.data[strategy_col].iloc[-1] / self.data[strategy_col].iloc[0]
        n_years = len(self.data) / 252
        cagr = total_return ** (1 / n_years) - 1

        # Maximum drawdown
        peaks = self.data[strategy_col].cummax()
        drawdowns = (self.data[strategy_col] - peaks) / peaks
        max_drawdown = drawdowns.min()

        if max_drawdown == 0:
            return np.nan
            
        return float(cagr / abs(max_drawdown))

    def get_summary(self) -> pd.DataFrame:
        """Generate comprehensive summary table for all strategies.
        
        Creates a DataFrame with all key metrics for easy comparison
        across strategies.
        
        Returns
        -------
        pd.DataFrame
            Summary table indexed by strategy name with columns:
            - Total Return (%)
            - Beta
            - Up Capture (%)
            - Down Capture (%)
            - Sortino Ratio
            - Calmar Ratio
            
        Examples
        --------
        >>> summary = analyzer.get_summary()
        >>> print(summary)
        """
        metrics = []
        cols = [c for c in self.returns.columns if c != "Date"]
        
        for col in cols:
            beta = self.calculate_beta(col)
            up_capture, down_capture = self.calculate_capture_ratios(col)
            sortino = self.calculate_sortino(col)
            calmar = self.calculate_calmar(col)
            
            # Total return for reference
            total_ret = (self.data[col].iloc[-1] / self.data[col].iloc[0] - 1) * 100

            metrics.append({
                "Strategy": col,
                "Total Return (%)": round(total_ret, 2),
                "Beta": round(beta, 2),
                "Up Capture (%)": round(up_capture, 1),
                "Down Capture (%)": round(down_capture, 1),
                "Sortino Ratio": round(sortino, 2),
                "Calmar Ratio": round(calmar, 2)
            })
            
        return pd.DataFrame(metrics).set_index("Strategy")
