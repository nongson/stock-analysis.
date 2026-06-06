"""Enhanced Stock Analysis Runner — sử dụng Design Patterns.

Chạy phân tích toàn diện với:
- Strategy Pattern: TechnicalAnalysis + Backtest
- Observer Pattern: Telegram + File + Console
- Factory Pattern: Pipeline factory
- Singleton Pattern: Database
- Facade Pattern: Simplified run interface

Cách chạy:
    python enhanced_runner.py
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Optional

import pandas as pd
from config import FETCH_DAYS
from crawler import fetch_yfinance, save_prices, load_prices
from patterns import (
    TechnicalAnalysisStrategy,
    BacktestStrategy,
    AnalysisFactory,
    ObservablePipeline,
    DatabaseSingleton,
    ConsoleObserver,
    TelegramObserver,
    FileObserver,
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


class AnalysisFacade:
    """Facade Pattern — đơn giản hóa toàn bộ quy trình phân tích."""

    def __init__(self, symbols: List[str], observers: Optional[List[str]] = None):
        self.symbols = symbols
        self.pipeline: ObservablePipeline = AnalysisFactory.create_pipeline(observers)
        self.tech_strategy = TechnicalAnalysisStrategy()
        self.backtest_strategy = BacktestStrategy(n_tests=10)
        self.db = DatabaseSingleton()

    async def run(self) -> List[dict]:
        all_results = []
        print(f"\n{'='*60}")
        print(f"  🚀 StockTech Enhanced Analysis Engine v2.0")
        print(f"  📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        print(f"  📊 Phân tích {len(self.symbols)} mã: {', '.join(self.symbols)}")
        print(f"{'='*60}\n")

        for symbol in self.symbols:
            result = await self._analyze_symbol(symbol)
            if result:
                all_results.append(result)

        await self.pipeline.notify_pipeline(all_results)
        self.db.close()
        return all_results

    async def _analyze_symbol(self, symbol: str) -> Optional[dict]:
        try:
            print(f"\n  🔍 [{symbol}] Bắt đầu phân tích...")

            # Step 1: Crawl
            print(f"  📡 [{symbol}] Crawl dữ liệu...")
            rows = fetch_yfinance(symbol, FETCH_DAYS)
            if not rows:
                logger.warning(f"[{symbol}] Không có dữ liệu")
                return None
            save_prices(rows)
            print(f"  💾 [{symbol}] Đã lưu {len(rows)} bản ghi")

            # Step 2: Load from DB
            prices = load_prices(symbol)
            if len(prices) < 100:
                logger.warning(f"[{symbol}] Chỉ có {len(prices)} phiên")
                return None

            df = pd.DataFrame(prices)

            # Step 3: Technical Analysis (Strategy Pattern)
            print(f"  ⚙️ [{symbol}] Tính toán 40+ chỉ báo kỹ thuật...")
            prediction = self.tech_strategy.analyze(symbol, df)
            if prediction is None:
                return None

            last_close = float(df["close"].iloc[-1])
            last_date = str(df["date"].iloc[-1])
            trend = prediction.get("trend", {})
            conf = prediction.get("confidence", {})
            short_conf = conf.get("short_term", 0)
            st = trend.get('ngan_han_1_5_ngay', 'N/A')
            conf_label = f"(tự tin {short_conf:.0f}%)" if short_conf >= 80 else "(không đủ tự tin)"
            print(f"  📈 [{symbol}] Xu hướng: Ngắn={st} {conf_label} | "
                  f"Trung={trend.get('trung_han_5_20_ngay', 'N/A')} | "
                  f"Dài={trend.get('dai_han_20_50_ngay', 'N/A')}")
            print(f"  💰 [{symbol}] Giá đóng cửa: {last_close:,.0f}₫")

            # Step 4: Backtest (Strategy Pattern)
            print(f"  🔬 [{symbol}] Chạy backtest 20 phiên...")
            backtest = self.backtest_strategy.analyze(symbol, df)
            if backtest and backtest.get("total_tests", 0) > 0:
                skip = backtest.get("skip", 0)
                total = backtest["total"]
                corr = backtest["correct"]
                acc = backtest["accuracy"]
                print(f"  ✅ [{symbol}] Dự đoán: {corr}/{total} đúng ({acc:.0f}%) | "
                      f"Bỏ qua: {skip} phiên (thiếu tự tin)")

            # Step 5: Save prediction history
            self._save_prediction(symbol, prediction, last_close)

            # Build result
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

            # Notify observers
            await self.pipeline.notify_analysis(symbol, prediction)
            await self.pipeline.notify_backtest(symbol, backtest)

            return result

        except Exception as e:
            logger.error(f"[{symbol}] Lỗi: {e}", exc_info=True)
            return None

    def _save_prediction(self, symbol: str, prediction: dict, close_price: float):
        conn = self.db.get_connection()
        trend = prediction.get("trend", {})
        signals = prediction.get("signals", {})

        score = 0
        st = trend.get("ngan_han_1_5_ngay", "")
        if st == "MUA":
            score = 1.0
        elif st == "TĂNG_NHẸ":
            score = 0.5
        elif st == "GIẢM_NHẸ":
            score = -0.5
        elif st == "BÁN":
            score = -1.0

        conn.execute(
            """INSERT INTO prediction_history
               (symbol, run_date, close_price, short_term, medium_term, long_term, signal_score)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (symbol, datetime.now().isoformat(), close_price,
             st,
             trend.get("trung_han_5_20_ngay", ""),
             trend.get("dai_han_20_50_ngay", ""),
             score)
        )
        conn.commit()


async def main():
    symbols = ["ACB", "VCB", "FPT", "HPG", "MWG"]

    facade = AnalysisFacade(
        symbols=symbols,
        observers=["console", "telegram", "file"],
    )

    results = await facade.run()

    if results:
        print(f"\n{'='*60}")
        print(f"  ✅ PHÂN TÍCH HOÀN TẤT — {len(results)}/{len(symbols)} mã thành công")
        print(f"{'='*60}")
        print(f"\n📁 Xem báo cáo chi tiết:")
        print(f"   • Markdown: reports/report_*.md")
        print(f"   • HTML:     reports/report_*.html")
        print(f"   • JSON:     reports/data_*.json")
        print(f"\n📋 File test: test_report.md (luôn được cập nhật)")
    else:
        print("\n❌ Không có mã nào được phân tích thành công!")

    # Summary table
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
