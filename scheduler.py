"""Cronjob chạy pipeline lúc 2h sáng mỗi ngày."""

import asyncio
import logging
from datetime import datetime
from typing import List

from config import DEFAULT_SYMBOLS, MIN_DATA_DAYS
from crawler import crawl_symbol, save_prices, load_prices, get_symbols_in_db
from indicators import compute_indicators
from predictor import analyze_trends
from telegram_bot import send_prediction

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def run_pipeline(symbols: List[str] = None):
    if symbols is None:
        symbols = DEFAULT_SYMBOLS
    logger.info(f"=== BẮT ĐẦU PIPELINE: {datetime.now()} ===")
    logger.info(f"Theo dõi {len(symbols)} mã: {', '.join(symbols)}")

    all_results = {}

    for symbol in symbols:
        try:
            logger.info(f"[{symbol}] Đang crawl dữ liệu...")
            rows = await crawl_symbol(symbol)
            if not rows:
                logger.warning(f"[{symbol}] Không có dữ liệu, bỏ qua")
                continue
            save_prices(rows)
            logger.info(f"[{symbol}] Đã lưu {len(rows)} bản ghi")

            prices = load_prices(symbol)
            if len(prices) < MIN_DATA_DAYS:
                logger.warning(f"[{symbol}] Chỉ có {len(prices)} phiếu < {MIN_DATA_DAYS}, bỏ qua")
                continue

            import pandas as pd
            df = pd.DataFrame(prices)
            df = df.dropna(subset=["open", "high", "low", "close", "volume"])
            if len(df) < MIN_DATA_DAYS:
                continue
            df["close"] = df["close"].astype(float)
            df["high"] = df["high"].astype(float)
            df["low"] = df["low"].astype(float)
            df["volume"] = df["volume"].astype(float)

            logger.info(f"[{symbol}] Tính toán chỉ báo...")
            indicators = compute_indicators(df)

            logger.info(f"[{symbol}] Phân tích xu thế...")
            result = analyze_trends(indicators)
            all_results[symbol] = result

            await send_prediction(symbol, result)

        except Exception as e:
            logger.error(f"[{symbol}] Lỗi: {e}")

    logger.info(f"=== KẾT THÚC PIPELINE: {datetime.now()} ===")
    return all_results


def run_pipeline_sync():
    asyncio.run(run_pipeline())
