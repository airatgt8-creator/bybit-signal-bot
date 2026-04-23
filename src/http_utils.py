from __future__ import annotations

import time
import requests


class HttpClient:
    def __init__(self, timeout: int = 20):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "bybit-signal-bot/1.0"})

    def get_json(self, url: str, headers: dict | None = None):
        response = self.session.get(url, timeout=self.timeout, headers=headers)
        response.raise_for_status()
        return response.json()

    def post_json(self, url: str, payload: dict, headers: dict | None = None):
        response = self.session.post(url, json=payload, timeout=self.timeout, headers=headers)
        response.raise_for_status()
        return response.json()

    def sleep(self, seconds: float):
        time.sleep(seconds)
