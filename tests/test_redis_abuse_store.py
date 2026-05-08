from __future__ import annotations

import unittest
from unittest.mock import patch

from automage_agents.config.settings import RuntimeSettings
from automage_agents.server.abuse_store import IdempotencyRecord, RedisAbuseProtectionStore, build_abuse_protection_store


class FakeRedisClient:
    def __init__(self) -> None:
        self._data: dict[str, str] = {}
        self._counts: dict[str, int] = {}
        self._expirations: dict[str, int] = {}

    async def incr(self, key: str) -> int:
        self._counts[key] = self._counts.get(key, 0) + 1
        return self._counts[key]

    async def expire(self, key: str, seconds: int) -> bool:
        self._expirations[key] = seconds
        return True

    async def get(self, key: str):
        return self._data.get(key)

    async def set(self, key: str, value: str, ex: int | None = None, nx: bool = False):
        if nx and key in self._data:
            return False
        self._data[key] = value
        if ex is not None:
            self._expirations[key] = ex
        return True


class RedisAbuseStoreTests(unittest.IsolatedAsyncioTestCase):
    async def test_redis_backend_rate_limit_and_idempotency_work(self) -> None:
        fake_client = FakeRedisClient()
        with patch("automage_agents.server.abuse_store._build_async_redis_client", return_value=fake_client):
            store = RedisAbuseProtectionStore(
                redis_url="redis://:automage@127.0.0.1:6379/0",
                key_prefix="automage-test",
                fallback_store=build_abuse_protection_store(RuntimeSettings()),
            )

            first = await store.allow("user_a:POST:/api/v1/tasks", limit=2, window_seconds=60)
            second = await store.allow("user_a:POST:/api/v1/tasks", limit=2, window_seconds=60)
            third = await store.allow("user_a:POST:/api/v1/tasks", limit=2, window_seconds=60)

            self.assertTrue(first)
            self.assertTrue(second)
            self.assertFalse(third)

            reserved = await store.reserve_idempotency("user_a:POST:/api/v1/tasks:key1", fingerprint="fp-1", ttl_seconds=300)
            self.assertTrue(reserved)

            record = await store.get_idempotency("user_a:POST:/api/v1/tasks:key1")
            self.assertIsInstance(record, IdempotencyRecord)
            self.assertEqual(record.request_fingerprint, "fp-1")
            self.assertEqual(record.status_code, 0)

            await store.save_idempotency(
                "user_a:POST:/api/v1/tasks:key1",
                fingerprint="fp-1",
                status_code=200,
                response_body={"code": 200, "msg": "ok"},
                ttl_seconds=300,
            )
            saved = await store.get_idempotency("user_a:POST:/api/v1/tasks:key1")
            self.assertEqual(saved.status_code, 200)
            self.assertEqual(saved.response_body["msg"], "ok")

    async def test_build_store_falls_back_to_memory_when_redis_unavailable(self) -> None:
        settings = RuntimeSettings(
            abuse_protection_enabled=True,
            abuse_protection_backend="redis",
            redis_url="redis://:automage@127.0.0.1:6379/0",
        )
        with patch("automage_agents.server.abuse_store._build_async_redis_client", side_effect=RuntimeError("boom")):
            store = build_abuse_protection_store(settings)

        allowed = await store.allow("fallback:rate", limit=1, window_seconds=60)
        self.assertTrue(allowed)


if __name__ == "__main__":
    unittest.main()
