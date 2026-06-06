"""Enhanced Stock Analysis Runner — sử dụng Design Patterns.

Central pipeline: tất cả logic phân tích tập trung tại đây.
Các file khác (main.py, scheduler.py) đều gọi qua module này.

Cách chạy:
    python enhanced_runner.py
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Optional

import pandas as pd
from config import FETCH_DAYS, DEFAULT_SYMBOLS, MIN_DATA_DAYS
from crawler import fetch_yfinance, async_save_prices, async_load_prices
from patterns import (
    TechnicalAnalysisStrategy,
    BacktestStrategy,
    AnalysisFactory,
    ObservablePipeline,
    AsyncDatabase,
    SyncDatabase,
    Database,
    ConsoleObserver,
    TelegramObserver,
    FileObserver,
)

logger = logging.getLogger(__name__)


def _calc_score(trend: dict) -> float:
    st = trend.get("ngan_han_1_5_ngay", "")
    if st == "MUA":
        return 1.0
    elif st == "TĂNG_NHẸ":
        return 0.5
    elif st == "GIẢM_NHẸ":
        return -0.5
    elif st == "BÁN":
        return -1.0
    return 0.0


class AnalysisFacade:
    """Facade Pattern — đơn giản hóa toàn bộ quy trình phân tích.

    DI: inject db, tech_strategy, backtest_strategy để dễ test.
    """

    def __init__(
        self,
        symbols: List[str],
        observers: Optional[List[str]] = None,
        n_backtest: int = 10,
        silent: bool = False,
        db: Optional[Database] = None,
        tech_strategy: Optional[TechnicalAnalysisStrategy] = None,
        backtest_strategy: Optional[BacktestStrategy] = None,
    ):
        self.symbols = symbols
        self.silent = silent
        self.pipeline: ObservablePipeline = AnalysisFactory.create_pipeline(observers)
        self.tech_strategy = tech_strategy or TechnicalAnalysisStrategy()
        self.backtest_strategy = backtest_strategy or BacktestStrategy(
            n_tests=n_backtest, db=db
        )
        self.db = db or AsyncDatabase()

    def _log(self, msg: str):
        if not self.silent:
            print(msg)

    async def run(self) -> List[dict]:
        all_results = []
        self._log(f"\n{'='*60}")
        self._log(f"  🚀 StockTech Analysis Engine v2.0")
        self._log(f"  📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        self._log(f"  📊 Phân tích {len(self.symbols)} mã: {', '.join(self.symbols)}")
        self._log(f"{'='*60}\n")

        for symbol in self.symbols:
            result = await self._analyze_symbol(symbol)
            if result:
                all_results.append(result)

        await self.pipeline.notify_pipeline(all_results)
        await self.db.close()
        return all_results

    async def run_symbol(self, symbol: str) -> Optional[dict]:
        return await self._analyze_symbol(symbol)

    async def _analyze_symbol(self, symbol: str) -> Optional[dict]:
        try:
            self._log(f"  🔍 [{symbol}] Crawl dữ liệu...")
            rows = fetch_yfinance(symbol, FETCH_DAYS)
            if not rows:
                logger.warning(f"[{symbol}] Không có dữ liệu")
                return None
            await async_save_prices(rows, self.db if isinstance(self.db, AsyncDatabase) else None)

            prices = await async_load_prices(
                symbol, db=self.db if isinstance(self.db, AsyncDatabase) else None
            )
            if len(prices) < MIN_DATA_DAYS:
                logger.warning(f"[{symbol}] Chỉ có {len(prices)} phiên < {MIN_DATA_DAYS}")
                return None

            df = pd.DataFrame(prices)

            self._log(f"  ⚙️ [{symbol}] Tính toán chỉ báo...")
            prediction = self.tech_strategy.analyze(symbol, df)
            if prediction is None:
                return None

            last_close = float(df["close"].iloc[-1])
            last_date = str(df["date"].iloc[-1])
            trend = prediction.get("trend", {})

            self._log(f"  🔬 [{symbol}] Backtest...")
            backtest = self.backtest_strategy.analyze(symbol, df)

            await self._save_prediction(symbol, prediction, last_close)

            result = {
                "symbol": symbol,
                "last_close": last_close,
                "last_date": last_date,
                "prediction": prediction,
                "backtest": backtest,
                "data_points": len(df),
                "close_price": f"{last_close:,.0f}₫",
                "trend": trend,
            }

            await self.pipeline.notify_analysis(symbol, prediction)
            await self.pipeline.notify_backtest(symbol, backtest)
            return result

        except Exception as e:
            logger.error(f"[{symbol}] Lỗi: {e}", exc_info=True)
            return None

    async def _save_prediction(self, symbol: str, prediction: dict, close_price: float):
        trend = prediction.get("trend", {})
        score = _calc_score(trend)
        sql = """INSERT INTO prediction_history
                 (symbol, run_date, close_price, short_term, medium_term, long_term, signal_score)
                 VALUES (?, ?, ?, ?, ?, ?, ?)"""
        params = (
            symbol, datetime.now().isoformat(), close_price,
            trend.get("ngan_han_1_5_ngay", ""),
            trend.get("trung_han_5_20_ngay", ""),
            trend.get("dai_han_20_50_ngay", ""), score,
        )
        if isinstance(self.db, AsyncDatabase):
            await self.db.execute(sql, params)
            await self.db.commit()
        else:
            self.db.execute(sql, params)
            self.db.commit()


def run_pipeline_sync(symbols: Optional[List[str]] = None,
                      observers: Optional[List[str]] = None,
                      silent: bool = False) -> List[dict]:
    if symbols is None:
        symbols = DEFAULT_SYMBOLS
    facade = AnalysisFacade(
        symbols=symbols, observers=observers, silent=silent, db=SyncDatabase(),
    )
    return asyncio.run(facade.run())


async def main():
    symbols = ["ACB", "VCB", "FPT", "HPG", "MWG"]
    facade = AnalysisFacade(symbols=symbols, observers=["console", "telegram", "file"])
    results = await facade.run()

    if results:
        print(f"\n{'='*60}")
        print(f"  ✅ PHÂN TÍCH HOÀN TẤT — {len(results)}/{len(symbols)} mã thành công")
        print(f"{'='*60}")
    else:
        print("\n❌ Không có mã nào được phân tích thành công!")

    print(f"\n{'='*80}")
    print(f"  📊 BẢNG TỔNG KẾT")
    print(f"{'='*80}")
    print(f"  {'Mã':8s} {'Giá':12s} {'Ngắn hạn':20s} {'Tự tin':8s} {'Đúng/TS':10s} {'TLệ%':6s}")
    print(f"  {'-'*8} {'-'*12} {'-'*20} {'-'*8} {'-'*10} {'-'*6}")
    for r in results:
        trend = r.get("trend", {})
        st = trend.get("ngan_han_1_5_ngay", "N/A")
        conf = r.get("prediction", {}).get("confidence", {}).get("short_term", 0)
        conf_str = f"{conf:.0f}%" if conf else "N/A"
        bt = r.get("backtest", {})
        if bt and bt.get("total", 0) > 0:
            acc_str = f"{bt['correct']}/{bt['total']}"
            pct_str = f"{bt['accuracy']:.0f}%"
        else:
            acc_str = "N/A"
            pct_str = "N/A"
        print(f"  {r['symbol']:8s} {r.get('close_price', 'N/A'):12s} {st:20s} {conf_str:8s} {acc_str:10s} {pct_str:6s}")
    print(f"{'='*80}\n")
    return results


if __name__ == "__main__":
    asyncio.run(main())
