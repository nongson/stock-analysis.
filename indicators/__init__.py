"""Technical Indicators Package.

Modules:
    _helpers: Core helper functions (SMA, EMA, WMA, SMMA)
    trend: Trend-following indicators (MA, Ichimoku, Supertrend, ADX, etc.)
    momentum: Momentum/oscillator indicators (RSI, MACD, Stochastic, etc.)
    volatility: Volatility indicators (ATR, Bollinger, Keltner, etc.)
    volume: Volume-based indicators (OBV, MFI, CMF, etc.)
"""

import numpy as np
import pandas as pd
from typing import Dict

from . import trend as _trend
from . import momentum as _momentum
from . import volatility as _volatility
from . import volume as _volume


def compute_indicators(df: pd.DataFrame) -> Dict[str, np.ndarray]:
    close = df["close"].values.astype(float)
    high = df["high"].values.astype(float)
    low = df["low"].values.astype(float)
    volume = df["volume"].values.astype(float)

    result = {}
    result.update(_trend.compute_trend(close, high, low, volume))
    result.update(_momentum.compute_momentum(close, high, low))
    result.update(_volatility.compute_volatility(close, high, low))
    result.update(_volume.compute_volume(close, high, low, volume))

    return result
