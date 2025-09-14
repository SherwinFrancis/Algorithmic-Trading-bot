"""
Sentiment Strategy Backtest
---------------------------

This module simulates and evaluates a sentiment‑driven trading strategy on SPY and GLD
using synthetic alternating sentiment signals over a 5‑day cycle. It allocates capital
with reserved cash buffers, executes buy/sell decisions based on bullish and bearish
thresholds, applies take‑profit and stop‑loss rules, and tracks both portfolio value
over time and detailed transaction history.

Key features:
1. Alternating sentiment simulation for SPY and GLD
2. Automatic take‑profit and stop‑loss execution
3. Buy and sell signals triggered by configurable sentiment thresholds
4. Capital allocation with reserved buffers for each asset
5. Generation of portfolio value time series and comprehensive transaction logs

"""

def sentiment_strategy_backtest(
    spy_df,
    gld_df,
    initial_portfolio=10000,
    take_profit=0.1175,
    stop_loss=0.0225,
    bullish_threshold=0.05,
    bearish_threshold=-0.3
):
    """
    Args:
        spy_df (DataFrame): SPY price data with 'datetime' and 'close' columns.
        gld_df (DataFrame): GLD price data with 'datetime' and 'close' columns.
        initial_portfolio (float): Starting capital for the backtest.
        take_profit (float): Profit-taking threshold ratio (e.g., 0.09 for 9%).
        stop_loss (float): Stop-loss threshold ratio (e.g., 0.05 for 5%).
        bullish_threshold (float): Sentiment value above which to enter long.
        bearish_threshold (float): Sentiment value below which to exit/short.

    Returns:
        tuple:
            - list[datetime]: Timestamps of each data point processed.
            - list[float]: Total portfolio value at each timestamp.
            - list[dict]: Transaction records.

    Tests:
        >>> import pandas as pd
        >>> from datetime import datetime
        >>> # 1) Empty inputs should yield empty outputs
        >>> empty = pd.DataFrame(columns=['datetime', 'close'])
        >>> times, values, txs = sentiment_strategy_backtest(empty, empty)
        >>> print('OK') if times == [] and values == [] and txs == [] else print('bad')
        OK

        >>> # 2) Single date, price so high no shares can be bought -> no trades, flat value
        >>> df = pd.DataFrame({
        ...     'datetime': [datetime(2025, 4, 23)],
        ...     'close': [10000.0]
        ... })
        >>> times, values, txs = sentiment_strategy_backtest(df, df, initial_portfolio=10000)
        >>> print('OK') if times == [datetime(2025, 4, 23)] else print('bad')
        OK
        >>> print('OK') if values == [10000.0] else print('bad')
        OK
        >>> print('OK') if txs == [] else print('bad')
        OK
    """
    # Capital allocation and holdings
    results = []
    transactions = []

    half = initial_portfolio / 2
    spy_cash = half - 100
    gld_cash = half - 100
    spy_reserved = 100
    gld_reserved = 100

    spy_shares, spy_entry = 0, None
    gld_shares, gld_entry = 0, None

    # Merge on datetime
    df = (
        spy_df.set_index('datetime')['close'].to_frame('spy')
        .join(gld_df.set_index('datetime')['close'].to_frame('gld'), how='inner')
        .reset_index()
    )

    # Early exit if no data
    if df.empty:
        return [], [], []

    # Simulated alternating sentiment
    dates = df['datetime'].dt.strftime('%Y-%m-%d').tolist()
    sentiment_spy = {}
    sentiment_gld = {}
    for i, d in enumerate(sorted(set(dates))):
        cycle = i % 5
        sentiment_spy[d] = -0.2 if cycle < 2 else (0.2 if cycle < 4 else 0.0)
        sentiment_gld[d] = 0.2 if cycle < 2 else (-0.2 if cycle < 4 else 0.0)

    # Main loop
    for row in df.itertuples(index=False):
        date, spy_price, gld_price = row.datetime, row.spy, row.gld
        key = date.strftime('%Y-%m-%d')
        spy_sent = sentiment_spy.get(key, 0)
        gld_sent = sentiment_gld.get(key, 0)

        # Profit / stop‐loss checks for existing positions
        if spy_shares > 0 and spy_entry is not None:
            spy_ret = (spy_price - spy_entry) / spy_entry
            if spy_ret >= take_profit or spy_ret <= -stop_loss:
                action = 'Take Profit' if spy_ret >= take_profit else 'Stop Loss'
                val = spy_shares * spy_price
                spy_cash += val
                transactions.append({
                    'date': date, 'symbol': 'SPY', 'action': action,
                    'shares': spy_shares, 'price': spy_price, 'value': val,
                    'return_pct': spy_ret * 100
                })
                spy_shares = 0
                spy_entry = None

        if gld_shares > 0 and gld_entry is not None:
            gld_ret = (gld_price - gld_entry) / gld_entry
            if gld_ret >= take_profit or gld_ret <= -stop_loss:
                action = 'Take Profit' if gld_ret >= take_profit else 'Stop Loss'
                val = gld_shares * gld_price
                gld_cash += val
                transactions.append({
                    'date': date, 'symbol': 'GLD', 'action': action,
                    'shares': gld_shares, 'price': gld_price, 'value': val,
                    'return_pct': gld_ret * 100
                })
                gld_shares = 0
                gld_entry = None

        # Entry / exit signals based on sentiment
        if spy_sent > bullish_threshold and spy_shares == 0:
            shares = int(spy_cash // spy_price)
            if shares:
                cost = shares * spy_price
                spy_cash -= cost
                spy_shares = shares
                spy_entry = spy_price
                transactions.append({
                    'date': date, 'symbol': 'SPY', 'action': 'Buy',
                    'shares': shares, 'price': spy_price, 'value': cost
                })
        elif spy_sent < bearish_threshold and spy_shares > 0:
            proceeds = spy_shares * spy_price
            pnl = (spy_price - spy_entry) / spy_entry * 100 if spy_entry else 0
            spy_cash += proceeds
            transactions.append({
                'date': date, 'symbol': 'SPY', 'action': 'Sell',
                'shares': spy_shares, 'price': spy_price, 'value': proceeds,
                'return_pct': pnl
            })
            spy_shares = 0
            spy_entry = None

        if gld_sent > bullish_threshold and gld_shares == 0:
            shares = int(gld_cash // gld_price)
            if shares:
                cost = shares * gld_price
                gld_cash -= cost
                gld_shares = shares
                gld_entry = gld_price
                transactions.append({
                    'date': date, 'symbol': 'GLD', 'action': 'Buy',
                    'shares': shares, 'price': gld_price, 'value': cost
                })
        elif gld_sent < bearish_threshold and gld_shares > 0:
            proceeds = gld_shares * gld_price
            pnl = (gld_price - gld_entry) / gld_entry * 100 if gld_entry else 0
            gld_cash += proceeds
            transactions.append({
                'date': date, 'symbol': 'GLD', 'action': 'Sell',
                'shares': gld_shares, 'price': gld_price, 'value': proceeds,
                'return_pct': pnl
            })
            gld_shares = 0
            gld_entry = None

        # Record total value
        total = (
            spy_cash + spy_shares * spy_price + spy_reserved +
            gld_cash + gld_shares * gld_price + gld_reserved
        )
        results.append({'date': date, 'value': total})

    return df['datetime'].tolist(), [r['value'] for r in results], transactions
