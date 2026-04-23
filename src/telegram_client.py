from __future__ import annotations

from .http_utils import HttpClient


class TelegramClient:
    def __init__(self, http: HttpClient, bot_token: str, chat_id: str):
        self.http = http
        self.bot_token = bot_token
        self.chat_id = chat_id

    def send_message(self, text: str):
        if not self.bot_token or not self.chat_id:
            print("[telegram] TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID is empty. Message not sent.")
            print(text)
            return
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "disable_web_page_preview": True,
        }
        self.http.post_json(url, payload)
