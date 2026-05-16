"""
结构化日志 - 更好的可观测性

优化点：
1. 结构化日志输出
2. 支持多种日志级别
3. 上下文信息自动注入
4. 便于日志分析和查询
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime
from typing import Any


class StructuredLogger:
    """
    结构化日志记录器
    
    输出 JSON 格式的日志，便于 ELK、Splunk 等日志系统分析。
    """

    def __init__(self, name: str, level: int = logging.INFO):
        """
        初始化日志记录器
        
        Args:
            name: 日志记录器名称
            level: 日志级别
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # 配置处理器
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(StructuredFormatter())
            self.logger.addHandler(handler)

    def _log(self, level: str, message: str, **kwargs: Any) -> None:
        """
        记录日志
        
        Args:
            level: 日志级别
            message: 日志消息
            **kwargs: 额外的上下文信息
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            **kwargs,
        }

        log_method = getattr(self.logger, level.lower())
        log_method(json.dumps(log_entry, ensure_ascii=False))

    def debug(self, message: str, **kwargs: Any) -> None:
        """记录 DEBUG 级别日志"""
        self._log("DEBUG", message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        """记录 INFO 级别日志"""
        self._log("INFO", message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """记录 WARNING 级别日志"""
        self._log("WARNING", message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """记录 ERROR 级别日志"""
        self._log("ERROR", message, **kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        """记录 CRITICAL 级别日志"""
        self._log("CRITICAL", message, **kwargs)


class StructuredFormatter(logging.Formatter):
    """结构化日志格式化器"""

    def format(self, record: logging.LogRecord) -> str:
        """
        格式化日志记录
        
        Args:
            record: 日志记录
        
        Returns:
            str: 格式化后的日志
        """
        # 如果消息已经是 JSON，直接返回
        try:
            json.loads(record.getMessage())
            return record.getMessage()
        except (json.JSONDecodeError, ValueError):
            # 否则包装为 JSON
            log_entry = {
                "timestamp": datetime.fromtimestamp(record.created).isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
            }

            if record.exc_info:
                log_entry["exception"] = self.formatException(record.exc_info)

            return json.dumps(log_entry, ensure_ascii=False)


# 全局日志记录器实例
_loggers: dict[str, StructuredLogger] = {}


def get_logger(name: str = "automage") -> StructuredLogger:
    """
    获取日志记录器
    
    Args:
        name: 日志记录器名称
    
    Returns:
        StructuredLogger: 日志记录器实例
    """
    if name not in _loggers:
        _loggers[name] = StructuredLogger(name)
    return _loggers[name]


# 便捷函数
def log_skill_execution(
    skill_name: str,
    actor_user_id: str,
    duration_ms: float,
    success: bool,
    **kwargs: Any,
) -> None:
    """
    记录 Skill 执行日志
    
    Args:
        skill_name: Skill 名称
        actor_user_id: 执行用户 ID
        duration_ms: 执行时间（毫秒）
        success: 是否成功
        **kwargs: 额外信息
    """
    logger = get_logger("automage.skill")
    logger.info(
        "skill_executed",
        skill_name=skill_name,
        actor_user_id=actor_user_id,
        duration_ms=duration_ms,
        success=success,
        **kwargs,
    )


def log_api_request(
    method: str,
    path: str,
    status_code: int,
    duration_ms: float,
    request_id: str,
    **kwargs: Any,
) -> None:
    """
    记录 API 请求日志
    
    Args:
        method: HTTP 方法
        path: 请求路径
        status_code: 状态码
        duration_ms: 响应时间（毫秒）
        request_id: 请求 ID
        **kwargs: 额外信息
    """
    logger = get_logger("automage.api")
    logger.info(
        "api_request",
        method=method,
        path=path,
        status_code=status_code,
        duration_ms=duration_ms,
        request_id=request_id,
        **kwargs,
    )


def log_cache_operation(
    operation: str,
    cache_key: str,
    hit: bool | None = None,
    **kwargs: Any,
) -> None:
    """
    记录缓存操作日志
    
    Args:
        operation: 操作类型（get, set, delete）
        cache_key: 缓存键
        hit: 是否命中（仅 get 操作）
        **kwargs: 额外信息
    """
    logger = get_logger("automage.cache")
    logger.debug(
        "cache_operation",
        operation=operation,
        cache_key=cache_key,
        hit=hit,
        **kwargs,
    )


def log_error(
    error_type: str,
    error_message: str,
    **kwargs: Any,
) -> None:
    """
    记录错误日志
    
    Args:
        error_type: 错误类型
        error_message: 错误消息
        **kwargs: 额外信息
    """
    logger = get_logger("automage.error")
    logger.error(
        "error_occurred",
        error_type=error_type,
        error_message=error_message,
        **kwargs,
    )
