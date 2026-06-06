"""
Script phân tích toàn diện:
1. Crawl dữ liệu mới nhất
2. Tính toán 40+ chỉ báo kỹ thuật
3. Đưa ra dự đoán xu hướng
4. Backtest: so sánh dự đoán vs kết quả thực tế
5. Gửi kết quả qua Telegram
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from config import DEFAULT_SYMBOLS
from crawler import fetch_yfinance, load_prices, save_prices
from indicators import compute_indicators
from predictor import analyze_trends
from telegram_bot import format_prediction_message, send_telegram

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


def compute_and_predict(symbol: str, df: pd.DataFrame) -> Optional[dict]:
    """Tính chỉ báo và dự đoán từ DataFrame."""
    if len(df) < 100:
        logger.warning(f"[{symbol}] Không đủ dữ liệu: {len(df)} phiên")
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


def test_predictions(symbol: str, df: pd.DataFrame, n_tests: int = 5) -> List[dict]:
    """Backtest: dùng dữ liệu đến ngày N, dự đoán ngày N+1, so sánh với thực tế."""
    results = []
    if len(df) < n_tests + 100:
        return results

    for i in range(n_tests, 0, -1):
        cut_idx = len(df) - i
        if cut_idx < 100:
            continue

        df_train = df.iloc[:cut_idx].copy()
        actual_row = df.iloc[cut_idx] if cut_idx < len(df) else None

        if actual_row is None:
            continue

        pred = compute_and_predict(f"{symbol}_test_{i}", df_train)
        if pred is None:
            continue

        actual_close = float(actual_row["close"])
        actual_open = float(actual_row["open"])
        actual_high = float(actual_row["high"])
        actual_low = float(actual_row["low"])
        pred_trend = pred.get("trend", {}).get("ngan_han_1_5_ngay", "KHÔNG_RÕ")
        pred_direction = _trend_to_direction(pred_trend)
        actual_direction = "TĂNG" if actual_close > actual_open else "GIẢM"
        actual_change_pct = ((actual_close - actual_open) / actual_open) * 100
        correct = (pred_direction == actual_direction) or \
                  (pred_direction == "TĂNG" and actual_close > df_train["close"].iloc[-1]) or \
                  (pred_direction == "GIẢM" and actual_close < df_train["close"].iloc[-1])

        if pred_direction == actual_direction:
            correct = True
        elif pred_direction == "TĂNG" and actual_close > float(df_train["close"].iloc[-1]):
            correct = True
        elif pred_direction == "GIẢM" and actual_close < float(df_train["close"].iloc[-1]):
            correct = True
        else:
            correct = False

        results.append({
            "date": actual_row["date"],
            "predicted": pred_trend,
            "prev_close": float(df_train["close"].iloc[-1]),
            "actual_open": actual_open,
            "actual_close": actual_close,
            "actual_high": actual_high,
            "actual_low": actual_low,
            "change_pct": round(actual_change_pct, 2),
            "direction": actual_direction,
            "correct": correct,
            "pred": pred,
        })
    return results


def _trend_to_direction(trend: str) -> str:
    if trend in ("MUA", "TĂNG_NHẸ"):
        return "TĂNG"
    elif trend in ("BÁN", "GIẢM_NHẸ"):
        return "GIẢM"
    return "ĐI_NGANG"


def format_test_message(symbol: str, test_results: List[dict]) -> str:
    if not test_results:
        return ""
    correct = sum(1 for r in test_results if r["correct"])
    total = len(test_results)
    acc = correct / total * 100 if total > 0 else 0
    trend_emoji = "🟢" if acc >= 60 else "🟡" if acc >= 40 else "🔴"

    lines = [f"📊 **Backtest {symbol} — {total} phiên gần nhất**",
             f"{trend_emoji} Độ chính xác: {correct}/{total} ({acc:.0f}%)", ""]

    for r in test_results[-10:]:
        corr_icon = "✅" if r["correct"] else "❌"
        actual_pct = r["change_pct"]
        pct_sign = "+" if actual_pct > 0 else ""
        lines.append(
            f"{corr_icon} {r['date']}: Dự đoán {r['predicted']:15s} "
            f"| Thực tế {r['direction']} ({pct_sign}{actual_pct:.1f}%) "
            f"| {r['prev_close']:.0f}→{r['actual_close']:.0f}"
        )

    lines.append("")
    lines.append(f"━━━━━━━━━━━━━━━━━━━")
    return "\n".join(lines)


async def analyze_symbol(symbol: str, days: int = 365) -> Optional[Dict]:
    """Phân tích 1 mã hoàn chỉnh."""
    try:
        logger.info(f"[{symbol}] Đang crawl dữ liệu...")
        rows = fetch_yfinance(symbol, days)
        if not rows:
            logger.warning(f"[{symbol}] Không có dữ liệu")
            return None
        save_prices(rows)
        prices = load_prices(symbol)
        if len(prices) < 100:
            logger.warning(f"[{symbol}] Chỉ có {len(prices)} phiên")
            return None

        df = pd.DataFrame(prices)
        result = compute_and_predict(symbol, df)
        if result is None:
            return None

        # Backtest
        test_results = test_predictions(symbol, df, n_tests=5)

        return {
            "symbol": symbol,
            "last_close": float(df["close"].iloc[-1]),
            "last_date": str(df["date"].iloc[-1]),
            "prediction": result,
            "backtest": test_results,
            "data_points": len(df),
        }
    except Exception as e:
        logger.error(f"[{symbol}] Lỗi: {e}", exc_info=True)
        return None


async def main():
    symbols = ["ACB", "VCB", "FPT", "HPG", "MWG"]
    all_results = []

    for symbol in symbols:
        result = await analyze_symbol(symbol)
        if result:
            all_results.append(result)

    # Gửi kết quả qua Telegram / console
    for r in all_results:
        symbol = r["symbol"]
        pred = r["prediction"]

        # Message dự đoán
        msg_pred = format_prediction_message(symbol, pred)
        await send_telegram(msg_pred)
        print(f"\n{'='*60}")
        print(msg_pred)

        # Message backtest
        if r["backtest"]:
            msg_test = format_test_message(symbol, r["backtest"])
            await send_telegram(msg_test)
            print(f"\n{msg_test}")

        # Tổng kết tỉ lệ đúng
        if r["backtest"]:
            correct = sum(1 for t in r["backtest"] if t["correct"])
            total = len(r["backtest"])
            logger.info(f"[{symbol}] Backtest: {correct}/{total} đúng ({correct/total*100:.0f}%)")

    # Tổng kết toàn bộ
    await send_telegram(
        f"📈 **Tổng kết phân tích {datetime.now().strftime('%d/%m/%Y')}**\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"Đã phân tích {len(all_results)} mã VN30\n"
        f"Dùng 40+ chỉ báo kỹ thuật\n"
        f"• Xu hướng (SMA, EMA, WMA, VWAP, Ichimoku, Supertrend, SAR, Aroon, Vortex)\n"
        f"• Động lượng (RSI, MACD, Stochastic, StochRSI, Williams, CCI, CMO, ROC)\n"
        f"• Biến động (ATR, Bollinger, Keltner, Choppiness, HistVol, Ulcer)\n"
        f"• Khối lượng (OBV, MFI, ADL, CMF, PVT, Volume Osc, EFI)\n"
        f"• Phân kỳ (RSI Div, MACD Div, Volume Div)\n"
        f"• Price Action, Fibonacci, Donchian, Pivot Points"
    )

    print(f"\n{'='*60}")
    print(f"Hoàn tất! Đã phân tích {len(all_results)}/{len(symbols)} mã thành công.")

    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("\n[!] Telegram chưa được cấu hình. Đặt biến môi trường:")
        print("    export TELEGRAM_TOKEN='your_bot_token'")
        print("    export TELEGRAM_CHAT_ID='your_chat_id'")
    return all_results


if __name__ == "__main__":
    from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
    asyncio.run(main())
