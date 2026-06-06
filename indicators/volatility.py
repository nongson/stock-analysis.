import numpy as np
from ._helpers import sma, ema, true_range


def compute_volatility(close, high, low):
    result = {}

    for period in [7, 14]:
        result[f"atr_{period}"] = _atr(high, low, close, period)

    bb_mid, bb_upper, bb_lower = _bollinger(close, 20, 2)
    result["bb_mid"] = bb_mid
    result["bb_upper"] = bb_upper
    result["bb_lower"] = bb_lower
    result["bb_%b"] = _bb_pct(close, bb_upper, bb_lower)
    result["bb_width"] = _bb_width(bb_upper, bb_lower, bb_mid)

    kc_mid, kc_upper, kc_lower = _keltner(high, low, close, 20, 2)
    result["kc_mid"] = kc_mid
    result["kc_upper"] = kc_upper
    result["kc_lower"] = kc_lower

    result["hist_vol_21"] = _hist_vol(close, 21)

    result["ulcer_index_14"] = _ulcer_index(close, 14)

    result["chop_14"] = _choppiness(high, low, close, 14)

    pp, r1, r2, r3, s1, s2, s3 = _pivot_full(high, low, close)
    result["pivot"] = pp
    result["pivot_r1"] = r1
    result["pivot_r2"] = r2
    result["pivot_r3"] = r3
    result["pivot_s1"] = s1
    result["pivot_s2"] = s2
    result["pivot_s3"] = s3

    fib_high, fib_low = _recent_swing(high, low, 20)
    if not np.isnan(fib_high) and not np.isnan(fib_low):
        diff = fib_high - fib_low
        n = len(close)
        result["fib_0"] = np.full(n, fib_low)
        result["fib_236"] = np.full(n, fib_low + 0.236 * diff)
        result["fib_382"] = np.full(n, fib_low + 0.382 * diff)
        result["fib_50"] = np.full(n, fib_low + 0.5 * diff)
        result["fib_618"] = np.full(n, fib_low + 0.618 * diff)
        result["fib_786"] = np.full(n, fib_low + 0.786 * diff)
        result["fib_100"] = np.full(n, fib_high)
        result["fib_1618"] = np.full(n, fib_high + 0.618 * diff)
        result["fib_2618"] = np.full(n, fib_high + 1.618 * diff)

    dc_upper, dc_mid, dc_lower = _donchian(high, low, 20)
    result["donchian_upper"] = dc_upper
    result["donchian_mid"] = dc_mid
    result["donchian_lower"] = dc_lower

    return result


def _atr(high, low, close, period=14):
    tr = true_range(high, low, close)
    return sma(tr, period) if period <= len(tr) else np.full_like(high, np.nan)


def _bollinger(values, period=20, num_std=2):
    mid = sma(values, period)
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
    mid = ema(close, period)
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
    tr = true_range(high, low, close)
    result = np.full_like(high, np.nan)
    for i in range(period, len(high)):
        atr_sum = np.nansum(tr[i - period + 1 : i + 1])
        hh = np.max(high[i - period + 1 : i + 1])
        ll = np.min(low[i - period + 1 : i + 1])
        if hh - ll != 0:
            result[i] = 100.0 * np.log10(atr_sum / (hh - ll)) / np.log10(period)
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
