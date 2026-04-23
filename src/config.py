from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


def _get_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


def _get_float(name: str, default: float) -> float:
    return float(os.getenv(name, str(default)).strip())


def _get_int(name: str, default: int) -> int:
    return int(os.getenv(name, str(default)).strip())


@dataclass(frozen=True)
class Settings:
    telegram_bot_token: str
    telegram_chat_id: str
    bybit_api_key: str
    bybit_api_secret: str
    bybit_testnet: bool
    enable_auto_buy: bool
    order_usdt_per_trade: float
    max_open_positions: int
    stop_loss_pct: float
    take_profit_pct: float
    scan_interval_seconds: int
    min_liquidity_usd: float
    min_volume_5m_usd: float
    min_price_change_5m_pct: float
    max_price_change_1h_pct: float
    min_buy_sell_ratio: float
    min_unique_buyers: int
    chain_filter: list[str]
    watchlist_bybit_symbols: list[str]
    enable_x_module: bool
    x_bearer_token: str
    x_query: str


def get_settings() -> Settings:
    chain_filter = [x.strip() for x in os.getenv("CHAIN_FILTER", "solana,base,ethereum,bsc").split(",") if x.strip()]
    watchlist = [x.strip().upper() for x in os.getenv("WATCHLIST_BYBIT_SYMBOLS", "").split(",") if x.strip()]
    return Settings(
        telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
        telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID", ""),
        bybit_api_key=os.getenv("BYBIT_API_KEY", ""),
        bybit_api_secret=os.getenv("BYBIT_API_SECRET", ""),
        bybit_testnet=_get_bool("BYBIT_TESTNET", True),
        enable_auto_buy=_get_bool("ENABLE_AUTO_BUY", False),
        order_usdt_per_trade=_get_float("ORDER_USDT_PER_TRADE", 10),
        max_open_positions=_get_int("MAX_OPEN_POSITIONS", 3),
        stop_loss_pct=_get_float("STOP_LOSS_PCT", 0.08),
        take_profit_pct=_get_float("TAKE_PROFIT_PCT", 0.18),
        scan_interval_seconds=_get_int("SCAN_INTERVAL_SECONDS", 60),
        min_liquidity_usd=_get_float("MIN_LIQUIDITY_USD", 100000),
        min_volume_5m_usd=_get_float("MIN_VOLUME_5M_USD", 150000),
        min_price_change_5m_pct=_get_float("MIN_PRICE_CHANGE_5M_PCT", 3),
        max_price_change_1h_pct=_get_float("MAX_PRICE_CHANGE_1H_PCT", 35),
        min_buy_sell_ratio=_get_float("MIN_BUY_SELL_RATIO", 1.15),
        min_unique_buyers=_get_int("MIN_UNIQUE_BUYERS", 20),
        chain_filter=chain_filter,
        watchlist_bybit_symbols=watchlist,
        enable_x_module=_get_bool("ENABLE_X_MODULE", False),
        x_bearer_token=os.getenv("X_BEARER_TOKEN", ""),
        x_query=os.getenv("X_QUERY", ""),
    )
