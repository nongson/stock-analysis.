"""Tests for indicators package."""

import numpy as np
import pandas as pd
from indicators import compute_indicators
from indicators._helpers import sma, ema


def make_df(rows=200):
    np.random.seed(42)
    close = np.cumsum(np.random.randn(rows)) + 100
    high = close + np.abs(np.random.randn(rows)) * 0.5
    low = close - np.abs(np.random.randn(rows)) * 0.5
    volume = np.random.randint(100000, 1000000, rows)
    dates = pd.date_range("2024-01-01", periods=rows, freq="D")
    return pd.DataFrame({
        "date": dates,
        "open": close * (1 + np.random.randn(rows) * 0.01),
        "high": high,
        "low": low,
        "close": close,
        "volume": volume,
    })


def test_sma():
    values = np.array([1, 2, 3, 4, 5], dtype=float)
    result = sma(values, 3)
    assert np.isnan(result[0])
    assert np.isnan(result[1])
    assert result[2] == 2.0
    assert result[3] == 3.0
    assert result[4] == 4.0


def test_ema():
    values = np.array([1, 2, 3, 4, 5], dtype=float)
    result = ema(values, 3)
    assert not np.isnan(result[0])
    assert result[0] == 1.0


def test_compute_indicators_returns_dict():
    df = make_df(200)
    result = compute_indicators(df)
    assert isinstance(result, dict)
    assert len(result) > 0


def test_compute_indicators_has_key_indicators():
    df = make_df(200)
    result = compute_indicators(df)
    expected_keys = [
        "sma_20", "ema_20", "rsi_14", "macd", "adx",
        "bb_%b", "obv", "mfi_14", "cmf_20", "supertrend_direction",
        "ichimoku_tenkan", "atr_14", "donchian_upper",
    ]
    for key in expected_keys:
        assert key in result, f"Missing key: {key}"
        assert len(result[key]) == 200, f"{key} length mismatch"


def test_compute_indicators_no_nan_at_end():
    df = make_df(200)
    result = compute_indicators(df)
    for key, arr in result.items():
        if len(arr) > 0 and not np.isnan(arr[-1]):
            return
    assert False, "All indicators have NaN at last position"
