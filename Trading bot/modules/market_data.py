"""
market_data.py

Twelve Data Market Data Utilities
---------------------------------

This module provides functions to fetch and process time series market data
from the Twelve Data API for use in Streamlit dashboards and analytical tools.

Key features:
1. fetch_time_series – retrieves historical OHLCV data for a given symbol, interval, and output size
2. get_latest_close – extracts the most recent closing price from fetched data
3. convert_to_dataframe – transforms the raw API JSON into a cleaner pandas DataFrame
4. calculate_normalized_data – computes base‑100 normalized price series for comparative analysis
"""

import requests
import pandas as pd
import streamlit as st
from config import TWELVE_DATA_API_KEY



@st.cache_data(ttl=300)
def fetch_time_series(symbol, interval='1minute', outputsize=30):
    """
    Fetch time series data from Twelve Data API

    Args:
        symbol (str): Stock symbol
        interval (str): Time interval (1min, 5min, 15min, 30min, 1h, 1day)
        outputsize (int): Number of data points

    Returns:
        list: Time series data sorted by datetime

    Tests:
        >>> # Ensure an invalid symbol returns an empty list
        >>> result = fetch_time_series('INVALIDSYM', interval='1day', outputsize=1)
        >>> print('OK') if result == [] else print('bad')
        OK
    """
    url = (
        f"https://api.twelvedata.com/time_series?symbol={symbol}"
        f"&interval={interval}&outputsize={outputsize}&apikey={TWELVE_DATA_API_KEY}"
    )
    try:
        data = requests.get(url).json()
        return sorted(data['values'], key=lambda x: x['datetime']) if 'values' in data else []
    except Exception as e:
        st.error(f"Error fetching data for {symbol}: {e}")
        return []

def get_latest_close(data):
    """
    Get the latest closing price from time series data

    Args:
        data (list): Time series data

    Returns:
        float: Latest closing price or None if data is empty

    Tests:
        >>> # None for empty data
        >>> print('OK') if get_latest_close([]) is None else print('bad')
        OK
        >>> # Returns correct float
        >>> ave = get_latest_close([{'close': '5'}, {'close': '10'}])
        >>> print('OK') if ave == 10.0 else print('bad')
        OK
    """
    return float(data[-1]['close']) if data else None

def convert_to_dataframe(data):
    """
    Convert API data to pandas DataFrame

    Args:
        data (list): Time series data

    Returns:
        DataFrame: Data formatted as pandas DataFrame

    Tests:
        >>> # Empty input
        >>> df_empty = convert_to_dataframe([])
        >>> print('OK') if df_empty.empty else print('bad')
        OK
        >>> # Type conversion check
        >>> sample = [{
        ...     'datetime': '2025-04-22 00:00:00',
        ...     'open': '10', 'high': '20', 'low': '5', 'close': '15', 'volume': '100'
        ... }]
        >>> df = convert_to_dataframe(sample)
        >>> print('OK') if df['close'][0] == 15.0 else print('bad')
        OK
    """
    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data)
    df['datetime'] = pd.to_datetime(df['datetime'])

    for col in ['open', 'high', 'low', 'close', 'volume']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col])

    return df

def calculate_normalized_data(spy_df, gold_df):
    """
    Calculate normalized prices (base 100)

    Args:
        spy_df (DataFrame): SPY data
        gold_df (DataFrame): GLD data

    Returns:
        tuple: Normalized SPY and GLD DataFrames

    Tests:
        >>> import pandas as pd
        >>> spy = pd.DataFrame({'datetime': ['2025-04-22', '2025-04-23'], 'close': [100, 150]})
        >>> spy['datetime'] = pd.to_datetime(spy['datetime'])
        >>> gold = spy.copy()
        >>> spy_n, gold_n = calculate_normalized_data(spy, gold)
        >>> print('OK') if spy_n['normalized'][1] == 150.0 else print('bad')
        OK
    """
    spy_normalized = spy_df.copy()
    gold_normalized = gold_df.copy()

    if not spy_df.empty:
        spy_normalized['normalized'] = spy_normalized['close'] / spy_normalized['close'].iloc[0] * 100

    if not gold_df.empty:
        gold_normalized['normalized'] = gold_normalized['close'] / gold_normalized['close'].iloc[0] * 100

    return spy_normalized, gold_normalized
