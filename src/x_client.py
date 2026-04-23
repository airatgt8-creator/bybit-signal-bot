from __future__ import annotations

from .http_utils import HttpClient


class XClient:
    """
    Опциональный модуль.
    Для реального использования нужен access plan в X Developer Platform.
    """

    def __init__(self, http: HttpClient, bearer_token: str):
        self.http = http
        self.bearer_token = bearer_token

    def count_mentions_recent(self, query: str) -> int:
        if not self.bearer_token:
            return 0
        headers = {"Authorization": f"Bearer {self.bearer_token}"}
        url = "https://api.x.com/2/tweets/search/recent"
        params_query = f"{url}?query={query}&max_results=10"
        try:
            data = self.http.get_json(params_query, headers=headers)
            return len(data.get("data", []))
        except Exception:
            return 0
