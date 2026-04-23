from __future__ import annotations

import time
from typing import Any

from .config import get_settings
from .http_utils import HttpClient
from .dexscreener_client import DexScreenerClient
from .telegram_client import TelegramClient
from .strategy import build_signal_from_pair, passes_filters, rank_signals
from .storage import LocalState
from .bybit_client import BybitClient


def format_signal_message(signal) -> str:
    bybit_text = signal.bybit_symbol or "нет пары в watchlist Bybit"
    return (
        f"🔥 Сигнал: {signal.base_symbol} ({signal.base_name})\n"
        f"Chain: {signal.chain_id}\n"
        f"Price: ${signal.price_usd:.8f}\n"
        f"Liquidity: ${signal.liquidity_usd:,.0f}\n"
        f"Volume 5m: ${signal.volume_5m_usd:,.0f}\n"
        f"Price change 5m: {signal.price_change_5m_pct:.2f}%\n"
        f"Price change 1h: {signal.price_change_1h_pct:.2f}%\n"
        f"Buys/Sells 5m: {signal.buys_5m}/{signal.sells_5m}\n"
        f"FDV: ${signal.fdv:,.0f}\n"
        f"Market Cap: ${signal.market_cap:,.0f}\n"
        f"Bybit: {bybit_text}\n"
        f"Score: {signal.score:.2f}\n"
        f"Почему прошёл: {signal.reason}\n"
        f"DEX: {signal.dex_url}"
    )


def fetch_candidate_pairs(dex: DexScreenerClient, chain_filter: set[str]) -> list[dict[str, Any]]:
    profiles = dex.get_latest_profiles()
    boosts = dex.get_latest_boosts()
    top_boosts = dex.get_top_boosts()

    resolved_pairs: list[dict[str, Any]] = []
    seen_pair_addresses = set()
    seen_tokens = set()

    for item in profiles + boosts + top_boosts:
        chain_id = item.get("chainId")
        token_address = item.get("tokenAddress")
        if not chain_id or not token_address:
            continue
        if chain_filter and chain_id not in chain_filter:
            continue

        token_key = (chain_id, token_address)
        if token_key in seen_tokens:
            continue
        seen_tokens.add(token_key)

        try:
            orders = dex.get_orders(chain_id, token_address)
            if not (orders or item in boosts or item in top_boosts):
                continue

            token_pairs = dex.get_token_pairs(chain_id, token_address)
            for pair in token_pairs[:3]:
                pair_address = pair.get("pairAddress")
                if not pair_address or pair_address in seen_pair_addresses:
                    continue
                seen_pair_addresses.add(pair_address)
                resolved_pairs.append(pair)
        except Exception:
            continue

    return resolved_pairs[:100]


def scan_once():
    settings = get_settings()
    http = HttpClient(timeout=20)
    dex = DexScreenerClient(http)
    tg = TelegramClient(http, settings.telegram_bot_token, settings.telegram_chat_id)
    state = LocalState()
    bybit = None
    if settings.enable_auto_buy and settings.bybit_api_key and settings.bybit_api_secret:
        bybit = BybitClient(settings.bybit_api_key, settings.bybit_api_secret, settings.bybit_testnet)

    print("[scan] start")
    pairs = fetch_candidate_pairs(dex, set(settings.chain_filter))
    if not pairs:
        print("[scan] no candidate pairs found")
        return

    signals = []
    watchlist = set(settings.watchlist_bybit_symbols)
    for pair in pairs:
        signal = build_signal_from_pair(pair, watchlist)
        if not signal:
            continue
        if passes_filters(
            signal,
            min_liq=settings.min_liquidity_usd,
            min_vol_5m=settings.min_volume_5m_usd,
            min_ch5m=settings.min_price_change_5m_pct,
            max_ch1h=settings.max_price_change_1h_pct,
            min_buy_sell_ratio=settings.min_buy_sell_ratio,
            min_unique_buyers=settings.min_unique_buyers,
        ):
            signals.append(signal)

    ranked = rank_signals(signals)[:5]
    print(f"[scan] filtered signals: {len(ranked)}")

    for signal in ranked:
        key = f"{signal.chain_id}:{signal.pair_address}"
        if state.already_sent(key):
            continue

        tg.send_message(format_signal_message(signal))
        state.mark_sent(key)

        if bybit and signal.bybit_symbol and state.position_count() < settings.max_open_positions:
            try:
                result = bybit.place_market_buy_by_quote(signal.bybit_symbol, settings.order_usdt_per_trade)
                tg.send_message(
                    f"✅ Auto-buy executed on Bybit\n"
                    f"Symbol: {signal.bybit_symbol}\n"
                    f"Amount: {settings.order_usdt_per_trade} USDT\n"
                    f"Response: {result.get('retMsg', 'OK')}"
                )
                state.add_position(signal.bybit_symbol, signal.price_usd)
            except Exception as exc:
                tg.send_message(f"❌ Bybit order failed for {signal.bybit_symbol}: {exc}")


def run():
    settings = get_settings()
    print("[bot] started")
    print(f"[bot] scan interval: {settings.scan_interval_seconds}s")
    while True:
        try:
            scan_once()
        except KeyboardInterrupt:
            print("[bot] stopped")
            raise
        except Exception as exc:
            print(f"[bot] error: {exc}")
        time.sleep(settings.scan_interval_seconds)
