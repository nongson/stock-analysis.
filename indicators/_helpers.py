import numpy as np


def sma(values, period):
    result = np.full_like(values, np.nan)
    for i in range(period - 1, len(values)):
        window = values[i - period + 1 : i + 1]
        if np.all(np.isnan(window)):
            continue
        result[i] = np.nanmean(window)
    return result


def ema(values, period):
    result = np.full_like(values, np.nan)
    k = 2.0 / (period + 1)
    result[0] = values[0]
    for i in range(1, len(values)):
        result[i] = values[i] * k + result[i - 1] * (1 - k)
    return result


def wma(values, period):
    weights = np.arange(1, period + 1)
    w_sum = weights.sum()
    result = np.full_like(values, np.nan)
    for i in range(period - 1, len(values)):
        result[i] = np.dot(values[i - period + 1 : i + 1], weights) / w_sum
    return result


def smma(values, period):
    result = np.full_like(values, np.nan)
    result[period - 1] = np.mean(values[:period])
    for i in range(period, len(values)):
        result[i] = (result[i - 1] * (period - 1) + values[i]) / period
    return result


def true_range(high, low, close):
    tr = np.full_like(high, np.nan)
    tr[0] = high[0] - low[0]
    for i in range(1, len(high)):
        tr[i] = max(high[i] - low[i],
                    abs(high[i] - close[i - 1]),
                    abs(low[i] - close[i - 1]))
    return tr
