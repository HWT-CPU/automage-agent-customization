from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from threading import Lock
from typing import Any, Protocol

from automage_agents.config.settings import RuntimeSettings


logger = logging.getLogger("automage.api")


@dataclass(slots=True)
class IdempotencyRecord:
    request_fingerprint: str
    status_code: int
    response_body: dict[str, Any]
    expires_at: float | None = None

    def to_payload(self) -> dict[str, Any]:
        return {
            "request_fingerprint": self.request_fingerprint,
            "status_code": self.status_code,
            "response_body": self.response_body,
        }

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "IdempotencyRecord":
        return cls(
            request_fingerprint=str(payload.get("request_fingerprint", "")),
            status_code=int(payload.get("status_code", 0)),
            response_body=dict(payload.get("response_body", {})),
            expires_at=None,
        )


class AbuseProtectionStore(Protocol):
    async def allow(self, key: str, *, limit: int, window_seconds: int) -> bool: ...

    async def get_idempotency(self, key: str) -> IdempotencyRecord | None: ...

    async def reserve_idempotency(self, key: str, *, fingerprint: str, ttl_seconds: int) -> bool: ...

    async def save_idempotency(
        self,
        key: str,
        *,
        fingerprint: str,
        status_code: int,
        response_body: dict[str, Any],
        ttl_seconds: int,
    ) -> None: ...


class MemoryAbuseProtectionStore:
    def __init__(self) -> None:
        self._events: dict[str, list[float]] = {}
        self._records: dict[str, IdempotencyRecord] = {}
        self._lock = Lock()

    async def allow(self, key: str, *, limit: int, window_seconds: int) -> bool:
        now = time.time()
        threshold = now - window_seconds
        with self._lock:
            events = [event for event in self._events.get(key, []) if event >= threshold]
            if len(events) >= limit:
                self._events[key] = events
                return False
            events.append(now)
            self._events[key] = events
            return True

    async def get_idempotency(self, key: str) -> IdempotencyRecord | None:
        now = time.time()
        with self._lock:
            self._cleanup_locked(now)
            return self._records.get(key)

    async def reserve_idempotency(self, key: str, *, fingerprint: str, ttl_seconds: int) -> bool:
        now = time.time()
        with self._lock:
            self._cleanup_locked(now)
            if key in self._records:
                return False
            self._records[key] = IdempotencyRecord(
                request_fingerprint=fingerprint,
                status_code=0,
                response_body={"detail": "request_in_progress"},
                expires_at=now + ttl_seconds,
            )
            return True

    async def save_idempotency(
        self,
        key: str,
        *,
        fingerprint: str,
        status_code: int,
        response_body: dict[str, Any],
        ttl_seconds: int,
    ) -> None:
        now = time.time()
        with self._lock:
            self._cleanup_locked(now)
            self._records[key] = IdempotencyRecord(
                request_fingerprint=fingerprint,
                status_code=status_code,
                response_body=response_body,
                expires_at=now + ttl_seconds,
            )

    def _cleanup_locked(self, now: float) -> None:
        expired_keys = [key for key, record in self._records.items() if (record.expires_at or 0) <= now]
        for key in expired_keys:
            self._records.pop(key, None)


class RedisAbuseProtectionStore:
    def __init__(
        self,
        *,
        redis_url: str,
        key_prefix: str,
        fallback_store: MemoryAbuseProtectionStore,
    ) -> None:
        self._client = _build_async_redis_client(redis_url)
        self._key_prefix = key_prefix.strip() or "automage"
        self._fallback_store = fallback_store
        self._degraded = False

    async def allow(self, key: str, *, limit: int, window_seconds: int) -> bool:
        if self._degraded:
            return await self._fallback_store.allow(key, limit=limit, window_seconds=window_seconds)
        try:
            redis_key = self._redis_key("rate", key)
            current = await self._client.incr(redis_key)
            if int(current) == 1:
                await self._client.expire(redis_key, window_seconds)
            return int(current) <= limit
        except Exception as exc:
            self._degrade(exc)
            return await self._fallback_store.allow(key, limit=limit, window_seconds=window_seconds)

    async def get_idempotency(self, key: str) -> IdempotencyRecord | None:
        if self._degraded:
            return await self._fallback_store.get_idempotency(key)
        try:
            redis_key = self._redis_key("idem", key)
            payload = await self._client.get(redis_key)
            if payload is None:
                return None
            if isinstance(payload, bytes):
                payload = payload.decode("utf-8")
            return IdempotencyRecord.from_payload(json.loads(payload))
        except Exception as exc:
            self._degrade(exc)
            return await self._fallback_store.get_idempotency(key)

    async def reserve_idempotency(self, key: str, *, fingerprint: str, ttl_seconds: int) -> bool:
        if self._degraded:
            return await self._fallback_store.reserve_idempotency(key, fingerprint=fingerprint, ttl_seconds=ttl_seconds)
        try:
            redis_key = self._redis_key("idem", key)
            record = IdempotencyRecord(
                request_fingerprint=fingerprint,
                status_code=0,
                response_body={"detail": "request_in_progress"},
            )
            return bool(
                await self._client.set(
                    redis_key,
                    json.dumps(record.to_payload(), ensure_ascii=False),
                    ex=ttl_seconds,
                    nx=True,
                )
            )
        except Exception as exc:
            self._degrade(exc)
            return await self._fallback_store.reserve_idempotency(key, fingerprint=fingerprint, ttl_seconds=ttl_seconds)

    async def save_idempotency(
        self,
        key: str,
        *,
        fingerprint: str,
        status_code: int,
        response_body: dict[str, Any],
        ttl_seconds: int,
    ) -> None:
        if self._degraded:
            await self._fallback_store.save_idempotency(
                key,
                fingerprint=fingerprint,
                status_code=status_code,
                response_body=response_body,
                ttl_seconds=ttl_seconds,
            )
            return
        try:
            redis_key = self._redis_key("idem", key)
            record = IdempotencyRecord(
                request_fingerprint=fingerprint,
                status_code=status_code,
                response_body=response_body,
            )
            await self._client.set(
                redis_key,
                json.dumps(record.to_payload(), ensure_ascii=False),
                ex=ttl_seconds,
            )
        except Exception as exc:
            self._degrade(exc)
            await self._fallback_store.save_idempotency(
                key,
                fingerprint=fingerprint,
                status_code=status_code,
                response_body=response_body,
                ttl_seconds=ttl_seconds,
            )

    def _redis_key(self, namespace: str, key: str) -> str:
        return f"{self._key_prefix}:{namespace}:{key}"

    def _degrade(self, exc: Exception) -> None:
        if self._degraded:
            return
        self._degraded = True
        logger.warning("redis abuse protection degraded to memory backend: %s", exc)


def build_abuse_protection_store(settings: RuntimeSettings) -> AbuseProtectionStore:
    memory_store = MemoryAbuseProtectionStore()
    if settings.abuse_protection_backend != "redis":
        return memory_store
    if not settings.redis_url:
        logger.warning("redis abuse protection requested but redis_url is empty, fallback to memory backend")
        return memory_store
    try:
        return RedisAbuseProtectionStore(
            redis_url=settings.redis_url,
            key_prefix=settings.redis_key_prefix,
            fallback_store=memory_store,
        )
    except Exception as exc:
        logger.warning("failed to initialize redis abuse protection backend, fallback to memory: %s", exc)
        return memory_store


def _build_async_redis_client(redis_url: str):
    try:
        from redis import asyncio as redis_async
    except ImportError as exc:
        raise RuntimeError("redis package is not installed") from exc
    return redis_async.from_url(redis_url, encoding="utf-8", decode_responses=True)
