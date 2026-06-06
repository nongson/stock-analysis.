import numpy as np
from ._helpers import sma, ema


def compute_momentum(close, high, low):
    result = {}

    for p in [7, 14, 21]:
        result[f"rsi_{p}"] = _rsi(close, p)

    stoch_k, stoch_d = _stochastic(high, low, close, 14, 3)
    result["stoch_%k"] = stoch_k
    result["stoch_%d"] = stoch_d

    result["stoch_rsi"] = _stoch_rsi(close, 14, 14)

    macd_line, signal, hist = _macd(close)
    result["macd"] = macd_line
    result["macd_signal"] = signal
    result["macd_histogram"] = hist

    for period in [5, 10]:
        result[f"momentum_{period}"] = _momentum(close, period)

    for period in [5, 10, 21]:
        result[f"roc_{period}"] = _roc(close, period)

    result["williams_%r"] = _williams_r(high, low, close, 14)

    result["cci_20"] = _cci(high, low, close, 20)

    result["cmo_14"] = _cmo(close, 14)

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
    ema12 = ema(values, 12)
    ema26 = ema(values, 26)
    macd_line = ema12 - ema26
    signal = ema(macd_line, 9)
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
    sma_tp = sma(tp, period)
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


def _stochastic(high, low, close, k_period=14, d_period=3):
    k = np.full_like(close, np.nan)
    for i in range(k_period - 1, len(close)):
        hh = np.max(high[i - k_period + 1 : i + 1])
        ll = np.min(low[i - k_period + 1 : i + 1])
        if hh - ll != 0:
            k[i] = (close[i] - ll) / (hh - ll) * 100
    d = sma(k, d_period)
    return k, d
