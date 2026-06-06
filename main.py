"""FastAPI app - API phân tích kỹ thuật chứng khoán."""

import asyncio
import logging
import sys
from datetime import datetime
from typing import Dict, List

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import (API_HOST, API_PORT, DEFAULT_SYMBOLS,
                    PIPELINE_HOUR, PIPELINE_MINUTE)
from enhanced_runner import AnalysisFacade
from telegram_bot import send_prediction

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("app.log"),
    ],
)
logger = logging.getLogger(__name__)

app = FastAPI(title="StockTech Analysis API", version="2.0")
scheduler = AsyncIOScheduler()


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "timestamp": datetime.now().isoformat(),
        },
    )

prediction_cache: Dict[str, dict] = {}


def _make_facade(symbols: List[str]) -> AnalysisFacade:
    return AnalysisFacade(
        symbols=symbols,
        observers=["telegram", "file"],
        silent=True
    )


async def run_full_pipeline(symbols: List[str] = None):
    global prediction_cache
    facade = _make_facade(symbols or DEFAULT_SYMBOLS)
    results = await facade.run()
    for r in results:
        symbol = r["symbol"]
        prediction_cache[symbol] = r["prediction"]
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
    facade = _make_facade([symbol])
    result = await facade.run_symbol(symbol)
    if result:
        prediction_cache[symbol] = result["prediction"]
        return {"symbol": symbol, "prediction": result["prediction"]}
    raise HTTPException(status_code=404, detail=f"Không có dữ liệu cho {symbol}")


@app.post("/api/run-pipeline")
async def trigger_pipeline(symbols: str = Query("", description="Danh sách mã, cách nhau bằng dấu phẩy")):
    sym_list = [s.strip().upper() for s in symbols.split(",") if s.strip()] if symbols else DEFAULT_SYMBOLS
    asyncio.ensure_future(run_full_pipeline(sym_list))
    return {"status": "started", "symbols": sym_list}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=API_HOST, port=API_PORT, reload=False)
