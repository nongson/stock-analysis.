import numpy as np
from ._helpers import ema


def compute_volume(close, high, low, volume):
    result = {}

    result["obv"] = _obv(close, volume)
    result["mfi_14"] = _mfi(high, low, close, volume, 14)
    result["adl"] = _adl(high, low, close, volume)
    result["cmf_20"] = _cmf(high, low, close, volume, 20)
    result["pvt"] = _pvt(close, volume)
    result["volume_osc"] = _volume_oscillator(volume, 5, 20)
    result["efi_13"] = _efi(close, volume, 13)

    return result


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
    fast_ema = ema(volume, fast)
    slow_ema = ema(volume, slow)
    result = np.full_like(volume, np.nan)
    mask = slow_ema != 0
    result[mask] = ((fast_ema[mask] - slow_ema[mask]) / slow_ema[mask]) * 100
    return result


def _efi(close, volume, period=13):
    result = np.full_like(volume, np.nan)
    result[1:] = (np.diff(close) / close[:-1]) * volume[1:]
    return result
