from __future__ import annotations

from typing import Iterable
from .models import Signal


def safe_float(value, default=0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


def safe_int(value, default=0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def build_signal_from_pair(pair: dict, watchlist_symbols: set[str]) -> Signal | None:
    chain_id = pair.get("chainId", "")
    pair_address = pair.get("pairAddress", "")
    url = pair.get("url", "")
    base_token = pair.get("baseToken", {}) or {}
    symbol = str(base_token.get("symbol", "")).upper()
    name = str(base_token.get("name", ""))

    price_usd = safe_float(pair.get("priceUsd"))
    liquidity_usd = safe_float((pair.get("liquidity") or {}).get("usd"))
    volume_5m = safe_float((pair.get("volume") or {}).get("m5"))
    price_change_5m = safe_float((pair.get("priceChange") or {}).get("m5"))
    price_change_1h = safe_float((pair.get("priceChange") or {}).get("h1"))
    txns_5m = (pair.get("txns") or {}).get("m5") or {}
    buys_5m = safe_int(txns_5m.get("buys"))
    sells_5m = safe_int(txns_5m.get("sells"))
    fdv = safe_float(pair.get("fdv"))
    market_cap = safe_float(pair.get("marketCap"))

    bybit_symbol = f"{symbol}USDT" if f"{symbol}USDT" in watchlist_symbols else None
    if symbol == "1000SHIB":
        bybit_symbol = "SHIB1000USDT" if "SHIB1000USDT" in watchlist_symbols else bybit_symbol

    total_txns = buys_5m + sells_5m
    if total_txns <= 0:
        return None

    buy_sell_ratio = buys_5m / max(sells_5m, 1)
    score = 0.0
    score += min(liquidity_usd / 100000, 5)
    score += min(volume_5m / 100000, 5)
    score += min(max(price_change_5m, 0) / 5, 4)
    score += min(buy_sell_ratio, 4)
    score += min(total_txns / 20, 4)

    return Signal(
        chain_id=chain_id,
        pair_address=pair_address,
        dex_url=url,
        base_symbol=symbol,
        base_name=name,
        price_usd=price_usd,
        liquidity_usd=liquidity_usd,
        volume_5m_usd=volume_5m,
        price_change_5m_pct=price_change_5m,
        price_change_1h_pct=price_change_1h,
        buys_5m=buys_5m,
        sells_5m=sells_5m,
        fdv=fdv,
        market_cap=market_cap,
        score=score,
        reason=f"liq={liquidity_usd:.0f}, vol5m={volume_5m:.0f}, ch5m={price_change_5m:.1f}%, b/s={buy_sell_ratio:.2f}, txns={total_txns}",
        bybit_symbol=bybit_symbol,
    )


def passes_filters(signal: Signal, *, min_liq: float, min_vol_5m: float, min_ch5m: float,
                   max_ch1h: float, min_buy_sell_ratio: float, min_unique_buyers: int) -> bool:
    ratio = signal.buys_5m / max(signal.sells_5m, 1)
    return all([
        signal.liquidity_usd >= min_liq,
        signal.volume_5m_usd >= min_vol_5m,
        signal.price_change_5m_pct >= min_ch5m,
        signal.price_change_1h_pct <= max_ch1h,
        ratio >= min_buy_sell_ratio,
        signal.buys_5m >= min_unique_buyers,
    ])


def rank_signals(signals: Iterable[Signal]) -> list[Signal]:
    return sorted(signals, key=lambda s: s.score, reverse=True)
