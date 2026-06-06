"""Pydantic models for API request/response."""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    time: str
    cached_symbols: List[str]


class SignalDetail(BaseModel):
    rsi: str = "KHÔNG_RÕ"
    rsi_divergence: str = "KHÔNG"
    macd: str = "KHÔNG_RÕ"
    macd_divergence: str = "KHÔNG"
    adx_strength: str = "YẾU"
    adx_direction: str = "KHÔNG_RÕ"
    supertrend: str = "KHÔNG_RÕ"
    mfi: str = "KHÔNG_RÕ"
    cmf: str = "KHÔNG_RÕ"
    volume_divergence: str = "KHÔNG_RÕ"
    donchian: str = "KHÔNG_RÕ"
    price_action: str = "KHÔNG_RÕ"


class Trend(BaseModel):
    ngan_han_1_5_ngay: str = "KHÔNG_RÕ"
    trung_han_5_20_ngay: str = "KHÔNG_RÕ"
    dai_han_20_50_ngay: str = "KHÔNG_RÕ"


class Confidence(BaseModel):
    short_term: float = 0.0
    medium_term: float = 0.0
    long_term: float = 0.0
    short_score: float = 0.0
    med_score: float = 0.0
    long_score: float = 0.0


class PredictionResult(BaseModel):
    metadata: Dict[str, Any]
    signals: SignalDetail
    trend: Trend
    confidence: Confidence
    entry_advice: str
    price_action: Dict[str, str]
    score_details: Dict[str, int]


class PredictionResponse(BaseModel):
    symbol: str
    prediction: PredictionResult


class PredictionsListResponse(BaseModel):
    predictions: Dict[str, PredictionResult]
    count: int


class PipelineTriggerResponse(BaseModel):
    status: str
    symbols: List[str]


class ErrorResponse(BaseModel):
    detail: str
    timestamp: str
