"""WebChat 客户端 - 对接 Web 聊天系统"""

from __future__ import annotations

from typing import Any

import requests


class WebChatClient:
    """WebChat 客户端 - 获取聊天消息和发送回复"""
    
    def __init__(
        self,
        api_base_url: str,
        api_key: str | None = None,
        timeout: int = 10,
    ):
        self.api_base_url = api_base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
    
    def get_pending_messages(self) -> list[dict[str, Any]]:
        """获取待处理的聊天消息"""
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        try:
            response = requests.get(
                f"{self.api_base_url}/api/messages/pending",
                headers=headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("messages", [])
        except Exception as exc:
            print(f"[ERROR] 获取 WebChat 消息失败: {exc}")
            return []
    
    def send_reply(
        self,
        message_id: str,
        reply_text: str,
    ) -> dict[str, Any]:
        """发送回复消息"""
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        try:
            response = requests.post(
                f"{self.api_base_url}/api/messages/{message_id}/reply",
                headers=headers,
                json={"text": reply_text},
                timeout=self.timeout,
            )
            response.raise_for_status()
            return {"ok": True, "response": response.json()}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}
    
    def mark_as_processed(self, message_id: str) -> dict[str, Any]:
        """标记消息为已处理"""
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        try:
            response = requests.post(
                f"{self.api_base_url}/api/messages/{message_id}/processed",
                headers=headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
            return {"ok": True}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}
