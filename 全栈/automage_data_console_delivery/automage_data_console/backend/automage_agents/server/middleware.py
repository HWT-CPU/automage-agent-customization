from __future__ import annotations

import hashlib
import logging
import time
from uuid import uuid4

from fastapi.responses import JSONResponse
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from automage_agents.config import load_runtime_settings
from automage_agents.server.abuse_store import build_abuse_protection_store
from automage_agents.server.request_context import request_id_var


logger = logging.getLogger("automage.api")
_settings = load_runtime_settings("configs/automage.local.toml")
_abuse_store = None
_abuse_store_signature: tuple[str, str | None, str] | None = None


class RequestTrackingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-Id") or str(uuid4())
        start = time.perf_counter()

        request.state.request_id = request_id
        token = request_id_var.set(request_id)

        try:
            response = await call_next(request)
        finally:
            request_id_var.reset(token)

        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        response.headers["X-Request-Id"] = request_id
        response.headers["X-Process-Time-Ms"] = str(duration_ms)

        logger.info(
            "request_id=%s method=%s path=%s status=%s duration_ms=%s",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response


class AbuseProtectionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not _settings.abuse_protection_enabled:
            return await call_next(request)

        abuse_store = _get_abuse_store()
        request_id = getattr(request.state, "request_id", None) or request.headers.get("X-Request-Id") or str(uuid4())
        client_key = request.headers.get("X-User-Id") or (request.client.host if request.client else "anonymous")
        path = request.url.path
        limit = _settings.rate_limit_max_requests
        window = _settings.rate_limit_window_seconds
        if request.method in {"POST", "PATCH", "PUT", "DELETE"} and _is_write_protected_path(path):
            limit = max(1, min(limit, 20))

        rate_limit_key = f"{client_key}:{request.method}:{path}"
        if not await abuse_store.allow(rate_limit_key, limit=limit, window_seconds=window):
            return JSONResponse(
                status_code=429,
                content={"detail": "rate_limit_exceeded", "request_id": request_id},
                headers={"X-Request-Id": request_id},
            )

        body_bytes = await request.body()
        request._body = body_bytes
        if request.method in {"POST", "PATCH", "PUT", "DELETE"} and _is_write_protected_path(path):
            idempotency_key = request.headers.get("Idempotency-Key")
            if idempotency_key:
                fingerprint = _fingerprint_request(request, client_key, body_bytes)
                store_key = f"{client_key}:{request.method}:{path}:{idempotency_key}"
                existing = await abuse_store.get_idempotency(store_key)
                conflict = _build_idempotency_conflict_response(
                    existing,
                    fingerprint=fingerprint,
                    request_id=request_id,
                    idempotency_key=idempotency_key,
                )
                if conflict is not None:
                    return conflict
                if not await abuse_store.reserve_idempotency(
                    store_key,
                    fingerprint=fingerprint,
                    ttl_seconds=_settings.idempotency_ttl_seconds,
                ):
                    existing = await abuse_store.get_idempotency(store_key)
                    conflict = _build_idempotency_conflict_response(
                        existing,
                        fingerprint=fingerprint,
                        request_id=request_id,
                        idempotency_key=idempotency_key,
                    )
                    if conflict is not None:
                        return conflict
                response = await call_next(request)
                if response.status_code < 500:
                    payload = await _extract_json_response(response)
                    await abuse_store.save_idempotency(
                        store_key,
                        fingerprint=fingerprint,
                        status_code=response.status_code,
                        response_body=payload,
                        ttl_seconds=_settings.idempotency_ttl_seconds,
                    )
                    response.headers["X-Idempotency-Key"] = idempotency_key
                return response

        return await call_next(request)


def _is_write_protected_path(path: str) -> bool:
    for item in _settings.write_protected_paths:
        if path == item or path.startswith(f"{item}/"):
            return True
    return False


def _fingerprint_request(request: Request, client_key: str, body_bytes: bytes) -> str:
    digest = hashlib.sha256()
    digest.update(client_key.encode("utf-8"))
    digest.update(request.method.encode("utf-8"))
    digest.update(request.url.path.encode("utf-8"))
    digest.update(body_bytes)
    return digest.hexdigest()


async def _extract_json_response(response) -> dict:
    body = b""
    async for chunk in response.body_iterator:
        body += chunk
    response.body_iterator = _single_chunk_iter(body)
    if not body:
        return {"detail": "ok"}
    try:
        import json

        return json.loads(body.decode("utf-8"))
    except Exception:
        return {"detail": body.decode("utf-8", errors="ignore")}


async def _single_chunk_iter(body: bytes):
    yield body


def _get_abuse_store():
    global _abuse_store, _abuse_store_signature
    signature = (
        _settings.abuse_protection_backend,
        _settings.redis_url,
        _settings.redis_key_prefix,
    )
    if _abuse_store is None or _abuse_store_signature != signature:
        _abuse_store = build_abuse_protection_store(_settings)
        _abuse_store_signature = signature
    return _abuse_store


def _build_idempotency_conflict_response(existing, *, fingerprint: str, request_id: str, idempotency_key: str):
    if existing is None:
        return None
    headers = {"X-Request-Id": request_id, "X-Idempotency-Key": idempotency_key}
    if existing.request_fingerprint != fingerprint:
        return JSONResponse(
            status_code=409,
            content={
                "detail": "idempotency_key_conflict",
                "request_id": request_id,
                "idempotency_conflict": True,
            },
            headers=headers,
        )
    if existing.status_code == 0:
        return JSONResponse(
            status_code=409,
            content={
                "detail": "request_in_progress",
                "request_id": request_id,
                "idempotency_in_progress": True,
            },
            headers=headers,
        )
    return JSONResponse(
        status_code=409,
        content={**existing.response_body, "request_id": request_id, "idempotency_replayed": True},
        headers=headers,
    )
