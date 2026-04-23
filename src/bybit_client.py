from __future__ import annotations

from typing import Any
from pybit.unified_trading import HTTP


class BybitClient:
    def __init__(self, api_key: str, api_secret: str, testnet: bool):
        self.session = HTTP(api_key=api_key, api_secret=api_secret, testnet=testnet)

    def get_spot_instruments(self) -> list[dict[str, Any]]:
        result = self.session.get_instruments_info(category="spot")
        return result.get("result", {}).get("list", [])

    def get_tickers(self, symbol: str | None = None) -> list[dict[str, Any]]:
        params: dict[str, Any] = {"category": "spot"}
        if symbol:
            params["symbol"] = symbol
        result = self.session.get_tickers(**params)
        return result.get("result", {}).get("list", [])

    def place_market_buy_by_quote(self, symbol: str, usdt_amount: float) -> dict[str, Any]:
        return self.session.place_order(
            category="spot",
            symbol=symbol,
            side="Buy",
            orderType="Market",
            qty=str(usdt_amount),
            marketUnit="quoteCoin",
        )
