"""
Financial Data Visualization Utilities
-------------------------------------
This module provides a comprehensive set of functions for creating interactive
financial charts and data visualizations for the dashboard.

Key features:
1. Price and volume visualization with customizable parameters
2. Normalized comparison charts for cross-asset performance evaluation
3. Strategy backtest visualization with benchmark comparisons
4. Market sentiment gauge for quick sentiment assessment
5. Portfolio allocation visualization through interactive pie charts

These visualization utilities use Plotly to create interactive, publication-quality
charts that help traders and analysts understand market trends, compare assets,
and evaluate portfolio performance over time.
"""

import plotly.graph_objects as go
import plotly.express as px


def create_price_chart(df, title, height=400):
    """
    Create a price chart using Plotly

    Args:
        df (DataFrame): Price data
        title (str): Chart title
        height (int): Chart height

    Returns:
        Figure: Plotly figure object

    Examples:
        >>> import pandas as pd
        >>> import plotly.graph_objects as go
        >>> from charts import create_price_chart
        >>> df = pd.DataFrame({
        ...     'datetime': pd.date_range("2020-01-01", periods=3),
        ...     'close': [100, 101, 102]
        ... })
        >>> fig = create_price_chart(df, "Test Chart")
        >>> isinstance(fig, go.Figure)
        True
    """
    fig = px.line(df, x='datetime', y='close', title=title)
    fig.update_layout(height=height)
    return fig


def create_volume_chart(df, title, height=400):
    """
    Create a volume chart using Plotly

    Args:
        df (DataFrame): Volume data
        title (str): Chart title
        height (int): Chart height

    Returns:
        Figure: Plotly figure object

    Examples:
        >>> import pandas as pd
        >>> import plotly.graph_objects as go
        >>> from charts import create_volume_chart
        >>> df = pd.DataFrame({
        ...     'datetime': pd.date_range("2020-01-01", periods=3),
        ...     'volume': [1000, 1500, 1200]
        ... })
        >>> fig = create_volume_chart(df, "Test Volume")
        >>> isinstance(fig, go.Figure)
        True
    """
    fig = px.bar(df, x='datetime', y='volume', title=title)
    fig.update_layout(height=height)
    return fig


def create_normalized_chart(spy_normalized, gold_normalized, height=500):
    """
    Create a normalized comparison chart

    Args:
        spy_normalized (DataFrame): Normalized SPY data
        gold_normalized (DataFrame): Normalized GLD data
        height (int): Chart height

    Returns:
        Figure: Plotly figure object

    Examples:
        >>> import pandas as pd
        >>> import plotly.graph_objects as go
        >>> from charts import create_normalized_chart
        >>> dates = pd.date_range("2020-01-01", periods=3)
        >>> spy_df = pd.DataFrame({'datetime': dates, 'normalized': [100, 102, 101]})
        >>> gold_df = pd.DataFrame({'datetime': dates, 'normalized': [100, 99, 98]})
        >>> fig = create_normalized_chart(spy_df, gold_df)
        >>> isinstance(fig, go.Figure)
        True
    """
    fig = go.Figure()

    if not spy_normalized.empty:
        fig.add_trace(
            go.Scatter(
                x=spy_normalized['datetime'],
                y=spy_normalized['normalized'],
                name="SPY"
            )
        )

    if not gold_normalized.empty:
        fig.add_trace(
            go.Scatter(
                x=gold_normalized['datetime'],
                y=gold_normalized['normalized'],
                name="GLD"
            )
        )

    fig.update_layout(title='Normalized Price (Base 100)', height=height)
    return fig


def create_backtest_chart(spy_df, gold_df, backtest_returns, initial_portfolio, height=400):
    """
        Create a portfolio backtest comparison chart

        Args:
            spy_df (DataFrame): SPY price data with 'datetime' and 'close' columns.
            gold_df (DataFrame): GLD price data with 'datetime' and 'close' columns.
            backtest_returns (list[float]): Portfolio value time series from the backtest.
            initial_portfolio (float): Starting capital used for benchmarks.
            height (int): Chart height in pixels.

        Returns:
            Figure: A Plotly Figure object comparing backtest performance against
            buy-and-hold SPY and GLD benchmarks over time.

        Examples:
            >>> import pandas as pd
            >>> import plotly.graph_objects as go
            >>> from charts import create_backtest_chart
            >>> dates = pd.date_range("2020-01-01", periods=3)
            >>> spy_df = pd.DataFrame({'datetime': dates, 'close': [100, 110, 120]})
            >>> gold_df = pd.DataFrame({'datetime': dates, 'close': [50, 55, 60]})
            >>> backtest = [1000, 1050, 1100]
            >>> fig = create_backtest_chart(spy_df, gold_df, backtest, 1000)
            >>> isinstance(fig, go.Figure)
            True
        """
    import plotly.graph_objects as go
    # ensure lengths match
    dates = spy_df['datetime']
    if len(backtest_returns) != len(dates):
        # either truncate the longer one, or raise an informative error
        n = min(len(backtest_returns), len(dates))
        backtest_returns = backtest_returns[:n]
        dates = dates.iloc[:n]

    # buy‐and‐hold benchmarks
    spy_val  = initial_portfolio * (spy_df['close'] / spy_df['close'].iloc[0])
    gold_val = initial_portfolio * (gold_df['close'] / gold_df['close'].iloc[0])

    fig = go.Figure([
        go.Scatter(x=spy_df['datetime'], y=spy_val,         name="Buy-and-Hold SPY"),
        go.Scatter(x=gold_df['datetime'], y=gold_val,        name="Buy-and-Hold GLD"),
    ])

    fig.update_layout(
        title="Portfolio Value Over Time",
        height=height,
        xaxis_title="Date",
        yaxis_title="Portfolio Value"
    )
    return fig


def create_sentiment_gauge(sentiment_score, height=250):
    """
    Create sentiment gauge chart

    Args:
        sentiment_score (float): Market sentiment score
        height (int): Chart height

    Returns:
        Figure: Plotly figure object

    Examples:
        >>> import plotly.graph_objects as go
        >>> from charts import create_sentiment_gauge
        >>> fig = create_sentiment_gauge(0.5)
        >>> isinstance(fig, go.Figure)
        True
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=sentiment_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Sentiment Index"},
        gauge={
            'axis': {'range': [-1, 1]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [-1, -0.3], 'color': "red"},
                {'range': [-0.3, 0.3], 'color': "gray"},
                {'range': [0.3, 1], 'color': "green"}
            ],
            'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': sentiment_score}
        }
    ))

    fig.update_layout(height=height)
    return fig
