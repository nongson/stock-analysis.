"""FastAPI app - API phân tích kỹ thuật chứng khoán."""

import asyncio
import json
import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import (API_HOST, API_PORT, DEFAULT_SYMBOLS,
                    PIPELINE_HOUR, PIPELINE_MINUTE, MIN_DATA_DAYS)
from crawler import crawl_symbol, save_prices, load_prices
from indicators import compute_indicators
from predictor import analyze_trends
from telegram_bot import send_prediction

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="StockTech Analysis API", version="1.0")
scheduler = AsyncIOScheduler()

# In-memory cache cho kết quả dự đoán
prediction_cache: Dict[str, dict] = {}


async def run_pipeline_for_symbol(symbol: str) -> Optional[dict]:
    try:
        logger.info(f"[{symbol}] Crawling data...")
        rows = await crawl_symbol(symbol)
        if not rows:
            logger.warning(f"[{symbol}] No data")
            return None
        save_prices(rows)
        prices = load_prices(symbol)
        if len(prices) < MIN_DATA_DAYS:
            logger.warning(f"[{symbol}] Only {len(prices)} records")
            return None
        df = pd.DataFrame(prices).dropna(subset=["open", "high", "low", "close", "volume"])
        if len(df) < MIN_DATA_DAYS:
            return None
        df["close"] = df["close"].astype(float)
        df["high"] = df["high"].astype(float)
        df["low"] = df["low"].astype(float)
        df["volume"] = df["volume"].astype(float)
        indicators = compute_indicators(df)
        result = analyze_trends(indicators)
        result["_updated_at"] = datetime.now().isoformat()
        return result
    except Exception as e:
        logger.error(f"[{symbol}] Error: {e}")
        return None


async def run_full_pipeline(symbols: List[str] = None):
    global prediction_cache
    if symbols is None:
        symbols = DEFAULT_SYMBOLS
    logger.info(f"Running pipeline for {len(symbols)} symbols")
    results = {}
    for symbol in symbols:
        result = await run_pipeline_for_symbol(symbol)
        if result:
            results[symbol] = result
            await send_prediction(symbol, result)
    prediction_cache.update(results)
    return results


@app.on_event("startup")
async def startup():
    scheduler.add_job(
        run_full_pipeline,
        "cron",
        hour=PIPELINE_HOUR,
        minute=PIPELINE_MINUTE,
        id="daily_pipeline",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(f"Scheduler started: daily at {PIPELINE_HOUR:02d}:{PIPELINE_MINUTE:02d}")
    await run_full_pipeline()


@app.on_event("shutdown")
async def shutdown():
    scheduler.shutdown()


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "time": datetime.now().isoformat(),
        "cached_symbols": list(prediction_cache.keys()),
    }


@app.get("/api/predictions")
async def get_all_predictions():
    return {"predictions": prediction_cache, "count": len(prediction_cache)}


@app.get("/api/predictions/{symbol}")
async def get_prediction(symbol: str):
    symbol = symbol.upper()
    if symbol in prediction_cache:
        return {"symbol": symbol, "prediction": prediction_cache[symbol]}
    result = await run_pipeline_for_symbol(symbol)
    if result:
        prediction_cache[symbol] = result
        return {"symbol": symbol, "prediction": result}
    raise HTTPException(status_code=404, detail=f"Không có dữ liệu cho {symbol}")


@app.post("/api/run-pipeline")
async def trigger_pipeline(symbols: str = Query("", description="Danh sách mã, cách nhau bằng dấu phẩy")):
    sym_list = [s.strip().upper() for s in symbols.split(",") if s.strip()] if symbols else DEFAULT_SYMBOLS
    asyncio.ensure_future(run_full_pipeline(sym_list))
    return {"status": "started", "symbols": sym_list}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=API_HOST, port=API_PORT, reload=False)
