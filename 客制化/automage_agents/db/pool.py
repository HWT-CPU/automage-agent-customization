"""
数据库连接池优化

优化点：
1. 配置优化的连接池参数
2. 连接健康检查
3. 连接回收机制
4. 连接池监控
"""

from __future__ import annotations

import time
from typing import Any

from sqlalchemy import create_engine, event, pool
from sqlalchemy.engine import Engine
from sqlalchemy.pool import QueuePool

from automage_agents.config.settings import RuntimeSettings


class OptimizedDatabasePool:
    """优化的数据库连接池"""

    def __init__(self, settings: RuntimeSettings):
        self.settings = settings
        self._engine: Engine | None = None
        self._stats = {
            "connections_created": 0,
            "connections_closed": 0,
            "connections_recycled": 0,
            "checkout_count": 0,
            "checkin_count": 0,
        }

    def create_engine(self) -> Engine:
        """
        创建优化的数据库引擎
        
        Returns:
            Engine: SQLAlchemy 引擎
        """
        connection_string = self._build_connection_string()

        # 创建引擎，使用优化的连接池配置
        engine = create_engine(
            connection_string,
            poolclass=QueuePool,
            pool_size=20,  # 连接池大小（默认 5）
            max_overflow=10,  # 最大溢出连接数（默认 10）
            pool_timeout=30,  # 获取连接超时时间（秒）
            pool_recycle=3600,  # 连接回收时间（1小时）
            pool_pre_ping=True,  # 连接前检查可用性
            echo=False,  # 生产环境关闭 SQL 日志
            echo_pool=False,  # 关闭连接池日志
            connect_args={
                "connect_timeout": 10,  # 连接超时
                "options": "-c statement_timeout=30000",  # 查询超时 30 秒
            },
        )

        # 注册事件监听器
        self._register_event_listeners(engine)

        self._engine = engine
        return engine

    def _build_connection_string(self) -> str:
        """构建数据库连接字符串"""
        pg = self.settings.postgres
        return f"postgresql://{pg.user}:{pg.password}@{pg.host}:{pg.port}/{pg.database}?sslmode={pg.sslmode}"

    def _register_event_listeners(self, engine: Engine) -> None:
        """注册连接池事件监听器"""

        @event.listens_for(engine, "connect")
        def receive_connect(dbapi_conn, connection_record):
            """连接创建时触发"""
            self._stats["connections_created"] += 1
            connection_record.info["connected_at"] = time.time()

        @event.listens_for(engine, "close")
        def receive_close(dbapi_conn, connection_record):
            """连接关闭时触发"""
            self._stats["connections_closed"] += 1

        @event.listens_for(engine, "checkout")
        def receive_checkout(dbapi_conn, connection_record, connection_proxy):
            """从连接池取出连接时触发"""
            self._stats["checkout_count"] += 1

        @event.listens_for(engine, "checkin")
        def receive_checkin(dbapi_conn, connection_record):
            """连接归还到连接池时触发"""
            self._stats["checkin_count"] += 1

        @event.listens_for(engine, "soft_invalidate")
        def receive_soft_invalidate(dbapi_conn, connection_record, exception):
            """连接失效时触发"""
            self._stats["connections_recycled"] += 1

    def get_pool_status(self) -> dict[str, Any]:
        """
        获取连接池状态
        
        Returns:
            dict: 连接池状态信息
        """
        if self._engine is None:
            return {"error": "Engine not initialized"}

        pool_obj = self._engine.pool

        return {
            "pool_size": pool_obj.size(),
            "checked_in_connections": pool_obj.checkedin(),
            "checked_out_connections": pool_obj.checkedout(),
            "overflow_connections": pool_obj.overflow(),
            "total_connections": pool_obj.size() + pool_obj.overflow(),
            "stats": self._stats,
        }

    def dispose(self) -> None:
        """释放所有连接"""
        if self._engine:
            self._engine.dispose()


# 全局连接池实例
_pool_instance: OptimizedDatabasePool | None = None


def get_database_pool(settings: RuntimeSettings) -> OptimizedDatabasePool:
    """
    获取数据库连接池实例（单例）
    
    Args:
        settings: 运行时配置
    
    Returns:
        OptimizedDatabasePool: 连接池实例
    """
    global _pool_instance
    if _pool_instance is None:
        _pool_instance = OptimizedDatabasePool(settings)
    return _pool_instance


def get_engine(settings: RuntimeSettings) -> Engine:
    """
    获取数据库引擎
    
    Args:
        settings: 运行时配置
    
    Returns:
        Engine: SQLAlchemy 引擎
    """
    pool_obj = get_database_pool(settings)
    if pool_obj._engine is None:
        pool_obj.create_engine()
    return pool_obj._engine
