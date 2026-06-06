from datetime import datetime, timedelta
from typing import List, Optional

import yfinance as yf
import pandas as pd
from config import FETCH_DAYS
from patterns import SyncDatabase, AsyncDatabase, Database


def get_db() -> SyncDatabase:
    return SyncDatabase()


# ==================== Sync versions ====================

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


def save_prices(rows: List[dict], db: Optional[Database] = None):
    if not rows:
        return
    db = db or SyncDatabase()
    conn = db.get_connection()
    conn.executemany(
        """INSERT OR REPLACE INTO stock_prices
           (symbol, date, open, high, low, close, volume)
           VALUES (:symbol, :date, :open, :high, :low, :close, :volume)""",
        rows,
    )
    conn.commit()


def load_prices(symbol: str, limit: int = 500, db: Optional[Database] = None) -> List[dict]:
    db = db or SyncDatabase()
    return db.fetchall(
        """SELECT date, open, high, low, close, volume
           FROM stock_prices WHERE symbol = ?
           ORDER BY date ASC LIMIT ?""",
        (symbol, limit),
    )


def get_symbols_in_db(db: Optional[Database] = None) -> List[str]:
    db = db or SyncDatabase()
    rows = db.fetchall("SELECT DISTINCT symbol FROM stock_prices")
    return [r["symbol"] for r in rows]


def get_latest_date(symbol: str, db: Optional[Database] = None) -> Optional[str]:
    db = db or SyncDatabase()
    row = db.fetchone(
        "SELECT MAX(date) AS max_date FROM stock_prices WHERE symbol = ?", (symbol,)
    )
    return row["max_date"] if row else None


# ==================== Async versions ====================

async def async_save_prices(rows: List[dict], db: Optional[AsyncDatabase] = None):
    if not rows:
        return
    db = db or AsyncDatabase()
    await db.executemany(
        """INSERT OR REPLACE INTO stock_prices
           (symbol, date, open, high, low, close, volume)
           VALUES (:symbol, :date, :open, :high, :low, :close, :volume)""",
        rows,
    )
    await db.commit()


async def async_load_prices(symbol: str, limit: int = 500, db: Optional[AsyncDatabase] = None) -> List[dict]:
    db = db or AsyncDatabase()
    return await db.fetchall(
        """SELECT date, open, high, low, close, volume
           FROM stock_prices WHERE symbol = ?
           ORDER BY date ASC LIMIT ?""",
        (symbol, limit),
    )
