import sqlite3
from datetime import datetime, timedelta
from typing import List, Optional

import yfinance as yf
import pandas as pd
from config import DB_PATH, FETCH_DAYS


def get_db_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS stock_prices (
            symbol TEXT NOT NULL,
            date TEXT NOT NULL,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER,
            PRIMARY KEY (symbol, date)
        )
    """)
    conn.commit()
    return conn


def fetch_yfinance(symbol: str, days: int = FETCH_DAYS) -> List[dict]:
    end = datetime.now()
    start = end - timedelta(days=days)
    yf_symbol = f"{symbol}.VN"
    ticker = yf.Ticker(yf_symbol)
    df = ticker.history(start=start.strftime("%Y-%m-%d"), end=end.strftime("%Y-%m-%d"))
    if df.empty:
        return []
    rows = []
    for date_idx, row in df.iterrows():
        rows.append({
            "symbol": symbol,
            "date": pd.Timestamp(date_idx).strftime("%Y-%m-%d"),
            "open": round(float(row["Open"]), 2),
            "high": round(float(row["High"]), 2),
            "low": round(float(row["Low"]), 2),
            "close": round(float(row["Close"]), 2),
            "volume": int(row["Volume"]),
        })
    return rows


async def crawl_symbol(symbol: str, days: int = FETCH_DAYS) -> List[dict]:
    return fetch_yfinance(symbol, days)


def save_prices(rows: List[dict]):
    if not rows:
        return
    conn = get_db_connection()
    conn.executemany(
        """INSERT OR REPLACE INTO stock_prices
           (symbol, date, open, high, low, close, volume)
           VALUES (:symbol, :date, :open, :high, :low, :close, :volume)""",
        rows,
    )
    conn.commit()
    conn.close()


def load_prices(symbol: str, limit: int = 500) -> List[dict]:
    conn = get_db_connection()
    cur = conn.execute(
        """SELECT date, open, high, low, close, volume
           FROM stock_prices WHERE symbol = ?
           ORDER BY date ASC LIMIT ?""",
        (symbol, limit),
    )
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows


def get_symbols_in_db() -> List[str]:
    conn = get_db_connection()
    cur = conn.execute("SELECT DISTINCT symbol FROM stock_prices")
    symbols = [row[0] for row in cur.fetchall()]
    conn.close()
    return symbols


def get_latest_date(symbol: str) -> Optional[str]:
    conn = get_db_connection()
    cur = conn.execute(
        "SELECT MAX(date) FROM stock_prices WHERE symbol = ?", (symbol,)
    )
    row = cur.fetchone()
    conn.close()
    return row[0] if row else None
