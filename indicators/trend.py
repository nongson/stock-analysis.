import numpy as np
from ._helpers import sma, ema, wma, smma, true_range


def compute_trend(close, high, low, volume):
    result = {}
    n = len(close)

    for period in [5, 10, 20, 50, 100, 200]:
        result[f"sma_{period}"] = sma(close, period)
    for period in [5, 10, 20, 50, 100, 200]:
        result[f"ema_{period}"] = ema(close, period)
    for period in [5, 10, 20]:
        result[f"wma_{period}"] = wma(close, period)
    for period in [5, 10, 20]:
        result[f"smma_{period}"] = smma(close, period)

    result["vwap"] = _vwap(high, low, close, volume)
    for period in [5, 10, 20]:
        result[f"vwma_{period}"] = _vwma(close, volume, period)

    result["median_price"] = (high + low) / 2.0
    result["typical_price"] = (high + low + close) / 3.0
    result["weighted_close"] = (high + low + 2 * close) / 4.0

    st_dir, st_upper, st_lower = _supertrend(high, low, close, 10, 3)
    result["supertrend_direction"] = st_dir
    result["supertrend_upper"] = st_upper
    result["supertrend_lower"] = st_lower

    result["psar"] = _psar(high, low)

    ten, kij, span_a, span_b, chikou = _ichimoku_full(high, low, close)
    result["ichimoku_tenkan"] = ten
    result["ichimoku_kijun"] = kij
    result["ichimoku_span_a"] = span_a
    result["ichimoku_span_b"] = span_b
    result["ichimoku_chikou"] = chikou

    aroon_up, aroon_down = _aroon(high, low, 25)
    result["aroon_up"] = aroon_up
    result["aroon_down"] = aroon_down

    vortex_pos, vortex_neg = _vortex(high, low, close, 14)
    result["vortex_pos"] = vortex_pos
    result["vortex_neg"] = vortex_neg

    adx_val, plus_di, minus_di = _adx(high, low, close, 14)
    result["adx"] = adx_val
    result["+di"] = plus_di
    result["-di"] = minus_di

    slope, intercept, r_sq = _linreg(close, 14)
    result["linreg_slope_14"] = slope
    result["linreg_intercept_14"] = intercept
    result["linreg_r2_14"] = r_sq

    return result


def compute_adx(high, low, close):
    return _adx(high, low, close, 14)


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


def _atr(high, low, close, period=14):
    tr = true_range(high, low, close)
    return sma(tr, period) if period <= len(tr) else np.full_like(high, np.nan)


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
    tr = true_range(high, low, close)
    vm_pos = np.full_like(high, np.nan)
    vm_neg = np.full_like(high, np.nan)
    for i in range(1, len(high)):
        vm_pos[i] = abs(high[i] - low[i - 1])
        vm_neg[i] = abs(low[i] - high[i - 1])
    vmp = sma(vm_pos, period)
    vmn = sma(vm_neg, period)
    tr_sum = sma(tr, period)
    pos = np.full_like(high, np.nan)
    neg = np.full_like(high, np.nan)
    for i in range(period, len(high)):
        if tr_sum[i] != 0:
            pos[i] = vmp[i] / tr_sum[i]
            neg[i] = vmn[i] / tr_sum[i]
    return pos, neg


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
    atr_series = sma(tr, period)
    pos_di_ema = ema(pos_dm, period)
    neg_di_ema = ema(neg_dm, period)
    plus_di = np.full_like(close, np.nan)
    minus_di = np.full_like(close, np.nan)
    dx = np.full_like(close, np.nan)
    for i in range(period, len(close)):
        if atr_series[i] != 0:
            plus_di[i] = 100 * pos_di_ema[i] / atr_series[i]
            minus_di[i] = 100 * neg_di_ema[i] / atr_series[i]
        if not (np.isnan(plus_di[i]) or np.isnan(minus_di[i]) or (plus_di[i] + minus_di[i]) == 0):
            dx[i] = abs(plus_di[i] - minus_di[i]) / (plus_di[i] + minus_di[i]) * 100
    adx_vals = sma(dx, period)
    return adx_vals, plus_di, minus_di


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
