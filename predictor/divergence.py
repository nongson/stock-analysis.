"""Divergence detection between price and indicators."""

import numpy as np
from typing import Optional


def detect_divergence(price: np.ndarray, indicator: np.ndarray, window: int = 14) -> Optional[str]:
    """Detect bullish/bearish divergence between price and indicator.

    Returns:
        "bullish" — price makes lower low, indicator makes higher low
        "bearish" — price makes higher high, indicator makes lower high
        None — no divergence detected
    """
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
