"""
API 中间件 - 提供请求日志、性能监控、错误处理等功能

优化点：
1. 统一的请求日志记录（结构化日志）
2. 性能监控和追踪
3. 错误处理和格式化
4. CORS 配置优化
"""

from __future__ import annotations

import time
import uuid
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from automage_agents.core.exceptions import AutoMageAgentError
from automage_agents.utils.logger import log_api_request, log_error


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件 - 记录所有 API 请求（使用结构化日志）"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # 生成请求 ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # 记录请求开始
        start_time = time.time()
        method = request.method
        path = request.url.path

        # 处理请求
        try:
            response = await call_next(request)
            duration_ms = (time.time() - start_time) * 1000

            # 添加响应头
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"

            # 记录结构化日志
            log_api_request(
                method=method,
                path=path,
                status_code=response.status_code,
                duration_ms=duration_ms,
                request_id=request_id,
            )

            return response

        except Exception as exc:
            duration_ms = (time.time() - start_time) * 1000

            # 记录错误日志
            log_error(
                error_type=exc.__class__.__name__,
                error_message=str(exc),
                method=method,
                path=path,
                duration_ms=duration_ms,
                request_id=request_id,
            )
            raise


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """错误处理中间件 - 统一处理异常并返回标准格式"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except AutoMageAgentError as exc:
            # 业务异常
            return JSONResponse(
                status_code=400,
                content={
                    "ok": False,
                    "error": {
                        "type": exc.__class__.__name__,
                        "message": str(exc),
                        "request_id": getattr(request.state, "request_id", None),
                    },
                },
            )
        except ValueError as exc:
            # 参数验证异常
            return JSONResponse(
                status_code=400,
                content={
                    "ok": False,
                    "error": {
                        "type": "ValidationError",
                        "message": str(exc),
                        "request_id": getattr(request.state, "request_id", None),
                    },
                },
            )
        except Exception as exc:
            # 未知异常
            return JSONResponse(
                status_code=500,
                content={
                    "ok": False,
                    "error": {
                        "type": "InternalServerError",
                        "message": "An unexpected error occurred",
                        "request_id": getattr(request.state, "request_id", None),
                    },
                },
            )


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """性能监控中间件 - 监控慢请求（使用结构化日志）"""

    def __init__(self, app, slow_request_threshold_ms: float = 1000.0):
        super().__init__(app)
        self.slow_request_threshold_ms = slow_request_threshold_ms

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        response = await call_next(request)
        duration_ms = (time.time() - start_time) * 1000

        # 记录慢请求
        if duration_ms > self.slow_request_threshold_ms:
            from automage_agents.utils.logger import get_logger

            logger = get_logger("automage.performance")
            logger.warning(
                "slow_request_detected",
                method=request.method,
                path=request.url.path,
                duration_ms=duration_ms,
                threshold_ms=self.slow_request_threshold_ms,
            )

        return response
