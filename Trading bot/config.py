"""
Configuration Constants
-----------------------

This module centralizes configuration settings and constants used throughout the
Trading Dashboard application, including API keys, trading parameters, sentiment
thresholds, global market time mappings, market hours, and default dashboard values.

Key features:
1. API keys for Twelve Data and NewsAPI
2. Profit-taking and stop-loss percentages with the cash allocation
3. Bullish and bearish sentiment thresholds
4. Timezone mappings for major financial centers
5. NYSE market open/close hours in New York time
6. Default portfolio value

Tests:
    >>> from config import (
    ...     TWELVE_DATA_API_KEY, NEWS_API_KEY, FINNHUB_API_KEY,
    ...     PROFIT_TAKING, STOP_LOSS, CASH_ALLOCATION,
    ...     BULLISH_THRESHOLD, BEARISH_THRESHOLD,
    ...     WORLD_CLOCK_CITIES,
    ...     MARKET_OPEN_HOUR, MARKET_OPEN_MINUTE,
    ...     MARKET_CLOSE_HOUR, MARKET_CLOSE_MINUTE,
    ...     DEFAULT_PORTFOLIO_VALUE
    ... )
    >>> # API keys should be non-empty strings
    >>> print('OK') if isinstance(TWELVE_DATA_API_KEY, str) and TWELVE_DATA_API_KEY else print('bad')
    OK
    >>> print('OK') if isinstance(NEWS_API_KEY, str) and NEWS_API_KEY else print('bad')
    OK
    >>> print('OK') if isinstance(FINNHUB_API_KEY, str) and FINNHUB_API_KEY else print('bad')
    OK

    >>> # Trading parameters match expected values
    >>> print('OK') if PROFIT_TAKING == 11.75 and STOP_LOSS == 2.25 else print('bad')
    OK
    >>> print('OK') if 0 < CASH_ALLOCATION < 1 else print('bad')
    OK

    >>> # Sentiment thresholds
    >>> print('OK') if BULLISH_THRESHOLD == 0.05 and BEARISH_THRESHOLD == 0.3 else print('bad')
    OK

    >>> # World clock cities mapping
    >>> print('OK') if WORLD_CLOCK_CITIES.get("New York") == "America/New_York" else print('bad')
    OK
    >>> print('OK') if "Tokyo" in WORLD_CLOCK_CITIES and WORLD_CLOCK_CITIES["Tokyo"] == "Asia/Tokyo" else print('bad')
    OK

    >>> # Market hours in New York
    >>> print('OK') if (MARKET_OPEN_HOUR, MARKET_OPEN_MINUTE, MARKET_CLOSE_HOUR, MARKET_CLOSE_MINUTE) == (9, 30, 16, 0) else print('bad')
    OK

    >>> # Default portfolio value
    >>> print('OK') if DEFAULT_PORTFOLIO_VALUE == 1000000.0 else print('bad')
    OK
"""

# API keys
TWELVE_DATA_API_KEY = 'Enter your Twelvedata API key'
NEWS_API_KEY = 'Enter your News API key'
FINNHUB_API_KEY = 'Enter your FINNHUB API key'

# Trading parameters
PROFIT_TAKING = 11.75
STOP_LOSS = 4.25
CASH_ALLOCATION = 0.2

# Sentiment thresholds
BULLISH_THRESHOLD = 0.05
BEARISH_THRESHOLD = 0.3

# World clock cities
WORLD_CLOCK_CITIES = {
    "New York": "America/New_York",
    "London": "Europe/London",
    "Tokyo": "Asia/Tokyo",
    "Hong Kong": "Asia/Hong_Kong",
    "Sydney": "Australia/Sydney",
    "Zurich": "Europe/Zurich"
}

# Market hours (New York time)
MARKET_OPEN_HOUR = 9
MARKET_OPEN_MINUTE = 30
MARKET_CLOSE_HOUR = 16
MARKET_CLOSE_MINUTE = 0

# Default dashboard values
DEFAULT_PORTFOLIO_VALUE = 1000000.0
