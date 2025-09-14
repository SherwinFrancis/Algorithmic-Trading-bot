"""
Trading Dashboard Application
-----------------------------

This module defines the Streamlit “Smart Trading Dashboard” app, integrating market
data, sentiment analysis, and global time utilities for traders and analysts.

Key features:
1. Page configuration and session-state reset
2. Sidebar controls for portfolio value, data interval, and output size
3. Fetching SPY and GLD time series through the market_data.py file
4. Sentiment analysis and backtest through the sentiment.py file and sentiment.py file
5. Interactive Plotly charts: price history, volume, normalized comparison, sentiment gauge
6. Trade table with styled “Take Profit” / “Stop Loss” highlights and dropdown selector
7. World clock and market countdown via world_clock.py file
8. Current price & news-headline display components

"""
import streamlit as st
from modules.market_data import fetch_time_series, convert_to_dataframe, calculate_normalized_data
from modules.sentiment import get_current_market_sentiment
from modules.sentiment_trader import sentiment_strategy_backtest
from modules.world_clock import display_world_clock, display_countdown_timer
from datetime import datetime
import pandas as pd
from ui.charts import (
    create_price_chart,
    create_volume_chart,
    create_normalized_chart,
    create_sentiment_gauge)
from ui.components import (
    display_sidebar_settings,
    display_current_prices,
    display_news_headlines,
    display_trade_dropdown
)

from config import PROFIT_TAKING, BULLISH_THRESHOLD, BEARISH_THRESHOLD, STOP_LOSS

def create_streamlit_app():
    """
    Build and render the Streamlit Trading Dashboard.

    Args:
        None

    Returns:
        None

    Examples:
        >>> import streamlit as st
        >>> import pandas as pd
        >>> import datetime as dt
        >>> from modules import market_data, sentiment, sentiment_trader, world_clock
        >>> from ui import charts, components
        >>> import config
        >>>
        >>> # Mock Streamlit functions and contexts
        >>> st.set_page_config = lambda **kwargs: None
        >>> st.session_state = {}
        >>> st.rerun = lambda: None
        >>> st.markdown = lambda text, **kwargs: None
        >>>
        >>> # Provide a sidebar context manager with button and id
        >>> Sidebar = type('Sidebar', (), {
        ...     '__enter__': lambda self: self,
        ...     '__exit__': lambda self, exc_type, exc_val, exc_tb: None,
        ...     'button': lambda self, text: False,
        ... })
        >>> st.sidebar = Sidebar()
        >>> st.sidebar.id = None  # satisfy cache decorator
        >>>
        >>> # Spinner context manager
        >>> Spinner = type('Spinner', (), {
        ...     '__init__': lambda self, text: None,
        ...     '__enter__': lambda self: self,
        ...     '__exit__': lambda self, exc_type, exc_val, exc_tb: None
        ... })
        >>> st.spinner = Spinner
        >>>
        >>> # Columns context
        >>> Column = type('Column', (), {
        ...     '__enter__': lambda self: self,
        ...     '__exit__': lambda self, exc_type, exc_val, exc_tb: None
        ... })
        >>> st.columns = lambda specs: [Column() for _ in range(specs if isinstance(specs, int) else len(specs))]
        >>> # Other Streamlit functions
        >>> st.error = lambda text: None
        >>> st.header = lambda text: None
        >>> st.subheader = lambda text: None
        >>> st.write = lambda *args, **kwargs: None
        >>> st.warning = lambda text: None
        >>> st.info = lambda text: None
        >>> st.plotly_chart = lambda fig, **kwargs: None
        >>> st.tabs = lambda tabs: [Column() for _ in tabs]
        >>> st.dataframe = lambda df, **kwargs: None
        >>>
        >>> # Mock external modules fetch and conversions
        >>> fetch_time_series = lambda symbol, **kwargs: []
        >>> convert_to_dataframe = lambda data: pd.DataFrame()
        >>> calculate_normalized_data = lambda spy, gold: (pd.DataFrame(), pd.DataFrame())
        >>> get_current_market_sentiment = lambda: (0.0, '', [])
        >>> sentiment_strategy_backtest = lambda *args, **kwargs: ([], [], [])
        >>> display_world_clock = lambda: None
        >>> display_countdown_timer = lambda: None
        >>>
        >>> # Mock UI components
        >>> create_price_chart = lambda df, title: {}
        >>> create_volume_chart = lambda df, title: {}
        >>> create_normalized_chart = lambda spy, gold: {}
        >>> create_sentiment_gauge = lambda score: {}
        >>> display_sidebar_settings = lambda **kwargs: (10000.0, '15min', 80)
        >>> display_current_prices = lambda spy, gold: None
        >>> display_news_headlines = lambda articles: None
        >>> display_trade_dropdown = lambda trades, mapping: None
        >>>
        >>> # Configuration values
        >>> config.PROFIT_TAKING = 11.75
        >>> config.BULLISH_THRESHOLD = 0.4
        >>> config.BEARISH_THRESHOLD = 0.3
        >>> config.STOP_LOSS = 2.25
        >>>
        >>> # Should execute without errors
        >>> create_streamlit_app()
    """
    st.set_page_config(
        page_title="Trading Dashboard",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    if st.sidebar.button(" Clear Session State (fully reset dashboard)"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    with st.sidebar:
        take_profit = PROFIT_TAKING / 100  # 11.75%
        stop_loss = STOP_LOSS / 100     # 2.25%
        bullish = BULLISH_THRESHOLD             # Bullish sentiment threshold
        bearish = -BEARISH_THRESHOLD           # Bearish sentiment threshold

        portfolio_value, interval, outputsize = display_sidebar_settings(
            on_refresh_callback=lambda: st.rerun()
        )

    with st.spinner("Fetching data..."):
        spy_data = fetch_time_series('SPY', interval=interval, outputsize=outputsize)
        gold_data = fetch_time_series('GLD', interval=interval, outputsize=outputsize)
        sentiment_score, sentiment_summary, article_details = get_current_market_sentiment()
        st.session_state['current_datetime'] = datetime.now()

    spy_df = convert_to_dataframe(spy_data)
    gold_df = convert_to_dataframe(gold_data)

    st.markdown(
        "<h1 style='color: darkgreen;'>Smart Trading Dashboard</h1>",
        unsafe_allow_html=True
    )
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("Market Data")

        if spy_df.empty or gold_df.empty:
            st.error(" Data not available.")
        else:
            tab1, tab2, tab3, tab4 = st.tabs([
                "Price Charts", "Comparison", "Volume", "Sentiment Strategy"
            ])

            with tab1:
                st.subheader("SPY and GLD Price History")
                st.plotly_chart(create_price_chart(spy_df, 'SPY Price'), use_container_width=True)
                st.plotly_chart(create_price_chart(gold_df, 'GLD Price'), use_container_width=True)

            with tab2:
                st.subheader("Normalized Comparison")
                spy_norm, gold_norm = calculate_normalized_data(spy_df, gold_df)
                st.plotly_chart(create_normalized_chart(spy_norm, gold_norm), use_container_width=True)

            with tab3:
                st.subheader("Trading Volume")
                if 'volume' in spy_df.columns:
                    st.plotly_chart(create_volume_chart(spy_df, 'SPY Volume'), use_container_width=True)
                if 'volume' in gold_df.columns:
                    st.plotly_chart(create_volume_chart(gold_df, 'GLD Volume'), use_container_width=True)

            with tab4:
                st.subheader(" Sentiment Strategy Results")
                dates, sentiment_values, sentiment_transactions = sentiment_strategy_backtest(
                    spy_df, gold_df, portfolio_value,
                    take_profit=take_profit,
                    stop_loss=stop_loss,
                    bullish_threshold=bullish,
                    bearish_threshold=bearish
                )

                if dates:
                    st.write(f" Range: {min(sentiment_values):,.2f} → {max(sentiment_values):,.2f}")
                else:
                    st.warning(" Strategy returned no dates.")

                if sentiment_transactions:
                    df_trades = pd.DataFrame(sentiment_transactions)

                    def highlight(row):
                        if 'Take Profit' in row['action']:
                            return ['background-color: #145A32; color: white'] * len(row)
                        elif 'Stop Loss' in row['action']:
                            return ['background-color: #922B21; color: white'] * len(row)
                        return [''] * len(row)

                    st.dataframe(df_trades.style.apply(highlight, axis=1))
                else:
                    st.info(" No trades triggered.")

                import plotly.graph_objects as go
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=dates, y=sentiment_values, name="Sentiment Strategy"))
                fig.add_trace(go.Scatter(x=spy_df['datetime'], y=portfolio_value * spy_df['close'] / spy_df['close'].iloc[0], name="Buy-and-Hold SPY"))
                fig.add_trace(go.Scatter(x=gold_df['datetime'], y=portfolio_value * gold_df['close'] / gold_df['close'].iloc[0], name="Buy-and-Hold GLD"))
                fig.update_layout(title="Strategy vs. Benchmarks", height=400)
                st.plotly_chart(fig, use_container_width=True)

                value_mapping = {
                    row['date']: val
                    for row, val in zip(pd.DataFrame({'date': dates}).to_dict('records'), sentiment_values)
                }

                display_trade_dropdown(sentiment_transactions, value_mapping)
                st.header("Market Sentiment")
                st.plotly_chart(create_sentiment_gauge(sentiment_score), use_container_width=True)
                st.subheader(sentiment_summary)
                display_news_headlines(article_details)

    with col2:
        display_current_prices(spy_data, gold_data)
        display_world_clock()
        display_countdown_timer()
