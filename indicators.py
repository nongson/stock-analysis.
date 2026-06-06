import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple


def compute_indicators(df: pd.DataFrame) -> Dict[str, np.ndarray]:
    close = df["close"].values.astype(float)
    high = df["high"].values.astype(float)
    low = df["low"].values.astype(float)
    volume = df["volume"].values.astype(float)
    n = len(close)

    result = {}

    def safe_last(arr):
        return arr if arr is None or len(arr) == 0 else arr

    # --- SMA ---
    for period in [5, 10, 20, 50, 100, 200]:
        result[f"sma_{period}"] = _sma(close, period)

    # --- EMA ---
    for period in [5, 10, 20, 50, 100, 200]:
        result[f"ema_{period}"] = _ema(close, period)

    # --- WMA ---
    for period in [5, 10, 20]:
        result[f"wma_{period}"] = _wma(close, period)

    # --- SMMA ---
    for period in [5, 10, 20]:
        result[f"smma_{period}"] = _smma(close, period)

    # --- VWAP ---
    result["vwap"] = _vwap(high, low, close, volume)

    # --- VWMA ---
    for period in [5, 10, 20]:
        result[f"vwma_{period}"] = _vwma(close, volume, period)

    # --- Median Price, Typical Price, Weighted Close ---
    result["median_price"] = (high + low) / 2.0
    result["typical_price"] = (high + low + close) / 3.0
    result["weighted_close"] = (high + low + 2 * close) / 4.0

    # --- RSI ---
    for p in [7, 14, 21]:
        result[f"rsi_{p}"] = _rsi(close, p)

    # --- Stochastic %K / %D ---
    stoch_k, stoch_d = _stochastic(high, low, close, 14, 3)
    result["stoch_%k"] = stoch_k
    result["stoch_%d"] = stoch_d

    # --- Stochastic RSI ---
    stoch_rsi_val = _stoch_rsi(close, 14, 14)
    result["stoch_rsi"] = stoch_rsi_val

    # --- MACD ---
    macd_line, signal, hist = _macd(close)
    result["macd"] = macd_line
    result["macd_signal"] = signal
    result["macd_histogram"] = hist

    # --- Momentum ---
    for period in [5, 10]:
        result[f"momentum_{period}"] = _momentum(close, period)

    # --- ROC ---
    for period in [5, 10, 21]:
        result[f"roc_{period}"] = _roc(close, period)

    # --- Williams %R ---
    result["williams_%r"] = _williams_r(high, low, close, 14)

    # --- CCI ---
    result["cci_20"] = _cci(high, low, close, 20)

    # --- CMO ---
    result["cmo_14"] = _cmo(close, 14)

    # --- ATR ---
    for period in [7, 14]:
        result[f"atr_{period}"] = _atr(high, low, close, period)

    # --- Bollinger Bands ---
    bb_mid, bb_upper, bb_lower = _bollinger(close, 20, 2)
    result["bb_mid"] = bb_mid
    result["bb_upper"] = bb_upper
    result["bb_lower"] = bb_lower
    result["bb_%b"] = _bb_pct(close, bb_upper, bb_lower)
    result["bb_width"] = _bb_width(bb_upper, bb_lower, bb_mid)

    # --- Keltner Channel ---
    kc_mid, kc_upper, kc_lower = _keltner(high, low, close, 20, 2)
    result["kc_mid"] = kc_mid
    result["kc_upper"] = kc_upper
    result["kc_lower"] = kc_lower

    # --- Historical Volatility ---
    result["hist_vol_21"] = _hist_vol(close, 21)

    # --- Ulcer Index ---
    result["ulcer_index_14"] = _ulcer_index(close, 14)

    # --- Choppiness Index ---
    result["chop_14"] = _choppiness(high, low, close, 14)

    # --- ADX ---
    adx_val, plus_di, minus_di = _adx(high, low, close, 14)
    result["adx"] = adx_val
    result["+di"] = plus_di
    result["-di"] = minus_di

    # --- Parabolic SAR ---
    result["psar"] = _psar(high, low)

    # --- Ichimoku (full) ---
    ten, kij, span_a, span_b, chikou = _ichimoku_full(high, low, close)
    result["ichimoku_tenkan"] = ten
    result["ichimoku_kijun"] = kij
    result["ichimoku_span_a"] = span_a
    result["ichimoku_span_b"] = span_b
    result["ichimoku_chikou"] = chikou

    # --- Supertrend ---
    st_dir, st_upper, st_lower = _supertrend(high, low, close, 10, 3)
    result["supertrend_direction"] = st_dir
    result["supertrend_upper"] = st_upper
    result["supertrend_lower"] = st_lower

    # --- Aroon ---
    aroon_up, aroon_down = _aroon(high, low, 25)
    result["aroon_up"] = aroon_up
    result["aroon_down"] = aroon_down

    # --- Vortex ---
    vortex_pos, vortex_neg = _vortex(high, low, close, 14)
    result["vortex_pos"] = vortex_pos
    result["vortex_neg"] = vortex_neg

    # --- OBV ---
    result["obv"] = _obv(close, volume)

    # --- MFI ---
    result["mfi_14"] = _mfi(high, low, close, volume, 14)

    # --- ADL ---
    result["adl"] = _adl(high, low, close, volume)

    # --- CMF ---
    result["cmf_20"] = _cmf(high, low, close, volume, 20)

    # --- PVT ---
    result["pvt"] = _pvt(close, volume)

    # --- Volume Oscillator ---
    result["volume_osc"] = _volume_oscillator(volume, 5, 20)

    # --- EFI ---
    result["efi_13"] = _efi(close, volume, 13)

    # --- Pivot Points ---
    pp, r1, r2, r3, s1, s2, s3 = _pivot_full(high, low, close)
    result["pivot"] = pp
    result["pivot_r1"] = r1
    result["pivot_r2"] = r2
    result["pivot_r3"] = r3
    result["pivot_s1"] = s1
    result["pivot_s2"] = s2
    result["pivot_s3"] = s3

    # --- Fibonacci levels (from recent swing) ---
    fib_high, fib_low = _recent_swing(high, low, 20)
    if not np.isnan(fib_high) and not np.isnan(fib_low):
        diff = fib_high - fib_low
        result["fib_0"] = np.full(n, fib_low)
        result["fib_236"] = np.full(n, fib_low + 0.236 * diff)
        result["fib_382"] = np.full(n, fib_low + 0.382 * diff)
        result["fib_50"] = np.full(n, fib_low + 0.5 * diff)
        result["fib_618"] = np.full(n, fib_low + 0.618 * diff)
        result["fib_786"] = np.full(n, fib_low + 0.786 * diff)
        result["fib_100"] = np.full(n, fib_high)
        result["fib_1618"] = np.full(n, fib_high + 0.618 * diff)
        result["fib_2618"] = np.full(n, fib_high + 1.618 * diff)

    # --- Donchian Channel ---
    dc_upper, dc_mid, dc_lower = _donchian(high, low, 20)
    result["donchian_upper"] = dc_upper
    result["donchian_mid"] = dc_mid
    result["donchian_lower"] = dc_lower

    # --- Linear Regression ---
    slope, intercept, r_sq = _linreg(close, 14)
    result["linreg_slope_14"] = slope
    result["linreg_intercept_14"] = intercept
    result["linreg_r2_14"] = r_sq

    return result


def _sma(values, period):
    result = np.full_like(values, np.nan)
    for i in range(period - 1, len(values)):
        window = values[i - period + 1 : i + 1]
        if np.all(np.isnan(window)):
            continue
        result[i] = np.nanmean(window)
    return result


def _ema(values, period):
    result = np.full_like(values, np.nan)
    k = 2.0 / (period + 1)
    result[0] = values[0]
    for i in range(1, len(values)):
        result[i] = values[i] * k + result[i - 1] * (1 - k)
    return result


def _wma(values, period):
    weights = np.arange(1, period + 1)
    w_sum = weights.sum()
    result = np.full_like(values, np.nan)
    for i in range(period - 1, len(values)):
        result[i] = np.dot(values[i - period + 1 : i + 1], weights) / w_sum
    return result


def _smma(values, period):
    result = np.full_like(values, np.nan)
    result[period - 1] = np.mean(values[:period])
    for i in range(period, len(values)):
        result[i] = (result[i - 1] * (period - 1) + values[i]) / period
    return result


def _vwap(high, low, close, volume):
    tp = (high + low + close) / 3.0
    cum_pv = np.cumsum(tp * volume)
    cum_v = np.cumsum(volume)
    result = np.full_like(close, np.nan)
    mask = cum_v > 0
    result[mask] = cum_pv[mask] / cum_v[mask]
    return result


def _vwma(values, volume, period):
    result = np.full_like(values, np.nan)
    for i in range(period - 1, len(values)):
        pv_sum = np.sum(values[i - period + 1 : i + 1] * volume[i - period + 1 : i + 1])
        v_sum = np.sum(volume[i - period + 1 : i + 1])
        result[i] = pv_sum / v_sum if v_sum != 0 else np.nan
    return result


def _rsi(values, period=14):
    deltas = np.diff(values)
    gains = np.where(deltas > 0, deltas, 0.0)
    losses = np.where(deltas < 0, -deltas, 0.0)
    result = np.full_like(values, np.nan)
    avg_gain = np.mean(gains[:period]) if period <= len(gains) else 0
    avg_loss = np.mean(losses[:period]) if period <= len(losses) else 0
    for i in range(period, len(values)):
        avg_gain = (avg_gain * (period - 1) + gains[i - 1]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i - 1]) / period
        if avg_loss == 0:
            result[i] = 100.0
        else:
            rs = avg_gain / avg_loss
            result[i] = 100.0 - 100.0 / (1.0 + rs)
    return result


def _stoch_rsi(values, rsi_period=14, stoch_period=14):
    rsi = _rsi(values, rsi_period)
    result = np.full_like(rsi, np.nan)
    for i in range(rsi_period + stoch_period - 1, len(rsi)):
        window = rsi[i - stoch_period + 1 : i + 1]
        mn, mx = np.nanmin(window), np.nanmax(window)
        if mx != mn:
            result[i] = (rsi[i] - mn) / (mx - mn) * 100
        else:
            result[i] = 50.0
    return result


def _macd(values):
    ema12 = _ema(values, 12)
    ema26 = _ema(values, 26)
    macd_line = ema12 - ema26
    signal = _ema(macd_line, 9)
    hist = macd_line - signal
    return macd_line, signal, hist


def _momentum(values, period=10):
    result = np.full_like(values, np.nan)
    for i in range(period, len(values)):
        result[i] = values[i] - values[i - period]
    return result


def _roc(values, period=10):
    result = np.full_like(values, np.nan)
    for i in range(period, len(values)):
        result[i] = ((values[i] - values[i - period]) / values[i - period]) * 100.0
    return result


def _williams_r(high, low, close, period=14):
    result = np.full_like(close, np.nan)
    for i in range(period - 1, len(close)):
        hh = np.max(high[i - period + 1 : i + 1])
        ll = np.min(low[i - period + 1 : i + 1])
        if hh - ll != 0:
            result[i] = ((hh - close[i]) / (hh - ll)) * -100.0
    return result


def _cci(high, low, close, period=20):
    tp = (high + low + close) / 3.0
    sma_tp = _sma(tp, period)
    result = np.full_like(tp, np.nan)
    for i in range(period - 1, len(tp)):
        mad = np.mean(np.abs(tp[i - period + 1 : i + 1] - sma_tp[i]))
        result[i] = (tp[i] - sma_tp[i]) / (0.015 * mad) if mad != 0 else np.nan
    return result


def _cmo(values, period=14):
    deltas = np.diff(values)
    result = np.full_like(values, np.nan)
    for i in range(period, len(values)):
        window = deltas[i - period : i]
        gains = np.sum(window[window > 0])
        losses = np.sum(-window[window < 0])
        total = gains + losses
        if total != 0:
            result[i] = ((gains - losses) / total) * 100.0
    return result


def _atr(high, low, close, period=14):
    tr = np.full_like(high, np.nan)
    tr[0] = high[0] - low[0]
    for i in range(1, len(high)):
        tr[i] = max(high[i] - low[i],
                    abs(high[i] - close[i - 1]),
                    abs(low[i] - close[i - 1]))
    return _sma(tr, period) if period <= len(tr) else np.full_like(high, np.nan)


def _bollinger(values, period=20, num_std=2):
    mid = _sma(values, period)
    rolling_std = np.full_like(values, np.nan)
    for i in range(period - 1, len(values)):
        rolling_std[i] = np.std(values[i - period + 1 : i + 1], ddof=1)
    upper = mid + num_std * rolling_std
    lower = mid - num_std * rolling_std
    return mid, upper, lower


def _bb_pct(close, upper, lower):
    denom = upper - lower
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(denom != 0, (close - lower) / denom, np.nan)


def _bb_width(upper, lower, mid):
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(mid != 0, (upper - lower) / mid * 100, np.nan)


def _keltner(high, low, close, period=20, multiplier=2):
    mid = _ema(close, period)
    atr_val = _atr(high, low, close, period)
    upper = mid + multiplier * atr_val
    lower = mid - multiplier * atr_val
    return mid, upper, lower


def _hist_vol(values, period=21):
    log_ret = np.full_like(values, np.nan)
    log_ret[1:] = np.log(values[1:] / values[:-1])
    result = np.full_like(values, np.nan)
    for i in range(period, len(values)):
        result[i] = np.nanstd(log_ret[i - period + 1 : i + 1]) * np.sqrt(252) * 100
    return result


def _ulcer_index(values, period=14):
    result = np.full_like(values, np.nan)
    for i in range(period - 1, len(values)):
        window = values[i - period + 1 : i + 1]
        peak = np.maximum.accumulate(window)
        dd = ((window - peak) / peak * 100) ** 2
        result[i] = np.sqrt(np.mean(dd))
    return result


def _choppiness(high, low, close, period=14):
    tr = np.full_like(high, np.nan)
    tr[0] = high[0] - low[0]
    for i in range(1, len(high)):
        tr[i] = max(high[i] - low[i],
                    abs(high[i] - close[i - 1]),
                    abs(low[i] - close[i - 1]))
    result = np.full_like(high, np.nan)
    for i in range(period, len(high)):
        atr_sum = np.nansum(tr[i - period + 1 : i + 1])
        hh = np.max(high[i - period + 1 : i + 1])
        ll = np.min(low[i - period + 1 : i + 1])
        if hh - ll != 0:
            result[i] = 100.0 * np.log10(atr_sum / (hh - ll)) / np.log10(period)
    return result


def _adx(high, low, close, period=14):
    up_move = np.zeros_like(high)
    down_move = np.zeros_like(high)
    up_move[1:] = np.diff(high)
    down_move[1:] = -np.diff(low)
    down_move[down_move < 0] = 0
    up_move[up_move < 0] = 0
    pos_dm = np.where(up_move > down_move, up_move, 0.0)
    neg_dm = np.where(down_move > up_move, down_move, 0.0)
    tr = np.full_like(close, np.nan)
    tr[0] = high[0] - low[0]
    for i in range(1, len(close)):
        tr[i] = max(high[i] - low[i], abs(high[i] - close[i-1]), abs(low[i] - close[i-1]))
    atr_series = _sma(tr, period)
    pos_di_ema = _ema(pos_dm, period)
    neg_di_ema = _ema(neg_dm, period)
    plus_di = np.full_like(close, np.nan)
    minus_di = np.full_like(close, np.nan)
    dx = np.full_like(close, np.nan)
    for i in range(period, len(close)):
        if atr_series[i] != 0:
            plus_di[i] = 100 * pos_di_ema[i] / atr_series[i]
            minus_di[i] = 100 * neg_di_ema[i] / atr_series[i]
        if not (np.isnan(plus_di[i]) or np.isnan(minus_di[i]) or (plus_di[i] + minus_di[i]) == 0):
            dx[i] = abs(plus_di[i] - minus_di[i]) / (plus_di[i] + minus_di[i]) * 100
    adx_vals = _sma(dx, period)
    return adx_vals, plus_di, minus_di


def _psar(high, low, af_start=0.02, af_step=0.02, af_max=0.2):
    n = len(high)
    sar = np.full(n, np.nan)
    ep = np.full(n, np.nan)
    af = np.full(n, af_start)
    trend = np.full(n, 1)
    if n < 2:
        return sar
    sar[0] = low[0]
    ep[0] = high[0]
    trend[0] = 1
    for i in range(1, n):
        if trend[i - 1] == 1:
            sar[i] = sar[i - 1] + af[i - 1] * (ep[i - 1] - sar[i - 1])
            if sar[i] > low[i]:
                sar[i] = ep[i - 1]
                trend[i] = -1
                af[i] = af_start
                ep[i] = low[i]
            else:
                trend[i] = 1
                if low[i] < sar[i]:
                    sar[i] = low[i]
                if high[i] > ep[i - 1]:
                    ep[i] = high[i]
                    af[i] = min(af[i - 1] + af_step, af_max)
                else:
                    ep[i] = ep[i - 1]
                    af[i] = af[i - 1]
        else:
            sar[i] = sar[i - 1] - af[i - 1] * (sar[i - 1] - ep[i - 1])
            if sar[i] < high[i]:
                sar[i] = ep[i - 1]
                trend[i] = 1
                af[i] = af_start
                ep[i] = high[i]
            else:
                trend[i] = -1
                if high[i] > sar[i]:
                    sar[i] = high[i]
                if low[i] < ep[i - 1]:
                    ep[i] = low[i]
                    af[i] = min(af[i - 1] + af_step, af_max)
                else:
                    ep[i] = ep[i - 1]
                    af[i] = af[i - 1]
        if trend[i] == -1:
            sar[i] = min(sar[i], low[i - 1] if i > 0 else sar[i])
        else:
            sar[i] = max(sar[i], high[i - 1] if i > 0 else sar[i])
    return sar


def _ichimoku_full(high, low, close):
    n = len(high)
    ten = np.full(n, np.nan)
    kij = np.full(n, np.nan)
    span_a = np.full(n, np.nan)
    span_b = np.full(n, np.nan)
    chikou = np.full(n, np.nan)
    for i in range(8, n):
        ten[i] = (np.max(high[i - 8:i + 1]) + np.min(low[i - 8:i + 1])) / 2
    for i in range(25, n):
        kij[i] = (np.max(high[i - 25:i + 1]) + np.min(low[i - 25:i + 1])) / 2
    for i in range(25, n):
        if not (np.isnan(ten[i]) or np.isnan(kij[i])):
            span_a[i] = (ten[i] + kij[i]) / 2
    for i in range(51, n):
        span_b[i] = (np.max(high[i - 51:i + 1]) + np.min(low[i - 51:i + 1])) / 2
    for i in range(26, n):
        chikou[i - 26] = close[i]
    return ten, kij, span_a, span_b, chikou


def _stochastic(high, low, close, k_period=14, d_period=3):
    k = np.full_like(close, np.nan)
    for i in range(k_period - 1, len(close)):
        hh = np.max(high[i - k_period + 1 : i + 1])
        ll = np.min(low[i - k_period + 1 : i + 1])
        if hh - ll != 0:
            k[i] = (close[i] - ll) / (hh - ll) * 100
    d = _sma(k, d_period)
    return k, d


def _supertrend(high, low, close, period=10, multiplier=3):
    atr = _atr(high, low, close, period)
    hl_avg = (high + low) / 2.0
    upper = hl_avg + multiplier * atr
    lower = hl_avg - multiplier * atr
    direction = np.full_like(close, np.nan)
    direction[0] = 1 if close[0] > lower[0] else -1
    for i in range(1, len(close)):
        if direction[i - 1] == 1:
            upper[i] = min(upper[i], upper[i-1])
        else:
            lower[i] = max(lower[i], lower[i-1])
        if close[i] > upper[i]:
            direction[i] = -1
        elif close[i] < lower[i]:
            direction[i] = 1
        else:
            direction[i] = direction[i - 1]
    return direction, upper, lower


def _aroon(high, low, period=25):
    up = np.full_like(high, np.nan)
    down = np.full_like(high, np.nan)
    for i in range(period - 1, len(high)):
        window_h = high[i - period + 1 : i + 1]
        window_l = low[i - period + 1 : i + 1]
        hh_idx = np.argmax(window_h)
        ll_idx = np.argmin(window_l)
        up[i] = ((period - 1 - hh_idx) / period) * 100
        down[i] = ((period - 1 - ll_idx) / period) * 100
    return up, down


def _vortex(high, low, close, period=14):
    tr = np.full_like(high, np.nan)
    tr[0] = high[0] - low[0]
    vm_pos = np.full_like(high, np.nan)
    vm_neg = np.full_like(high, np.nan)
    for i in range(1, len(high)):
        tr[i] = max(high[i] - low[i], abs(high[i] - close[i - 1]), abs(low[i] - close[i - 1]))
        vm_pos[i] = abs(high[i] - low[i - 1])
        vm_neg[i] = abs(low[i] - high[i - 1])
    vmp = _sma(vm_pos, period)
    vmn = _sma(vm_neg, period)
    tr_sum = _sma(tr, period)
    pos = np.full_like(high, np.nan)
    neg = np.full_like(high, np.nan)
    for i in range(period, len(high)):
        if tr_sum[i] != 0:
            pos[i] = vmp[i] / tr_sum[i]
            neg[i] = vmn[i] / tr_sum[i]
    return pos, neg


def _obv(close, volume):
    obv = np.full_like(volume, np.nan)
    obv[0] = volume[0]
    for i in range(1, len(close)):
        if close[i] > close[i - 1]:
            obv[i] = obv[i - 1] + volume[i]
        elif close[i] < close[i - 1]:
            obv[i] = obv[i - 1] - volume[i]
        else:
            obv[i] = obv[i - 1]
    return obv


def _mfi(high, low, close, volume, period=14):
    tp = (high + low + close) / 3.0
    mfi_vals = np.full_like(close, np.nan)
    for i in range(period, len(close)):
        pos_flow = 0
        neg_flow = 0
        for j in range(i - period, i):
            if tp[j + 1] > tp[j]:
                pos_flow += tp[j + 1] * volume[j + 1]
            else:
                neg_flow += tp[j + 1] * volume[j + 1]
        if neg_flow != 0:
            mfr = pos_flow / neg_flow
            mfi_vals[i] = 100.0 - 100.0 / (1.0 + mfr)
    return mfi_vals


def _adl(high, low, close, volume):
    hl_range = high - low
    mf_mult = np.divide(((close - low) - (high - close)), hl_range, out=np.zeros_like(hl_range), where=hl_range != 0)
    mf_vol = mf_mult * volume
    result = np.full_like(volume, np.nan)
    result[0] = mf_vol[0]
    for i in range(1, len(close)):
        result[i] = result[i - 1] + mf_vol[i]
    return result


def _cmf(high, low, close, volume, period=20):
    hl_range = high - low
    mf_mult = np.divide(((close - low) - (high - close)), hl_range, out=np.zeros_like(hl_range), where=hl_range != 0)
    mf_vol = mf_mult * volume
    result = np.full_like(close, np.nan)
    for i in range(period - 1, len(close)):
        sum_mf = np.nansum(mf_vol[i - period + 1 : i + 1])
        sum_v = np.nansum(volume[i - period + 1 : i + 1])
        result[i] = sum_mf / sum_v if sum_v != 0 else np.nan
    return result


def _pvt(close, volume):
    result = np.full_like(volume, np.nan)
    result[0] = 0
    for i in range(1, len(close)):
        pct_change = (close[i] - close[i - 1]) / close[i - 1]
        result[i] = result[i - 1] + pct_change * volume[i]
    return result


def _volume_oscillator(volume, fast=5, slow=20):
    fast_ema = _ema(volume, fast)
    slow_ema = _ema(volume, slow)
    result = np.full_like(volume, np.nan)
    mask = slow_ema != 0
    result[mask] = ((fast_ema[mask] - slow_ema[mask]) / slow_ema[mask]) * 100
    return result


def _efi(close, volume, period=13):
    result = np.full_like(volume, np.nan)
    result[1:] = (np.diff(close) / close[:-1]) * volume[1:]
    return result


def _pivot_full(high, low, close):
    pp = (high + low + close) / 3.0
    r1 = 2 * pp - low
    r2 = pp + (high - low)
    r3 = high + 2 * (pp - low)
    s1 = 2 * pp - high
    s2 = pp - (high - low)
    s3 = low - 2 * (high - pp)
    return pp, r1, r2, r3, s1, s2, s3


def _recent_swing(high, low, lookback=20):
    end = len(high) - 1
    start = max(0, end - lookback)
    if end < lookback:
        return np.nan, np.nan
    return np.max(high[start:end + 1]), np.min(low[start:end + 1])


def _donchian(high, low, period=20):
    upper = np.full_like(high, np.nan)
    lower = np.full_like(high, np.nan)
    for i in range(period - 1, len(high)):
        upper[i] = np.max(high[i - period + 1 : i + 1])
        lower[i] = np.min(low[i - period + 1 : i + 1])
    mid = (upper + lower) / 2.0
    return upper, mid, lower


def _linreg(values, period=14):
    n = len(values)
    slope = np.full(n, np.nan)
    intercept = np.full(n, np.nan)
    r_sq = np.full(n, np.nan)
    x = np.arange(period)
    for i in range(period - 1, n):
        y = values[i - period + 1 : i + 1]
        A = np.vstack([x, np.ones(period)]).T
        try:
            m, b = np.linalg.lstsq(A, y, rcond=None)[0]
            slope[i] = m
            intercept[i] = b
            y_pred = m * x + b
            ss_res = np.sum((y - y_pred) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            r_sq[i] = 1 - (ss_res / ss_tot) if ss_tot != 0 else np.nan
        except np.linalg.LinAlgError:
            pass
    return slope, intercept, r_sq
