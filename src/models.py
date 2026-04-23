from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Signal:
    chain_id: str
    pair_address: str
    dex_url: str
    base_symbol: str
    base_name: str
    price_usd: float
    liquidity_usd: float
    volume_5m_usd: float
    price_change_5m_pct: float
    price_change_1h_pct: float
    buys_5m: int
    sells_5m: int
    fdv: float
    market_cap: float
    score: float
    reason: str
    bybit_symbol: Optional[str] = None
