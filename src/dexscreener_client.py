from __future__ import annotations

from typing import Any
from .http_utils import HttpClient


class DexScreenerClient:
    def __init__(self, http: HttpClient):
        self.http = http
        self.base_url = "https://api.dexscreener.com"

    def get_latest_profiles(self) -> list[dict[str, Any]]:
        return self.http.get_json(f"{self.base_url}/token-profiles/latest/v1")

    def get_latest_boosts(self) -> list[dict[str, Any]]:
        return self.http.get_json(f"{self.base_url}/token-boosts/latest/v1")

    def get_top_boosts(self) -> list[dict[str, Any]]:
        return self.http.get_json(f"{self.base_url}/token-boosts/top/v1")

    def get_orders(self, chain_id: str, token_address: str) -> list[dict[str, Any]]:
        return self.http.get_json(f"{self.base_url}/orders/v1/{chain_id}/{token_address}")

    def get_pair(self, chain_id: str, pair_id: str) -> dict[str, Any]:
        data = self.http.get_json(f"{self.base_url}/latest/dex/pairs/{chain_id}/{pair_id}")
        pairs = data.get("pairs") or []
        if not pairs:
            raise ValueError(f"No pair data for {chain_id}:{pair_id}")
        return pairs[0]

    def get_token_pairs(self, chain_id: str, token_address: str) -> list[dict[str, Any]]:
        return self.http.get_json(f"{self.base_url}/token-pairs/v1/{chain_id}/{token_address}")
