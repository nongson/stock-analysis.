"""Design Patterns for stock analysis engine.

- Strategy Pattern: interchangeable analysis/backtest strategies
- Observer Pattern: notify multiple channels (Telegram, file, console)
- Factory Pattern: create analysis pipelines
- Singleton Pattern: database connection
- Facade Pattern: simplified interface to complex subsystems
"""

import abc
import sqlite3
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Protocol

import pandas as pd
import numpy as np

from config import DB_PATH

logger = logging.getLogger(__name__)


# ==================== Singleton Pattern ====================

class DatabaseSingleton:
    _instance = None
    _conn = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def get_connection(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(str(DB_PATH))
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._init_tables()
        return self._conn

    def _init_tables(self):
        conn = self._conn
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
        conn.execute("""
            CREATE TABLE IF NOT EXISTS backtest_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                run_date TEXT NOT NULL,
                test_date TEXT NOT NULL,
                predicted_trend TEXT,
                actual_direction TEXT,
                prev_close REAL,
                actual_close REAL,
                change_pct REAL,
                correct INTEGER,
                accuracy REAL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS prediction_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                run_date TEXT NOT NULL,
                close_price REAL,
                short_term TEXT,
                medium_term TEXT,
                long_term TEXT,
                signal_score REAL
            )
        """)
        conn.commit()

    def close(self):
        if self._conn:
            self._conn.close()
            DatabaseSingleton._instance = None
            DatabaseSingleton._conn = None


# ==================== Strategy Pattern ====================

class AnalysisStrategy(abc.ABC):
    @abc.abstractmethod
    def analyze(self, symbol: str, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        pass


class TechnicalAnalysisStrategy(AnalysisStrategy):
    def analyze(self, symbol: str, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        from indicators import compute_indicators
        from predictor import analyze_trends

        if len(df) < 100:
            logger.warning(f"[{symbol}] Not enough data: {len(df)} days")
            return None

        df = df.dropna(subset=["open", "high", "low", "close", "volume"]).copy()
        df["close"] = df["close"].astype(float)
        df["high"] = df["high"].astype(float)
        df["low"] = df["low"].astype(float)
        df["volume"] = df["volume"].astype(float)

        indicators = compute_indicators(df)
        indicators["close"] = df["close"].values
        indicators["high"] = df["high"].values
        indicators["low"] = df["low"].values

        result = analyze_trends(indicators)
        result["_updated_at"] = datetime.now().isoformat()
        return result


class BacktestStrategy(AnalysisStrategy):
    def __init__(self, n_tests: int = 20):
        self.n_tests = n_tests

    def analyze(self, symbol: str, df: pd.DataFrame) -> Optional[Dict[str, Any]]:
        if len(df) < self.n_tests + 100:
            return {"symbol": symbol, "tests": [], "accuracy": 0.0, "total": 0,
                    "correct": 0, "skip": 0, "skip_pct": 0.0}

        strategy = TechnicalAnalysisStrategy()
        results = []
        skip_count = 0
        db = DatabaseSingleton()
        conn = db.get_connection()

        for i in range(self.n_tests, 0, -1):
            cut_idx = len(df) - i
            if cut_idx < 100:
                continue

            df_train = df.iloc[:cut_idx].copy()
            actual_row = df.iloc[cut_idx] if cut_idx < len(df) else None
            if actual_row is None:
                continue

            pred = strategy.analyze(f"{symbol}_test_{i}", df_train)
            if pred is None:
                skip_count += 1
                continue

            pred_trend = pred.get("trend", {}).get("ngan_han_1_5_ngay", "KHÔNG_RÕ")
            med_trend = pred.get("trend", {}).get("trung_han_5_20_ngay", "KHÔNG_RÕ")

            # ADX filter: skip khi thị trường đi ngang (ADX < 20)
            adx_val = pred.get("metadata", {}).get("adx")
            if adx_val is not None and adx_val < 20:
                skip_count += 1
                results.append({
                    "date": actual_row["date"],
                    "predicted": "KHÔNG_RÕ",
                    "prev_close": float(df_train["close"].iloc[-1]),
                    "actual_open": float(actual_row["open"]),
                    "actual_close": float(actual_row["close"]),
                    "actual_high": float(actual_row["high"]),
                    "actual_low": float(actual_row["low"]),
                    "change_pct": 0.0,
                    "direction": "TĂNG" if float(actual_row["close"]) > float(actual_row["open"]) else "GIẢM",
                    "correct": False,
                    "skipped": True,
                    "pred": pred,
                })
                continue

            # Volatility filter: skip khi ATR/close > 4% (quá biến động, khó dự đoán)
            atr_val = pred.get("metadata", {}).get("atr_14")
            prev_close = float(df_train["close"].iloc[-1])
            if atr_val is not None and prev_close > 0:
                atr_ratio = atr_val / prev_close * 100
                if atr_ratio > 4.0:
                    skip_count += 1
                    results.append({
                        "date": actual_row["date"],
                        "predicted": "KHÔNG_RÕ",
                        "prev_close": prev_close,
                        "actual_open": float(actual_row["open"]),
                        "actual_close": float(actual_row["close"]),
                        "actual_high": float(actual_row["high"]),
                        "actual_low": float(actual_row["low"]),
                        "change_pct": 0.0,
                        "direction": "TĂNG" if float(actual_row["close"]) > float(actual_row["open"]) else "GIẢM",
                        "correct": False,
                        "skipped": True,
                        "pred": pred,
                    })
                    continue

            # Multi-timeframe confirmation: emit khi ngắn hạn + trung hạn đồng thuận
            if pred_trend == "KHÔNG_RÕ" or med_trend == "KHÔNG_RÕ" or pred_trend != med_trend:
                skip_count += 1
                skip_reason = "KHÔNG_RÕ"
                if pred_trend != med_trend:
                    skip_reason = f"MÂU_THUẪN ({pred_trend} vs {med_trend})"
                results.append({
                    "date": actual_row["date"],
                    "predicted": skip_reason,
                    "prev_close": float(df_train["close"].iloc[-1]),
                    "actual_open": float(actual_row["open"]),
                    "actual_close": float(actual_row["close"]),
                    "actual_high": float(actual_row["high"]),
                    "actual_low": float(actual_row["low"]),
                    "change_pct": 0.0,
                    "direction": "TĂNG" if float(actual_row["close"]) > float(actual_row["open"]) else "GIẢM",
                    "correct": False,
                    "skipped": True,
                    "pred": pred,
                })
                continue

            actual_open = float(actual_row["open"])
            actual_close = float(actual_row["close"])
            actual_direction = "TĂNG" if actual_close > actual_open else "GIẢM"
            actual_change_pct = ((actual_close - actual_open) / actual_open) * 100

            correct = (pred_trend == "MUA" and actual_direction == "TĂNG") or \
                      (pred_trend == "BÁN" and actual_direction == "GIẢM")

            results.append({
                "date": actual_row["date"],
                "predicted": pred_trend,
                "prev_close": float(df_train["close"].iloc[-1]),
                "actual_open": actual_open,
                "actual_close": actual_close,
                "actual_high": float(actual_row["high"]),
                "actual_low": float(actual_row["low"]),
                "change_pct": round(actual_change_pct, 2),
                "direction": actual_direction,
                "correct": correct,
                "skipped": False,
                "pred": pred,
            })

            conn.execute(
                """INSERT INTO backtest_history
                   (symbol, run_date, test_date, predicted_trend, actual_direction,
                    prev_close, actual_close, change_pct, correct, accuracy)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (symbol, datetime.now().isoformat(), actual_row["date"],
                 pred_trend, actual_direction,
                 float(df_train["close"].iloc[-1]), actual_close,
                 round(actual_change_pct, 2), int(correct), 0.0)
            )
        conn.commit()

        predicted_results = [r for r in results if not r.get("skipped", False)]
        total_predicted = len(predicted_results)
        correct_count = sum(1 for r in predicted_results if r["correct"])
        accuracy = round((correct_count / total_predicted * 100), 1) if total_predicted > 0 else 0.0
        total_tests = len(results)
        skip_pct = round((skip_count / total_tests * 100), 1) if total_tests > 0 else 0.0

        return {
            "symbol": symbol,
            "tests": results,
            "accuracy": accuracy,
            "total": total_predicted,
            "correct": correct_count,
            "skip": skip_count,
            "skip_pct": skip_pct,
            "total_tests": total_tests,
        }


# ==================== Observer Pattern ====================

class ReportObserver(abc.ABC):
    @abc.abstractmethod
    async def on_analysis_complete(self, symbol: str, result: Dict[str, Any]) -> None:
        pass

    @abc.abstractmethod
    async def on_backtest_complete(self, symbol: str, backtest_result: Dict[str, Any]) -> None:
        pass

    @abc.abstractmethod
    async def on_pipeline_complete(self, all_results: List[Dict[str, Any]]) -> None:
        pass


class TelegramObserver(ReportObserver):
    async def on_analysis_complete(self, symbol: str, result: Dict[str, Any]) -> None:
        from telegram_bot import format_prediction_message, send_telegram
        msg = format_prediction_message(symbol, result)
        await send_telegram(msg)

    async def on_backtest_complete(self, symbol: str, backtest_result: Dict[str, Any]) -> None:
        from telegram_bot import send_telegram
        msg = self._format_backtest_msg(symbol, backtest_result)
        if msg:
            await send_telegram(msg)

    async def on_pipeline_complete(self, all_results: List[Dict[str, Any]]) -> None:
        from telegram_bot import send_telegram
        summary = self._format_summary(all_results)
        await send_telegram(summary)

    def _format_backtest_msg(self, symbol: str, bt: Dict[str, Any]) -> str:
        if not bt or bt.get("total", 0) == 0:
            return ""
        acc = bt["accuracy"]
        trend_emoji = "🟢" if acc >= 60 else "🟡" if acc >= 40 else "🔴"
        lines = [
            f"📊 **Backtest {symbol} — {bt['total']} phiên gần nhất**",
            f"{trend_emoji} Độ chính xác: {bt['correct']}/{bt['total']} ({acc:.0f}%)",
            "",
        ]
        for r in bt.get("tests", [])[-5:]:
            icon = "✅" if r["correct"] else "❌"
            pct = r["change_pct"]
            sign = "+" if pct > 0 else ""
            lines.append(
                f"{icon} {r['date']}: {r['predicted']:15s} | "
                f"Thực tế {r['direction']} ({sign}{pct:.1f}%) | "
                f"{r['prev_close']:.0f}→{r['actual_close']:.0f}"
            )
        lines.extend(["", "━━━━━━━━━━━━━━━━━━━"])
        return "\n".join(lines)

    def _format_summary(self, results: List[Dict[str, Any]]) -> str:
        if not results:
            return ""
        lines = [
            f"📈 **Tổng kết {datetime.now().strftime('%d/%m/%Y')}**",
            "━━━━━━━━━━━━━━━━━━━",
            "Chỉ emit tín hiệu khi tự tin ≥ 80%",
            "",
        ]
        for r in results:
            trend = r.get("trend", {})
            st = trend.get("ngan_han_1_5_ngay", "N/A")
            conf = r.get("prediction", {}).get("confidence", {}).get("short_term", 0)
            bt = r.get("backtest", {})
            acc_str = f" | Acc: {bt.get('accuracy', 0):.0f}%" if bt else ""
            skip_str = f" | Bỏ qua: {bt.get('skip', 0)}" if bt else ""
            lines.append(f"• **{r['symbol']}** {r.get('close_price', '')}: {st} "
                         f"(TC: {conf:.0f}%){acc_str}{skip_str}")
        lines.append("━━━━━━━━━━━━━━━━━━━")
        return "\n".join(lines)


class FileObserver(ReportObserver):
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        import os
        os.makedirs(self.output_dir, exist_ok=True)

    async def on_analysis_complete(self, symbol: str, result: Dict[str, Any]) -> None:
        pass

    async def on_backtest_complete(self, symbol: str, backtest_result: Dict[str, Any]) -> None:
        pass

    async def on_pipeline_complete(self, all_results: List[Dict[str, Any]]) -> None:
        from report_generator import ReportGenerator
        gen = ReportGenerator(self.output_dir)
        gen.generate_markdown(all_results)
        gen.generate_html(all_results)


class ConsoleObserver(ReportObserver):
    async def on_analysis_complete(self, symbol: str, result: Dict[str, Any]) -> None:
        trend = result.get("trend", {})
        conf = result.get("confidence", {})
        short_conf = conf.get("short_term", 0)
        print(f"  [{symbol}] Ngắn hạn: {trend.get('ngan_han_1_5_ngay', 'N/A')} "
              f"(tự tin: {short_conf:.0f}%) | "
              f"Trung hạn: {trend.get('trung_han_5_20_ngay', 'N/A')} | "
              f"Dài hạn: {trend.get('dai_han_20_50_ngay', 'N/A')}")

    async def on_backtest_complete(self, symbol: str, bt: Dict[str, Any]) -> None:
        if bt:
            skip = bt.get("skip", 0)
            print(f"  [{symbol}] Backtest: {bt.get('correct', 0)}/{bt.get('total', 0)} "
                  f"đúng ({bt.get('accuracy', 0):.0f}%) "
                  f"[bỏ qua {skip} phiên KHÔNG_RÕ]")

    async def on_pipeline_complete(self, all_results: List[Dict[str, Any]]) -> None:
        print(f"\n{'='*60}")
        print(f"✅ Hoàn tất! Đã phân tích {len(all_results)} mã thành công.")
        print(f"📁 Báo cáo lưu tại: reports/")


class ObservablePipeline:
    def __init__(self):
        self._observers: List[ReportObserver] = []

    def attach(self, observer: ReportObserver):
        self._observers.append(observer)

    def detach(self, observer: ReportObserver):
        self._observers.remove(observer)

    async def notify_analysis(self, symbol: str, result: Dict[str, Any]):
        for obs in self._observers:
            try:
                await obs.on_analysis_complete(symbol, result)
            except Exception as e:
                logger.error(f"Observer error (analysis): {e}")

    async def notify_backtest(self, symbol: str, bt: Dict[str, Any]):
        for obs in self._observers:
            try:
                await obs.on_backtest_complete(symbol, bt)
            except Exception as e:
                logger.error(f"Observer error (backtest): {e}")

    async def notify_pipeline(self, results: List[Dict[str, Any]]):
        for obs in self._observers:
            try:
                await obs.on_pipeline_complete(results)
            except Exception as e:
                logger.error(f"Observer error (pipeline): {e}")


# ==================== Factory Pattern ====================

class AnalysisFactory:
    @staticmethod
    def create_strategy(strategy_type: str = "technical", **kwargs) -> AnalysisStrategy:
        if strategy_type == "technical":
            return TechnicalAnalysisStrategy()
        elif strategy_type == "backtest":
            return BacktestStrategy(n_tests=kwargs.get("n_tests", 20))
        raise ValueError(f"Unknown strategy: {strategy_type}")

    @staticmethod
    def create_pipeline(observers: Optional[List[str]] = None) -> ObservablePipeline:
        pipeline = ObservablePipeline()
        if observers is None:
            observers = ["console", "telegram", "file"]

        for obs_type in observers:
            if obs_type == "console":
                pipeline.attach(ConsoleObserver())
            elif obs_type == "telegram":
                pipeline.attach(TelegramObserver())
            elif obs_type == "file":
                pipeline.attach(FileObserver())
        return pipeline
