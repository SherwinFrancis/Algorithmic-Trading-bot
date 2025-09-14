"""
Market Sentiment Analysis
------------------------
This module implements a news-based market sentiment analysis system that evaluates
current market sentiment by analyzing business headlines.

Key features:
1. Retrieves recent business news headlines from the News API
2. Performs natural language processing(sentiment analysis**) to calculate sentiment scores
3. Categorizes market sentiment as Bullish, Bearish, or Neutral depending on the sentiment_scores
4. Caches results to minimize API usage and improve dashboard performance
5. Provides detailed article information for further manual analysis if required

**The sentiment analysis uses TextBlob to evaluate the emotional tone of headlines,
which can serve as a leading indicator for market movements and inform investment decisions.
"""

import requests
from textblob import TextBlob
from datetime import datetime, timedelta
from typing import Tuple, List, Dict
from config import NEWS_API_KEY, BULLISH_THRESHOLD, BEARISH_THRESHOLD
import streamlit as st

NEWS_API_KEY = 'd4eeac3a7bf24bd1aaf6f0021b6342cc'

# Trading parameters
PROFIT_TAKING = 11.75
STOP_LOSS = 2.25
CASH_ALLOCATION = 0.2

# Sentiment thresholds
BULLISH_THRESHOLD = 0.05
BEARISH_THRESHOLD = 0.3



def get_current_market_sentiment(asset: str = None) -> Tuple[float, str, List[Dict]]:
    """
    Fetch market sentiment based on business or asset-specific news headlines.

    Args:
        asset: Optional ticker or keyword to filter headlines (e.g. "SPY", "GLD", "gold").
               If None, pulls general business headlines.

    Returns:
        avg_score    : float polarity average [-1, +1]
        summary      : " Bullish", " Neutral", or " Bearish"
        article_list : list of {title, url, source, sentiment}

    Tests:
        >>> # When no matching articles are returned, should get default values
        >>> avg, summary, details = get_current_market_sentiment("NOSUCHASSET")
        >>> print('OK') if avg == 0.0 and summary == " No news available" and details == [] else print('bad')
        OK
    """
    base = "https://newsapi.org/v2"
    if asset:
        url = f"{base}/everything"
        params = {
            "q": asset,
            "from": (datetime.utcnow() - timedelta(days=1)).isoformat(),
            "to": datetime.utcnow().isoformat(),
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": 20,
            "apiKey": NEWS_API_KEY,
        }
    else:
        url = f"{base}/top-headlines"
        params = {
            "category": "business",
            "language": "en",
            "pageSize": 20,
            "apiKey": NEWS_API_KEY,
        }

    resp = requests.get(url, params=params)
    resp.raise_for_status()
    data = resp.json().get("articles", [])

    if not data:
        return 0.0, " No news available", []

    scores = []
    details = []
    for art in data:
        title = art.get("title", "")
        polarity = TextBlob(title).sentiment.polarity
        scores.append(polarity)
        details.append({
            "title": title,
            "url":   art.get("url", ""),
            "source": art.get("source", {}).get("name", "Unknown"),
            "sentiment": polarity,
        })

    avg = sum(scores) / len(scores)
    if avg > BULLISH_THRESHOLD:
        sum_of_sentiment = " Bullish"
    elif avg < BEARISH_THRESHOLD:
        sum_of_sentiment = " Bearish"
    else:
        sum_of_sentiment = " Neutral"

    return avg, sum_of_sentiment, details


@st.cache_data(ttl=86400)
def historical_market_sentiment(date: str, asset: str) -> Tuple[float, str, List[Dict]]:
    """
    Fetch market sentiment for a given asset on a specific date.

    Args:
        date (str): Date in ISO format (YYYY-MM-DD) for which to fetch headlines.
        asset (str): Asset keyword to search in news (e.g. "Tesla", "gold", "BTC").

    Returns:
        tuple: (avg_score, sentiment_summary, article_details)

    Tests:
        >>> # Future date or no articles returns defaults
        >>> result = historical_market_sentiment('2100-01-01', 'INVALID_ASSET')
        >>> print('OK') if result == (0, " No articles found for that date/asset.", []) else print('bad')
        OK
    """
    # Build NewsAPI query for that single day
    url = (
        "https://newsapi.org/v2/everything"
        f"?q={asset}"
        f"&from={date}&to={date}"
        "&language=en"
        "&sortBy=publishedAt"
        f"&apiKey={NEWS_API_KEY}"
    )

    try:
        response = requests.get(url)
        response.raise_for_status()
        articles = response.json().get("articles", [])

        if not articles:
            return 0, " No articles found for that date/asset.", []

        scores = []
        article_details = []

        # limit to first 10 to keep parity with current function
        for article in articles[:10]:
            title = article.get("title", "")
            polarity = TextBlob(title).sentiment.polarity
            scores.append(polarity)
            article_details.append({
                "title": title,
                "url": article.get("url", ""),
                "source": article.get("source", {}).get("name", "Unknown"),
                "sentiment": polarity
            })

        avg_score = sum(scores) / len(scores)

        if avg_score > BULLISH_THRESHOLD:
            summary = " Bullish"
        elif avg_score < BEARISH_THRESHOLD:
            summary = " Bearish"
        else:
            summary = " Neutral"

        return avg_score, summary, article_details

    except requests.RequestException as e:
        st.error(f"Network error fetching historical sentiment: {e}")
        return 0, " Error", []
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return 0, " Error", []
