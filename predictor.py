"""Prediction engine — Voting System với ngưỡng ≥70% đồng thuận.

Cách hoạt động:
1. Mỗi indicator vote: MUA (+1), BÁN (-1), hoặc KHÔNG_RÕ (0)
2. Tính weighted vote: ∑(vote × weight) / ∑(weight của vote không trung tính)
3. Nếu weighted vote >= +0.70 → MUA (tự tin = vote%)
4. Nếu weighted vote <= -0.70 → BÁN (tự tin = vote%)
5. Còn lại → KHÔNG_RÕ (không đủ đồng thuận)
"""

import numpy as np
from typing import Dict, Any, Optional, List


_WEIGHTS: Dict[str, float] = {
    "supertrend": 1.5,
    "adx": 1.4,
    "ichimoku": 1.3,
    "trend_ma": 1.2,
    "price_action": 1.2,
    "parabolic_sar": 1.1,
    "macd": 1.0,
    "aroon": 1.0,
    "vortex": 0.9,
    "cmf": 0.9,
    "rsi": 0.7,
    "mfi": 0.8,
    "stoch_rsi": 0.6,
    "williams_r": 0.6,
    "cci": 0.5,
    "bollinger": 0.5,
    "donchian": 0.5,
}


def _vote_value(scores: List[float], weights: List[float]) -> float:
    """Tính weighted vote: 1 = MUA, -1 = BÁN, 0 = trung tính."""
    if not scores or not weights:
        return 0.0
    arr = np.array(scores)
    w = np.array(weights)
    return float(np.average(arr, weights=w))


def _vote(name: str, vote: float, votes: list, vweights: list):
    """vote = +1 (MUA), -1 (BÁN), 0 (trung tính)."""
    votes.append(vote)
    vweights.append(_WEIGHTS.get(name, 0.5))


def _final(scores: List[float], weights: List[float]) -> Dict[str, Any]:
    """
    Voting system: đếm % weighted votes đồng thuận với hướng chính.
    - Mỗi indicator vote: >0 = MUA, <0 = BÁN, =0 = trung tính
    - Confidence = % weighted votes cùng hướng (bỏ qua trung tính)
    - Chỉ emit MUA/BÁN khi confidence >= 70%
    """
    if not scores:
        return {"signal": "KHÔNG_RÕ", "score": 0.0, "confidence": 0.0, "votes": 0}

    w_vote = _vote_value(scores, weights)
    buy_w = sum(w for s, w in zip(scores, weights) if s > 0)
    sell_w = sum(w for s, w in zip(scores, weights) if s < 0)
    total_active = buy_w + sell_w

    if total_active == 0:
        return {"signal": "KHÔNG_RÕ", "score": 0.0, "confidence": 0.0, "votes": len(scores)}

    if w_vote > 0:
        confidence = buy_w / total_active * 100
    else:
        confidence = sell_w / total_active * 100

    if confidence >= 70:
        signal = "MUA" if w_vote > 0 else "BÁN"
    else:
        signal = "KHÔNG_RÕ"

    return {
        "signal": signal,
        "score": round(w_vote, 2),
        "confidence": round(confidence, 1),
        "votes": len(scores),
    }


def _choppiness_filter(indicators: Dict) -> bool:
    """Bỏ qua nếu Choppiness Index > 40 (thị trường đi ngang, khó dự đoán)."""
    chop = indicators.get("chop_14")
    if chop is not None and len(chop) > 0 and not np.isnan(chop[-1]):
        if float(chop[-1]) > 40:
            return False
    return True


def analyze_trends(indicators: Dict[str, np.ndarray]) -> Dict[str, Any]:
    last_idx = -1

    def latest(arr, default=None):
        if arr is None or len(arr) == 0:
            return default
        val = arr[last_idx]
        return round(float(val), 2) if not np.isnan(val) else default

    def prev(arr, offset=1, default=None):
        if arr is None or len(arr) <= offset:
            return default
        val = arr[-1 - offset]
        return round(float(val), 2) if not np.isnan(val) else default

    close_val = latest(indicators.get("close"))
    close_arr = indicators.get("close")
    if close_val is None:
        return _empty_result()

    short_v: List[float] = []
    short_w: List[float] = []
    med_v: List[float] = []
    med_w: List[float] = []
    long_v: List[float] = []
    long_w: List[float] = []

    # ============== TREND-FOLLOWING ==============

    # 1. Supertrend (w=1.5)
    st_dir = latest(indicators.get("supertrend_direction"))
    if st_dir is not None:
        v = 1.0 if st_dir == -1 else -1.0
        _vote("supertrend", v, short_v, short_w)
        _vote("supertrend", v, med_v, med_w)

    # 2. ADX + DI (w=1.4)
    adx_val = latest(indicators.get("adx"))
    pdi = latest(indicators.get("+di"))
    mdi = latest(indicators.get("-di"))
    if adx_val is not None and pdi is not None and mdi is not None and adx_val >= 20:
        if pdi > mdi:
            v = 1.0 if adx_val >= 25 else 0.5
        else:
            v = -1.0 if adx_val >= 25 else -0.5
        _vote("adx", v, short_v, short_w)
        _vote("adx", v, med_v, med_w)
        _vote("adx", v, long_v, long_w)

    # 3. Ichimoku (w=1.3)
    tenkan = latest(indicators.get("ichimoku_tenkan"))
    kijun = latest(indicators.get("ichimoku_kijun"))
    span_a = latest(indicators.get("ichimoku_span_a"))
    span_b = latest(indicators.get("ichimoku_span_b"))
    if tenkan is not None and kijun is not None:
        v = 0.0
        if tenkan > kijun:
            v += 0.3
        else:
            v -= 0.3
        if span_a is not None and span_b is not None:
            if span_a > span_b:
                v += 0.2
            else:
                v -= 0.2
            if close_val is not None:
                cloud_top = max(span_a, span_b)
                cloud_bot = min(span_a, span_b)
                if close_val > cloud_top:
                    v += 0.5
                elif close_val < cloud_bot:
                    v -= 0.5
        v = max(-1.0, min(1.0, v))
        _vote("ichimoku", v, short_v, short_w)
        _vote("ichimoku", v, med_v, med_w)
        _vote("ichimoku", v, long_v, long_w)

    # 4. Parabolic SAR (w=1.1)
    psar_val = latest(indicators.get("psar"))
    if psar_val is not None and close_val is not None:
        v = 0.8 if close_val > psar_val else -0.8
        _vote("parabolic_sar", v, med_v, med_w)
        _vote("parabolic_sar", v, long_v, long_w)

    # 5. MA Trend (w=1.2)
    ma_buy, ma_sell = 0, 0
    for p in [20, 50, 100, 200]:
        for ma in [f"sma_{p}", f"ema_{p}"]:
            m = latest(indicators.get(ma))
            if m is not None:
                if close_val > m:
                    ma_buy += 1
                else:
                    ma_sell += 1
    total_ma = ma_buy + ma_sell
    if total_ma > 0:
        v = (ma_buy - ma_sell) / total_ma
        _vote("trend_ma", v, med_v, med_w)
        _vote("trend_ma", v, long_v, long_w)

    # 6. Aroon (w=1.0)
    ar_up = latest(indicators.get("aroon_up"))
    ar_down = latest(indicators.get("aroon_down"))
    if ar_up is not None and ar_down is not None:
        if ar_up > 70 and ar_down < 30:
            v = 0.8
        elif ar_down > 70 and ar_up < 30:
            v = -0.8
        elif ar_up > ar_down:
            v = 0.3
        elif ar_down > ar_up:
            v = -0.3
        else:
            v = 0.0
        _vote("aroon", v, med_v, med_w)
        _vote("aroon", v, long_v, long_w)

    # 7. Vortex (w=0.9)
    vp = latest(indicators.get("vortex_pos"))
    vn = latest(indicators.get("vortex_neg"))
    if vp is not None and vn is not None:
        if vp > 1.0 and vp > vn:
            v = 0.6
        elif vn > 1.0 and vn > vp:
            v = -0.6
        elif vp > vn:
            v = 0.3
        elif vn > vp:
            v = -0.3
        else:
            v = 0.0
        _vote("vortex", v, med_v, med_w)

    # ============== MOMENTUM / OSCILLATORS ==============

    # 8. MACD (w=1.0)
    macd_latest = latest(indicators.get("macd"))
    signal_latest = latest(indicators.get("macd_signal"))
    hist_latest = latest(indicators.get("macd_histogram"))
    hist_prev = prev(indicators.get("macd_histogram"), 1)
    if macd_latest is not None and signal_latest is not None:
        v = 0.0
        if macd_latest > signal_latest:
            v += 0.5
        else:
            v -= 0.5
        if hist_latest is not None and hist_prev is not None:
            if hist_latest > hist_prev:
                v += 0.3
            elif hist_latest < hist_prev:
                v -= 0.3
        v = max(-1.0, min(1.0, v))
        _vote("macd", v, short_v, short_w)
        _vote("macd", v, med_v, med_w)

    # 9. RSI(14) (w=0.7)
    rsi_arr = indicators.get("rsi_14")
    rsi_val = latest(rsi_arr)
    if rsi_val is not None:
        if rsi_val > 70:
            v = -0.6
        elif rsi_val < 30:
            v = 0.6
        elif rsi_val > 60:
            v = -0.3
        elif rsi_val < 40:
            v = 0.3
        else:
            v = 0.0
        _vote("rsi", v, short_v, short_w)

    # 10. RSI Divergence
    rsi_div = _detect_divergence(close_arr, rsi_arr, 14)
    rsi_div_str = "KHÔNG"
    if rsi_div == "bullish":
        rsi_div_str = "PHÂN_KỲ_TĂNG"
    elif rsi_div == "bearish":
        rsi_div_str = "PHÂN_KỲ_GIẢM"

    # 11. MACD Divergence
    macd_arr = indicators.get("macd")
    macd_div = _detect_divergence(close_arr, macd_arr, 14)
    macd_div_str = "KHÔNG"
    if macd_div == "bullish":
        macd_div_str = "PHÂN_KỲ_TĂNG"
    elif macd_div == "bearish":
        macd_div_str = "PHÂN_KỲ_GIẢM"

    # 12. StochRSI (w=0.6)
    stoch_rsi_val = latest(indicators.get("stoch_rsi"))
    if stoch_rsi_val is not None:
        if stoch_rsi_val > 80:
            v = -0.5
        elif stoch_rsi_val < 20:
            v = 0.5
        elif stoch_rsi_val > 60:
            v = -0.3
        elif stoch_rsi_val < 40:
            v = 0.3
        else:
            v = 0.0
        _vote("stoch_rsi", v, short_v, short_w)

    # 13. Williams %R (w=0.6)
    wr_val = latest(indicators.get("williams_%r"))
    if wr_val is not None:
        if wr_val <= -80:
            v = 0.6
        elif wr_val >= -20:
            v = -0.6
        elif wr_val <= -50:
            v = 0.3
        else:
            v = -0.3
        _vote("williams_r", v, short_v, short_w)

    # 14. CCI (w=0.5)
    cci_val = latest(indicators.get("cci_20"))
    if cci_val is not None:
        if cci_val > 100:
            v = -0.6
        elif cci_val < -100:
            v = 0.6
        elif cci_val > 50:
            v = -0.3
        elif cci_val < -50:
            v = 0.3
        else:
            v = 0.0
        _vote("cci", v, short_v, short_w)

    # 15. MFI (w=0.8)
    mfi_val = latest(indicators.get("mfi_14"))
    if mfi_val is not None:
        if mfi_val > 80:
            v = -0.5
        elif mfi_val < 20:
            v = 0.5
        elif mfi_val > 50:
            v = 0.3
        else:
            v = -0.3
        _vote("mfi", v, short_v, short_w)

    # 16. Bollinger %b (w=0.5)
    bb_pct_val = latest(indicators.get("bb_%b"))
    if bb_pct_val is not None:
        if bb_pct_val > 1.0:
            v = -0.3
        elif bb_pct_val < 0.0:
            v = 0.3
        else:
            v = 0.0
        _vote("bollinger", v, short_v, short_w)

    # ============== VOLUME ==============

    # 17. CMF (w=0.9)
    cmf_val = latest(indicators.get("cmf_20"))
    if cmf_val is not None:
        if cmf_val > 0.05:
            v = 0.5
        elif cmf_val < -0.05:
            v = -0.5
        else:
            v = 0.0
        _vote("cmf", v, med_v, med_w)

    # 18. Volume Divergence
    obv_arr = indicators.get("obv")
    vol_div = _detect_divergence(close_arr, obv_arr, 14)
    if vol_div == "bullish":
        vol_div_str = "DÒNG_TIỀN_VÀO"
    elif vol_div == "bearish":
        vol_div_str = "DÒNG_TIỀN_RA"
    else:
        vol_div_str = "KHÔNG_RÕ"

    # 19. Donchian (w=0.5)
    dc_up = latest(indicators.get("donchian_upper"))
    dc_lo = latest(indicators.get("donchian_lower"))
    if close_val is not None and dc_up is not None and dc_lo is not None:
        if close_val >= dc_up:
            v = 0.6
        elif close_val <= dc_lo:
            v = -0.6
        else:
            v = 0.0
        _vote("donchian", v, short_v, short_w)

    # 20. Price Action (w=1.2)
    pa_signal = _price_action_pattern(close_arr, indicators.get("high"), indicators.get("low"))
    pa_short = pa_signal.get("short_term", "TRUNG_TÍNH")
    if pa_short == "TĂNG":
        v = 0.8
    elif pa_short == "GIẢM":
        v = -0.8
    elif pa_short == "TĂNG_NHẸ":
        v = 0.3
    elif pa_short == "GIẢM_NHẸ":
        v = -0.3
    else:
        v = 0.0
    _vote("price_action", v, short_v, short_w)

    # ============== FINAL SIGNALS ==============

    short_result = _final(short_v, short_w)
    med_result = _final(med_v, med_w)
    long_result = _final(long_v, long_w)

    short_term = short_result["signal"]
    medium_term = med_result["signal"]
    long_term = long_result["signal"]

    entry_advice = _entry_advice(short_result, med_result, long_result, rsi_val, vol_div_str)

    meta = {
        "close": close_val,
        "rsi_14": rsi_val,
        "macd": macd_latest,
        "macd_signal": signal_latest,
        "macd_histogram": hist_latest,
        "adx": adx_val,
        "+di": pdi,
        "-di": mdi,
        "atr_14": latest(indicators.get("atr_14")),
        "bb_%b": bb_pct_val,
        "stoch_rsi": stoch_rsi_val,
        "mfi_14": mfi_val,
        "cmf_20": cmf_val,
        "supertrend_dir": st_dir,
        "short_score": short_result["score"],
        "short_confidence": short_result["confidence"],
        "med_score": med_result["score"],
        "med_confidence": med_result["confidence"],
        "long_score": long_result["score"],
        "long_confidence": long_result["confidence"],
    }

    return {
        "metadata": meta,
        "signals": {
            "rsi": "TĂNG" if rsi_val and rsi_val > 50 else "GIẢM" if rsi_val else "KHÔNG_RÕ",
            "rsi_divergence": rsi_div_str,
            "macd": "TĂNG" if macd_latest and signal_latest and macd_latest > signal_latest else "GIẢM",
            "macd_divergence": macd_div_str,
            "adx_strength": "MẠNH" if adx_val and adx_val >= 25 else "YẾU",
            "adx_direction": "TĂNG" if pdi and mdi and pdi > mdi else "GIẢM",
            "supertrend": "TĂNG" if st_dir == -1 else "GIẢM",
            "mfi": "TĂNG" if mfi_val and mfi_val > 50 else "GIẢM",
            "cmf": "TĂNG" if cmf_val and cmf_val > 0.05 else "GIẢM",
            "volume_divergence": vol_div_str,
            "donchian": "BREAKOUT_TRÊN" if dc_up and close_val and close_val >= dc_up else "BREAKOUT_DƯỚI",
            "price_action": pa_signal.get("pattern", "KHÔNG_RÕ"),
        },
        "trend": {
            "ngan_han_1_5_ngay": short_term,
            "trung_han_5_20_ngay": medium_term,
            "dai_han_20_50_ngay": long_term,
        },
        "confidence": {
            "short_term": short_result["confidence"],
            "medium_term": med_result["confidence"],
            "long_term": long_result["confidence"],
            "short_score": short_result["score"],
            "med_score": med_result["score"],
            "long_score": long_result["score"],
        },
        "entry_advice": entry_advice,
        "price_action": pa_signal,
        "score_details": {
            "short_term_indicators": short_result["votes"],
            "medium_term_indicators": med_result["votes"],
            "long_term_indicators": long_result["votes"],
        },
    }


def _detect_divergence(price: np.ndarray, indicator: np.ndarray, window: int = 14) -> Optional[str]:
    if price is None or indicator is None or len(price) < window * 2:
        return None
    end = len(price) - 1
    start = max(0, end - window * 2)
    p_slice = price[start:end + 1]
    i_slice = indicator[start:end + 1]
    if np.any(np.isnan(p_slice)) or np.any(np.isnan(i_slice)):
        return None
    half = len(p_slice) // 2
    if half < 3:
        return None
    p_first = p_slice[:half]
    p_second = p_slice[half:]
    i_first = i_slice[:half]
    i_second = i_slice[half:]
    p1_min, p1_max = np.min(p_first), np.max(p_first)
    p2_min, p2_max = np.min(p_second), np.max(p_second)
    i1_min, i1_max = np.min(i_first), np.max(i_first)
    i2_min, i2_max = np.min(i_second), np.max(i_second)
    if p2_min < p1_min and i2_min > i1_min:
        return "bullish"
    if p2_max > p1_max and i2_max < i1_max:
        return "bearish"
    return None


def _price_action_pattern(close: np.ndarray, high: np.ndarray = None, low: np.ndarray = None) -> Dict[str, str]:
    result = {"pattern": "KHÔNG_RÕ", "short_term": "TRUNG_TÍNH"}
    if close is None or len(close) < 10:
        return result
    c5 = close[-5:]
    hh = all(c5[i] <= c5[i + 1] if not (np.isnan(c5[i]) or np.isnan(c5[i + 1])) else True for i in range(len(c5) - 1))
    ll = all(c5[i] >= c5[i + 1] if not (np.isnan(c5[i]) or np.isnan(c5[i + 1])) else True for i in range(len(c5) - 1))
    c3 = close[-3:]
    up3 = all(c3[i] < c3[i + 1] for i in range(2) if not (np.isnan(c3[i]) or np.isnan(c3[i + 1])))
    down3 = all(c3[i] > c3[i + 1] for i in range(2) if not (np.isnan(c3[i]) or np.isnan(c3[i + 1])))
    if up3:
        result["pattern"] = "3_NẾN_TĂNG"
        result["short_term"] = "TĂNG"
    elif down3:
        result["pattern"] = "3_NẾN_GIẢM"
        result["short_term"] = "GIẢM"
    elif hh:
        result["pattern"] = "HH_HL"
        result["short_term"] = "TĂNG_NHẸ"
    elif ll:
        result["pattern"] = "LH_LL"
        result["short_term"] = "GIẢM_NHẸ"
    if high is not None and low is not None:
        h5 = high[-5:]
        l5 = low[-5:]
        avg_range = np.mean(h5 - l5) if np.all(np.isfinite(h5 - l5)) else 0
        if avg_range > 0:
            last_range = (high[-1] - low[-1]) if not (np.isnan(high[-1]) or np.isnan(low[-1])) else 0
            if 0 < last_range < avg_range * 0.5:
                result["pattern"] += " | NÉN"
                result["short_term"] = "CHỜ"
    return result


def _entry_advice(short: Dict, med: Dict, long: Dict,
                  rsi: Optional[float], vol_div: str) -> str:
    short_sig = short.get("signal", "KHÔNG_RÕ")
    short_conf = short.get("confidence", 0)
    med_sig = med.get("signal", "KHÔNG_RÕ")
    if short_conf < 70:
        return "CHỜ (thiếu đồng thuận)"
    if short_sig == "MUA":
        if rsi is not None and rsi < 35:
            return "MUA_TÍCH_CỰC (oversold + đồng thuận)"
        if med_sig == "MUA":
            return "MUA (đồng thuận ngắn+trung)"
        return "CÓ_THỂ_MUA"
    elif short_sig == "BÁN":
        if rsi is not None and rsi > 65:
            return "BÁN_TÍCH_CỰC (overbought + đồng thuận)"
        if med_sig == "BÁN":
            return "BÁN (đồng thuận ngắn+trung)"
        return "CÓ_THỂ_BÁN"
    return "CHỜ (chưa rõ xu hướng)"


def _empty_result() -> Dict[str, Any]:
    return {
        "metadata": {},
        "signals": {},
        "trend": {
            "ngan_han_1_5_ngay": "KHÔNG_RÕ",
            "trung_han_5_20_ngay": "KHÔNG_RÕ",
            "dai_han_20_50_ngay": "KHÔNG_RÕ",
        },
        "confidence": {},
        "entry_advice": "CHỜ (thiếu dữ liệu)",
        "price_action": {},
        "score_details": {},
    }
