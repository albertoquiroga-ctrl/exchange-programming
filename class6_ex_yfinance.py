"""Question 1 requirements (keep for easy reference inside the file).

1. Install `yfinance` with `py -m pip install yfinance`.
2. Provide `get_price_lastweek(ticker)` that fetches Monday–Friday prices for last week.
3. Call that function for AAPL, MSFT, NVDA, TSLA, MS, GS.
4. Report which ticker delivered the highest return (Friday close ÷ Monday open).

Below implements the solution and prints the requested information.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Dict, cast

import pandas as pd
import yfinance as yf


def _last_week_range(reference: date | None = None) -> tuple[date, date]:
    """Return the Monday and Friday dates for the previous full work week."""
    if reference is None:
        reference = datetime.now(timezone.utc).date()
    # Monday is 0 and Sunday is 6; subtract to reach current week's Monday.
    current_week_monday = reference - timedelta(days=reference.weekday())
    last_week_monday = current_week_monday - timedelta(days=7)
    last_week_friday = last_week_monday + timedelta(days=4)
    return last_week_monday, last_week_friday


def get_price_lastweek(ticker: str) -> pd.DataFrame:
    """Download OHLC data for the ticker covering last week's trading days.

    Implements Step 2 by pulling the raw prices and keeping only the target week.
    """
    monday, friday = _last_week_range()
    # Step 2: download daily candles for the prior week using yfinance.
    raw_df = yf.download(
        ticker,
        start=monday.isoformat(),
        end=(friday + timedelta(days=1)).isoformat(),
        interval="1d",
        auto_adjust=False,
        progress=False,
    )

    if raw_df is None or raw_df.empty:
        raise ValueError(f"No price data returned for {ticker} between {monday} and {friday}.")

    df = cast(pd.DataFrame, raw_df).copy()

    # Clean up index/columns so downstream logic gets predictable structures.
    df.index = pd.DatetimeIndex(pd.to_datetime(df.index).tz_localize(None))
    df = df.sort_index()
    dt_index = cast(pd.DatetimeIndex, df.index)

    if isinstance(df.columns, pd.MultiIndex):
        df = df.droplevel("Ticker", axis=1)

    start_ts = pd.Timestamp(monday)
    end_ts = pd.Timestamp(friday)
    normalized_index = dt_index.normalize()
    date_mask = (normalized_index >= start_ts) & (normalized_index <= end_ts)
    weekday_mask = dt_index.dayofweek <= 4
    df = df.loc[date_mask & weekday_mask]

    if df.empty:
        raise ValueError(f"No weekday price data returned for {ticker} in the prior week.")

    return df[["Open", "Close"]]


def compute_weekly_returns(tickers: list[str]) -> Dict[str, float]:
    """Calculate weekly returns for each ticker based on Monday open and Friday close.

    Addresses the return calculation needed for Step 4.
    """
    returns: Dict[str, float] = {}
    for ticker in tickers:
        prices = get_price_lastweek(ticker)
        # Use first and last available trading days in case of holidays.
        monday_open = float(prices.iloc[0]["Open"])
        friday_close = float(prices.iloc[-1]["Close"])
        returns[ticker] = (friday_close / monday_open) - 1
    return returns


if __name__ == "__main__":
    # Step 3: gather weekly prices for each requested ticker.
    watchlist = ["AAPL", "MSFT", "NVDA", "TSLA", "MS", "GS"]

    for symbol in watchlist:
        weekly_prices = get_price_lastweek(symbol)
        print(f"\n{symbol} prices last week:")
        print(weekly_prices)

    # Step 4: compute and compare returns, then announce the top performer.
    weekly_returns = compute_weekly_returns(watchlist)
    print("\nWeekly returns (Friday close over Monday open):")
    for symbol, rtn in weekly_returns.items():
        print(f"{symbol}: {rtn:.2%}")

    top_ticker = max(watchlist, key=lambda ticker: weekly_returns[ticker])
    print(f"\nHighest return last week: {top_ticker} at {weekly_returns[top_ticker]:.2%}")
