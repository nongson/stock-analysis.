"""Gửi kết quả dự đoán qua Telegram bot."""

import asyncio
from typing import Dict, Any

from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID


def _arrow(val: str) -> str:
    mapping = {
        "MUA": "🟢 MUA", "BÁN": "🔴 BÁN",
        "TĂNG_MẠNH": "🟢📈 Tăng mạnh", "TĂNG_NHẸ": "🟗📈 Tăng nhẹ",
        "GIẢM_MẠNH": "🔻📉 Giảm mạnh", "GIẢM_NHẸ": "🔶📉 Giảm nhẹ",
        "ĐI_NGANG": "⚪ Đi ngang", "TĂNG": "🟢📈 Tăng", "GIẢM": "🔴📉 Giảm",
        "TRUNG_TÍNH": "⚪ Trung tính",
        "QUÁ_MUA": "🔴 Quá mua", "QUÁ_BÁN": "🟢 Quá bán",
        "MẠNH": "💪 Mạnh", "YẾU": "💤 Yếu", "TRUNG_BÌNH": "📊 Trung bình",
        "TRÊN_DẢI_TRÊN (quá mua)": "🔴 Trên dải trên",
        "DƯỚI_DẢI_DƯỚI (quá bán)": "🟢 Dưới dải dưới",
        "GIỮA_DẢI": "⚪ Giữa dải", "TRÊN_GIỮA": "🟗 Trên giữa", "DƯỚI_GIỮA": "🔶 Dưới giữa",
        "GẦN_DẢI_TRÊN": "🟡 Gần dải trên", "GẦN_DẢI_DƯỚI": "🔵 Gần dải dưới",
        "TĂNG (uptrend)": "🟢 Uptrend", "GIẢM (downtrend)": "🔴 Downtrend",
        "TĂNG (above SAR)": "🟢 Trên SAR", "GIẢM (below SAR)": "🔴 Dưới SAR",
        "KHÔNG_RÕ": "❓ Không rõ",
        "PHÂN_KỲ_TĂNG": "🟢⚠️ PHÂN KỲ TĂNG",
        "PHÂN_KỲ_GIẢM": "🔴⚠️ PHÂN KỲ GIẢM",
        "TĂNG_MẠNH (mây xanh)": "🟢☁️ Mây xanh", "GIẢM_MẠNH (mây đỏ)": "🔴☁️ Mây đỏ",
        "TĂNG (price above cloud)": "🟢 Trên mây", "GIẢM (price below cloud)": "🔴 Dưới mây",
        "TRONG_MÂY": "⚪ Trong mây",
        "KHỐI_LƯỢNG_TĂNG": "⬆️📊 KL tăng", "KHỐI_LƯỢNG_GIẢM": "⬇️📊 KL giảm",
        "DÒNG_TIỀN_VÀO (Bullish)": "🟢💰 Dòng tiền vào",
        "DÒNG_TIỀN_RA (Bearish)": "🔴💰 Dòng tiền ra",
        "BREAKOUT_TRÊN": "🟢🚀 Breakout trên",
        "BREAKOUT_DƯỚI": "🔴💥 Breakout dưới", "TRONG_KÊNH": "⚪ Trong kênh",
        "TĂNG (dòng tiền vào)": "🟢 Dòng tiền vào",
        "GIẢM (dòng tiền ra)": "🔴 Dòng tiền ra",
        "TĂNG (áp lực mua)": "🟢 Áp lực mua",
        "GIẢM (áp lực bán)": "🔴 Áp lực bán",
        "3_NẾN_TĂNG_LIÊN_TIẾP": "🟢📗 3 nến tăng",
        "3_NẾN_GIẢM_LIÊN_TIẾP": "🔴📕 3 nến giảm",
        "CAO_HƠN_CAO_HƠN": "🟗 HH pattern",
        "THẤP_HƠN_THẤP_HƠN": "🔶 LL pattern",
        "CHỜ_BREAKOUT": "⏳ Chờ breakout",
        "CAO": "🔴 Cao", "THẤP": "🟢 Thấp",
        "NẮM_GIỮ / MUA_THÊM_NẾU_CÓ_XÁC_NHẬN": "🟗 Nắm giữ/có thể mua thêm",
        "CẮT_LỖ / CHỜ_MUA_LẠI": "🔶 Cắt lỗ/chờ mua lại",
        "CHỜ (chưa rõ xu hướng)": "⏳ Chờ",
        "CÓ_THỂ_MUA": "🟢 Có thể mua",
        "CÓ_THỂ_BÁN": "🔴 Có thể bán",
        "MUA_TÍCH_CỰC (RSI quá bán + xu hướng tăng)": "🟢✅ MUA TÍCH CỰC",
        "BÁN_TÍCH_CỰC (RSI quá mua + xu hướng giảm)": "🔴✅ BÁN TÍCH CỰC",
        "MUA (phân kỳ tăng, kỳ vọng đảo chiều)": "🟢 MUA (phân kỳ)",
        "BÁN (phân kỳ giảm, kỳ vọng đảo chiều)": "🔴 BÁN (phân kỳ)",
        "MUA (breakout kênh Donchian)": "🟢🚀 MUA (breakout)",
        "BÁN (breakdown kênh Donchian)": "🔴💥 BÁN (breakdown)",
        "CHỜ (thị trường đi ngang, chờ breakout)": "⏳ Chờ sideways",
        "KHÔNG": "✅ Không",
        "ĐI_NGANG (sideways)": "⚪ Sideways",
        "XU_HƯỚNG (trending)": "📈 Trending",
        "TRUNG_GIAN": "⚪ Trung gian",
    }
    if val and val in mapping:
        return mapping[val]
    return val


def format_prediction_message(symbol: str, result: Dict[str, Any]) -> str:
    meta = result.get("metadata", {})
    signals = result.get("signals", {})
    trend = result.get("trend", {})
    fib = result.get("fibonacci_levels", {})
    advice = result.get("entry_advice", "")
    pa = result.get("price_action", {})
    close_price = f"{meta.get('close', 0):,.0f}".replace(",", ".") if isinstance(meta.get("close"), (int, float)) else "N/A"

    trend_map = {
        "MUA": "🟢 **MUA**", "BÁN": "🔴 **BÁN**",
        "TĂNG_NHẸ": "🟗 Tăng nhẹ", "GIẢM_NHẸ": "🔶 Giảm nhẹ",
        "ĐI_NGANG": "⚪ Đi ngang",
    }

    fib_str = ""
    if fib:
        fib_items = ", ".join(fib.values())
        fib_str = f"\n📍 **Fibonacci:** {fib_items}"

    pa_str = f"\n📐 **PA:** {_arrow(pa.get('pattern', ''))}" if pa.get("pattern") and pa["pattern"] != "KHÔNG_RÕ" else ""

    advice_str = f"\n🎯 **Gợi ý:** {_arrow(advice)}" if advice else ""

    vol_div = signals.get("volume_divergence", "")
    vol_div_str = f"\n💰 **Vol.Div:** {_arrow(vol_div)}" if vol_div and vol_div != "KHÔNG_RÕ" else ""

    rsi_div = signals.get("rsi_divergence", "")
    rsi_div_str = f"\n⚠️ **RSI.Div:** {_arrow(rsi_div)}" if rsi_div and rsi_div not in ("KHÔNG", "KHÔNG_RÕ") else ""

    macd_div = signals.get("macd_divergence", "")
    macd_div_str = f"\n⚠️ **MACD.Div:** {_arrow(macd_div)}" if macd_div and macd_div not in ("KHÔNG", "KHÔNG_RÕ") else ""

    msg = (
        f"📊 **{symbol}** — {close_price}₫\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"**📈 Xu thế:**\n"
        f"• Ngắn hạn (1-5d): {trend_map.get(trend.get('ngan_han_1_5_ngay', ''), trend.get('ngan_han_1_5_ngay', ''))}\n"
        f"• Trung hạn (5-20d): {trend_map.get(trend.get('trung_han_5_20_ngay', ''), trend.get('trung_han_5_20_ngay', ''))}\n"
        f"• Dài hạn (20-50d): {trend_map.get(trend.get('dai_han_20_50_ngay', ''), trend.get('dai_han_20_50_ngay', ''))}\n"
        f"{pa_str}{rsi_div_str}{macd_div_str}{vol_div_str}{fib_str}{advice_str}\n"
        f"\n"
        f"**📊 Chỉ báo kỹ thuật:**\n"
        f"• RSI(14): {meta.get('rsi_14', 'N/A')} → {_arrow(signals.get('rsi', ''))}\n"
        f"• StochRSI: {'%.0f' % meta.get('stoch_rsi', 0) if meta.get('stoch_rsi') else 'N/A'} → {_arrow(signals.get('stoch_rsi', ''))}\n"
        f"• MACD: {meta.get('macd', 'N/A')} → {_arrow(signals.get('macd', ''))}\n"
        f"• Williams %R: {meta.get('williams_%r', 'N/A')} → {_arrow(signals.get('williams_r', ''))}\n"
        f"• CCI(20): {meta.get('cci_20', 'N/A')} → {_arrow(signals.get('cci', ''))}\n"
        f"• CMO(14): {meta.get('cmo_14', 'N/A')} → {_arrow(signals.get('cmo', ''))}\n"
        f"• Bollinger: {_arrow(signals.get('bollinger', ''))}\n"
        f"• Stochastic: {_arrow(signals.get('stochastic', ''))}\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"**📉 Xu hướng:**\n"
        f"• ADX: {_arrow(signals.get('adx_strength', ''))} / {_arrow(signals.get('adx_direction', ''))}\n"
        f"• Ichimoku: {_arrow(signals.get('ichimoku', ''))} | {_arrow(signals.get('ichimoku_cloud', ''))}\n"
        f"• Supertrend: {_arrow(signals.get('supertrend', ''))}\n"
        f"• Parabolic SAR: {_arrow(signals.get('parabolic_sar', ''))}\n"
        f"• Aroon: {_arrow(signals.get('aroon', ''))}\n"
        f"• Vortex: {_arrow(signals.get('vortex', ''))}\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"**💰 Khối lượng:**\n"
        f"• MFI(14): {meta.get('mfi_14', 'N/A')} → {_arrow(signals.get('mfi', ''))}\n"
        f"• CMF(20): {meta.get('cmf_20', 'N/A')} → {_arrow(signals.get('cmf', ''))}\n"
        f"• Vol Osc: {meta.get('volume_osc', 'N/A')}% → {_arrow(signals.get('volume_oscillator', ''))}\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"**🌪 Biến động:**\n"
        f"• Choppiness: {meta.get('choppiness_14', 'N/A')} → {_arrow(signals.get('choppiness', ''))}\n"
        f"• Hist Vol(21): {meta.get('hist_vol_21', 'N/A')}% → {_arrow(signals.get('historical_volatility', ''))}\n"
        f"• Donchian: {_arrow(signals.get('donchian', ''))}"
    )
    return msg


async def send_telegram(message: str) -> bool:
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("[Telegram] Skipped: token hoặc chat_id chưa được cấu hình")
        return False
    try:
        from telegram import Bot
        bot = Bot(token=TELEGRAM_TOKEN)
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode="Markdown")
        print(f"[Telegram] Đã gửi tin nhắn thành công")
        return True
    except Exception as e:
        print(f"[Telegram] Lỗi gửi tin nhắn: {e}")
        return False


async def send_prediction(symbol: str, result: Dict[str, Any]) -> bool:
    msg = format_prediction_message(symbol, result)
    return await send_telegram(msg)
