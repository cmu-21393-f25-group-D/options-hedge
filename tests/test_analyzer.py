"""Tests for portfolio analyzer module."""

import numpy as np
import pandas as pd
import pytest
from options_hedge.analyzer import PortfolioAnalyzer


class TestPortfolioAnalyzer:
    """Test PortfolioAnalyzer class."""

    def test_initialization(self):
        """Test analyzer initialization."""
        data = pd.DataFrame({
            'Date': pd.date_range('2020-01-01', periods=100),
            'Strategy_A': np.linspace(100, 120, 100),
            'Benchmark': np.linspace(100, 110, 100),
        })
        
        analyzer = PortfolioAnalyzer(data, benchmark_col='Benchmark')
        
        assert analyzer.benchmark_col == 'Benchmark'
        assert analyzer.rf == 0.0
        assert len(analyzer.returns) == 99  # One less due to pct_change
        assert 'Strategy_A' in analyzer.returns.columns
        assert 'Benchmark' in analyzer.returns.columns

    def test_beta_calculation(self):
        """Test beta calculation."""
        # Create data where strategy returns are proportional to benchmark
        dates = pd.date_range('2020-01-01', periods=100)
        np.random.seed(42)  # For reproducibility
        benchmark_returns = np.random.randn(100) * 0.01
        benchmark = 100 * (1 + benchmark_returns).cumprod()
        
        # Strategy with 1.5x the returns -> beta should be ~1.5
        strategy_returns = benchmark_returns * 1.5
        strategy = 100 * (1 + strategy_returns).cumprod()
        
        data = pd.DataFrame({
            'Date': dates,
            'Strategy': strategy,
            'Benchmark': benchmark,
        })
        
        analyzer = PortfolioAnalyzer(data, benchmark_col='Benchmark')
        beta = analyzer.calculate_beta('Strategy')
        
        # Beta should be close to 1.5
        assert 1.4 < beta < 1.6

    def test_beta_perfect_correlation(self):
        """Test beta with perfect positive correlation."""
        dates = pd.date_range('2020-01-01', periods=100)
        benchmark = np.linspace(100, 120, 100)
        strategy = benchmark.copy()  # Perfect correlation -> beta = 1
        
        data = pd.DataFrame({
            'Date': dates,
            'Strategy': strategy,
            'Benchmark': benchmark,
        })
        
        analyzer = PortfolioAnalyzer(data, benchmark_col='Benchmark')
        beta = analyzer.calculate_beta('Strategy')
        
        assert abs(beta - 1.0) < 0.01

    def test_capture_ratios(self):
        """Test upside and downside capture ratios."""
        dates = pd.date_range('2020-01-01', periods=100)
        
        # Create alternating up/down market
        benchmark_returns = np.array([0.01 if i % 2 == 0 else -0.01 for i in range(100)])
        benchmark = 100 * (1 + benchmark_returns).cumprod()
        
        # Strategy: captures 80% upside, 50% downside
        strategy_returns = np.array([
            0.008 if i % 2 == 0 else -0.005 for i in range(100)
        ])
        strategy = 100 * (1 + strategy_returns).cumprod()
        
        data = pd.DataFrame({
            'Date': dates,
            'Strategy': strategy,
            'Benchmark': benchmark,
        })
        
        analyzer = PortfolioAnalyzer(data, benchmark_col='Benchmark')
        up, down = analyzer.calculate_capture_ratios('Strategy')
        
        # Should capture ~80% upside and ~50% downside
        assert 70 < up < 90
        assert 40 < down < 60

    def test_capture_ratios_all_positive(self):
        """Test capture ratios with only positive returns."""
        dates = pd.date_range('2020-01-01', periods=50)
        benchmark = np.linspace(100, 150, 50)  # Always increasing
        strategy = np.linspace(100, 140, 50)   # Also increasing, less
        
        data = pd.DataFrame({
            'Date': dates,
            'Strategy': strategy,
            'Benchmark': benchmark,
        })
        
        analyzer = PortfolioAnalyzer(data, benchmark_col='Benchmark')
        up, down = analyzer.calculate_capture_ratios('Strategy')
        
        assert up > 0  # Should have upside capture
        assert pd.isna(down) or down == 0  # No down markets

    def test_sortino_ratio(self):
        """Test Sortino ratio calculation."""
        dates = pd.date_range('2020-01-01', periods=252)  # 1 year
        
        # Strategy with positive return and some downside
        returns = np.random.randn(252) * 0.01
        returns[:126] = abs(returns[:126])  # First half all positive
        strategy = 100 * (1 + returns).cumprod()
        
        benchmark = 100 * (1 + np.random.randn(252) * 0.01).cumprod()
        
        data = pd.DataFrame({
            'Date': dates,
            'Strategy': strategy,
            'Benchmark': benchmark,
        })
        
        analyzer = PortfolioAnalyzer(data, benchmark_col='Benchmark')
        sortino = analyzer.calculate_sortino('Strategy')
        
        assert isinstance(sortino, float)
        assert not pd.isna(sortino)

    def test_sortino_no_downside(self):
        """Test Sortino ratio with no negative returns."""
        dates = pd.date_range('2020-01-01', periods=100)
        strategy = np.linspace(100, 150, 100)  # Always increasing
        benchmark = np.linspace(100, 140, 100)
        
        data = pd.DataFrame({
            'Date': dates,
            'Strategy': strategy,
            'Benchmark': benchmark,
        })
        
        analyzer = PortfolioAnalyzer(data, benchmark_col='Benchmark')
        sortino = analyzer.calculate_sortino('Strategy')
        
        # No downside volatility -> should be NaN or very high
        assert pd.isna(sortino) or sortino > 10

    def test_calmar_ratio(self):
        """Test Calmar ratio calculation."""
        dates = pd.date_range('2020-01-01', periods=252)
        
        # Create strategy with known drawdown
        values = np.linspace(100, 150, 252)
        values[100:120] = np.linspace(150, 120, 20)  # Drawdown
        
        data = pd.DataFrame({
            'Date': dates,
            'Strategy': values,
            'Benchmark': np.linspace(100, 140, 252),
        })
        
        analyzer = PortfolioAnalyzer(data, benchmark_col='Benchmark')
        calmar = analyzer.calculate_calmar('Strategy')
        
        assert isinstance(calmar, float)
        assert not pd.isna(calmar)
        assert calmar > 0  # Positive return, should be positive

    def test_calmar_no_drawdown(self):
        """Test Calmar ratio with no drawdown."""
        dates = pd.date_range('2020-01-01', periods=100)
        strategy = np.linspace(100, 150, 100)  # Always increasing
        benchmark = np.linspace(100, 140, 100)
        
        data = pd.DataFrame({
            'Date': dates,
            'Strategy': strategy,
            'Benchmark': benchmark,
        })
        
        analyzer = PortfolioAnalyzer(data, benchmark_col='Benchmark')
        calmar = analyzer.calculate_calmar('Strategy')
        
        # No drawdown -> should be NaN or very high
        assert pd.isna(calmar) or calmar > 100

    def test_get_summary(self):
        """Test summary table generation."""
        dates = pd.date_range('2020-01-01', periods=252)
        
        data = pd.DataFrame({
            'Date': dates,
            'Strategy_A': 100 * (1 + np.random.randn(252) * 0.01).cumprod(),
            'Strategy_B': 100 * (1 + np.random.randn(252) * 0.015).cumprod(),
            'Benchmark': 100 * (1 + np.random.randn(252) * 0.01).cumprod(),
        })
        
        analyzer = PortfolioAnalyzer(data, benchmark_col='Benchmark')
        summary = analyzer.get_summary()
        
        # Check structure
        assert isinstance(summary, pd.DataFrame)
        assert len(summary) == 3  # 3 strategies
        assert 'Total Return (%)' in summary.columns
        assert 'Beta' in summary.columns
        assert 'Up Capture (%)' in summary.columns
        assert 'Down Capture (%)' in summary.columns
        assert 'Sortino Ratio' in summary.columns
        assert 'Calmar Ratio' in summary.columns
        
        # Check all strategies present
        assert 'Strategy_A' in summary.index
        assert 'Strategy_B' in summary.index
        assert 'Benchmark' in summary.index

    def test_summary_values_reasonable(self):
        """Test that summary values are in reasonable ranges."""
        dates = pd.date_range('2020-01-01', periods=252)
        
        data = pd.DataFrame({
            'Date': dates,
            'Strategy': 100 * (1 + np.random.randn(252) * 0.01).cumprod(),
            'Benchmark': 100 * (1 + np.random.randn(252) * 0.01).cumprod(),
        })
        
        analyzer = PortfolioAnalyzer(data, benchmark_col='Benchmark')
        summary = analyzer.get_summary()
        
        # Check reasonable ranges
        for strategy in summary.index:
            # Beta should be reasonable
            assert -5 < summary.loc[strategy, 'Beta'] < 5
            
            # Capture ratios should be percentages (can be > 100%)
            assert -500 < summary.loc[strategy, 'Up Capture (%)'] < 500
            assert -500 < summary.loc[strategy, 'Down Capture (%)'] < 500

    def test_custom_risk_free_rate(self):
        """Test analyzer with custom risk-free rate."""
        dates = pd.date_range('2020-01-01', periods=100)
        
        data = pd.DataFrame({
            'Date': dates,
            'Strategy': np.linspace(100, 120, 100),
            'Benchmark': np.linspace(100, 110, 100),
        })
        
        analyzer = PortfolioAnalyzer(data, benchmark_col='Benchmark', risk_free_rate=0.03)
        
        assert analyzer.rf == 0.03

    def test_empty_strategy_column(self):
        """Test behavior with strategy that has no data."""
        dates = pd.date_range('2020-01-01', periods=100)
        
        data = pd.DataFrame({
            'Date': dates,
            'Strategy': [100.0] * 100,  # Constant value
            'Benchmark': np.linspace(100, 110, 100),
        })
        
        analyzer = PortfolioAnalyzer(data, benchmark_col='Benchmark')
        
        # Should handle constant strategy (zero returns)
        beta = analyzer.calculate_beta('Strategy')
        assert isinstance(beta, float)

    def test_benchmark_beta_is_one(self):
        """Test that benchmark's beta vs itself is 1.0."""
        dates = pd.date_range('2020-01-01', periods=100)
        
        data = pd.DataFrame({
            'Date': dates,
            'Benchmark': 100 * (1 + np.random.randn(100) * 0.01).cumprod(),
        })
        
        analyzer = PortfolioAnalyzer(data, benchmark_col='Benchmark')
        beta = analyzer.calculate_beta('Benchmark')
        
        assert abs(beta - 1.0) < 0.01  # Should be very close to 1

    def test_negative_returns_handling(self):
        """Test handling of strategies with negative total returns."""
        dates = pd.date_range('2020-01-01', periods=252)
        
        # Strategy that loses money
        strategy = np.linspace(100, 70, 252)
        benchmark = np.linspace(100, 110, 252)
        
        data = pd.DataFrame({
            'Date': dates,
            'Strategy': strategy,
            'Benchmark': benchmark,
        })
        
        analyzer = PortfolioAnalyzer(data, benchmark_col='Benchmark')
        summary = analyzer.get_summary()
        
        # Should still produce metrics
        assert summary.loc['Strategy', 'Total Return (%)'] < 0
        assert isinstance(summary.loc['Strategy', 'Beta'], (int, float))
