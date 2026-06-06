"""Voting System — weighted voting với ngưỡng ≥70% đồng thuận.

Cách hoạt động:
1. Mỗi indicator vote: MUA (+1), BÁN (-1), hoặc KHÔNG_RÕ (0)
2. Tính weighted vote: ∑(vote × weight) / ∑(weight của vote không trung tính)
3. Nếu weighted vote >= +0.70 → MUA (tự tin = vote%)
4. Nếu weighted vote <= -0.70 → BÁN (tự tin = vote%)
5. Còn lại → KHÔNG_RÕ (không đủ đồng thuận)
"""

import numpy as np
from typing import Dict, Any, List


_WEIGHTS: Dict[str, float] = {
    "supertrend": 1.5,
    "adx": 1.4,
    "ichimoku": 1.3,
    "trend_ma": 1.2,
    "price_action": 1.2,
    "parabolic_sar": 1.1,
    "macd": 1.0,
    "aroon": 1.0,
    "vortex": 0.9,
    "cmf": 0.9,
    "rsi": 0.7,
    "mfi": 0.8,
    "stoch_rsi": 0.6,
    "williams_r": 0.6,
    "cci": 0.5,
    "bollinger": 0.5,
    "donchian": 0.5,
}


def vote_value(scores: List[float], weights: List[float]) -> float:
    """Tính weighted vote: 1 = MUA, -1 = BÁN, 0 = trung tính."""
    if not scores or not weights:
        return 0.0
    arr = np.array(scores)
    w = np.array(weights)
    return float(np.average(arr, weights=w))


def validate_vote(name: str, vote: float, votes: list, vweights: list):
    """vote = +1 (MUA), -1 (BÁN), 0 (trung tính)."""
    votes.append(vote)
    vweights.append(_WEIGHTS.get(name, 0.5))


def final_vote(scores: List[float], weights: List[float]) -> Dict[str, Any]:
    """
    Voting system: đếm % weighted votes đồng thuận với hướng chính.
    - Mỗi indicator vote: >0 = MUA, <0 = BÁN, =0 = trung tính
    - Confidence = % weighted votes cùng hướng (bỏ qua trung tính)
    - Chỉ emit MUA/BÁN khi confidence >= 70%
    """
    if not scores:
        return {"signal": "KHÔNG_RÕ", "score": 0.0, "confidence": 0.0, "votes": 0}

    w_vote = vote_value(scores, weights)
    buy_w = sum(w for s, w in zip(scores, weights) if s > 0)
    sell_w = sum(w for s, w in zip(scores, weights) if s < 0)
    total_active = buy_w + sell_w

    if total_active == 0:
        return {"signal": "KHÔNG_RÕ", "score": 0.0, "confidence": 0.0, "votes": len(scores)}

    if w_vote > 0:
        confidence = buy_w / total_active * 100
    else:
        confidence = sell_w / total_active * 100

    if confidence >= 70:
        signal = "MUA" if w_vote > 0 else "BÁN"
    else:
        signal = "KHÔNG_RÕ"

    return {
        "signal": signal,
        "score": round(w_vote, 2),
        "confidence": round(confidence, 1),
        "votes": len(scores),
    }
