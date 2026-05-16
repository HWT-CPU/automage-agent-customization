"""
Redis 缓存实现 - 支持分布式部署

优化点：
1. 分布式缓存
2. 缓存持久化
3. 更大的缓存容量
4. 支持多实例部署
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from automage_agents.core.models import SkillResult


class RedisCache:
    """
    Redis 缓存实现
    
    支持分布式部署，多实例共享缓存。
    """

    def __init__(self, redis_url: str, key_prefix: str = "automage:"):
        """
        初始化 Redis 缓存
        
        Args:
            redis_url: Redis 连接 URL (redis://host:port/db)
            key_prefix: 键前缀
        """
        try:
            import redis
            self._redis = redis.from_url(redis_url, decode_responses=True)
            self.key_prefix = key_prefix
            self._available = True
        except ImportError:
            print("⚠️  Redis not installed. Install with: pip install redis")
            self._redis = None
            self._available = False
        except Exception as exc:
            print(f"⚠️  Failed to connect to Redis: {exc}")
            self._redis = None
            self._available = False

    def is_available(self) -> bool:
        """检查 Redis 是否可用"""
        return self._available and self._redis is not None

    def _make_key(self, key: str) -> str:
        """生成完整的键名"""
        return f"{self.key_prefix}{key}"

    def get(self, key: str) -> Any | None:
        """
        获取缓存值
        
        Args:
            key: 缓存键
        
        Returns:
            Any: 缓存值，不存在返回 None
        """
        if not self.is_available():
            return None

        try:
            value = self._redis.get(self._make_key(key))
            if value is None:
                return None
            return json.loads(value)
        except Exception as exc:
            print(f"⚠️  Redis get error: {exc}")
            return None

    def set(self, key: str, value: Any, ttl_seconds: int = 300) -> bool:
        """
        设置缓存值
        
        Args:
            key: 缓存键
            value: 缓存值
            ttl_seconds: 过期时间（秒）
        
        Returns:
            bool: 是否成功
        """
        if not self.is_available():
            return False

        try:
            serialized = json.dumps(value, ensure_ascii=False)
            self._redis.setex(self._make_key(key), ttl_seconds, serialized)
            return True
        except Exception as exc:
            print(f"⚠️  Redis set error: {exc}")
            return False

    def delete(self, key: str) -> bool:
        """
        删除缓存值
        
        Args:
            key: 缓存键
        
        Returns:
            bool: 是否成功
        """
        if not self.is_available():
            return False

        try:
            self._redis.delete(self._make_key(key))
            return True
        except Exception as exc:
            print(f"⚠️  Redis delete error: {exc}")
            return False

    def clear_pattern(self, pattern: str) -> int:
        """
        删除匹配模式的所有键
        
        Args:
            pattern: 键模式（支持通配符 *）
        
        Returns:
            int: 删除的键数量
        """
        if not self.is_available():
            return 0

        try:
            full_pattern = self._make_key(pattern)
            keys = self._redis.keys(full_pattern)
            if keys:
                return self._redis.delete(*keys)
            return 0
        except Exception as exc:
            print(f"⚠️  Redis clear_pattern error: {exc}")
            return 0

    def exists(self, key: str) -> bool:
        """
        检查键是否存在
        
        Args:
            key: 缓存键
        
        Returns:
            bool: 是否存在
        """
        if not self.is_available():
            return False

        try:
            return self._redis.exists(self._make_key(key)) > 0
        except Exception as exc:
            print(f"⚠️  Redis exists error: {exc}")
            return False

    def get_ttl(self, key: str) -> int:
        """
        获取键的剩余过期时间
        
        Args:
            key: 缓存键
        
        Returns:
            int: 剩余秒数，-1 表示永不过期，-2 表示不存在
        """
        if not self.is_available():
            return -2

        try:
            return self._redis.ttl(self._make_key(key))
        except Exception as exc:
            print(f"⚠️  Redis get_ttl error: {exc}")
            return -2


class RedisSkillResultCache:
    """
    基于 Redis 的 Skill 结果缓存
    
    支持分布式部署。
    """

    def __init__(self, redis_url: str, ttl_seconds: int = 60):
        """
        初始化 Redis Skill 缓存
        
        Args:
            redis_url: Redis 连接 URL
            ttl_seconds: 默认过期时间
        """
        self._cache = RedisCache(redis_url, key_prefix="automage:skill:")
        self.ttl_seconds = ttl_seconds

        # 可缓存的 Skill 列表
        self._cacheable_skills = {
            "fetch_my_tasks",
            "read_staff_daily_report",
            "search_feishu_knowledge",
            "analyze_team_reports",
        }

    def is_available(self) -> bool:
        """检查 Redis 是否可用"""
        return self._cache.is_available()

    def get_cache_key(self, skill_name: str, actor_user_id: str, payload: dict[str, Any]) -> str:
        """生成缓存键"""
        payload_str = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        key_str = f"{skill_name}:{actor_user_id}:{payload_str}"
        return hashlib.md5(key_str.encode()).hexdigest()

    def is_cacheable(self, skill_name: str) -> bool:
        """判断 Skill 是否可缓存"""
        return skill_name in self._cacheable_skills

    def get(self, skill_name: str, actor_user_id: str, payload: dict[str, Any]) -> SkillResult | None:
        """获取缓存的 Skill 结果"""
        if not self.is_cacheable(skill_name) or not self.is_available():
            return None

        cache_key = self.get_cache_key(skill_name, actor_user_id, payload)
        cached_data = self._cache.get(cache_key)

        if cached_data is None:
            return None

        # 反序列化为 SkillResult
        return SkillResult(
            ok=cached_data.get("ok", False),
            data=cached_data.get("data"),
            message=cached_data.get("message", ""),
            error_code=cached_data.get("error_code"),
        )

    def set(
        self,
        skill_name: str,
        actor_user_id: str,
        payload: dict[str, Any],
        result: SkillResult,
        ttl_seconds: int | None = None,
    ) -> bool:
        """缓存 Skill 结果"""
        if not self.is_cacheable(skill_name) or not result.ok or not self.is_available():
            return False

        cache_key = self.get_cache_key(skill_name, actor_user_id, payload)
        ttl = ttl_seconds if ttl_seconds is not None else self.ttl_seconds

        # 序列化 SkillResult
        cached_data = {
            "ok": result.ok,
            "data": result.data,
            "message": result.message,
            "error_code": result.error_code,
        }

        return self._cache.set(cache_key, cached_data, ttl)

    def invalidate(self, skill_name: str, actor_user_id: str) -> int:
        """使指定用户的 Skill 缓存失效"""
        if not self.is_available():
            return 0

        # 删除匹配的键
        pattern = f"{skill_name}:{actor_user_id}:*"
        return self._cache.clear_pattern(pattern)

    def clear(self) -> int:
        """清空所有 Skill 缓存"""
        if not self.is_available():
            return 0

        return self._cache.clear_pattern("*")


# 全局 Redis 缓存实例
_redis_skill_cache: RedisSkillResultCache | None = None


def get_redis_skill_cache(redis_url: str, ttl_seconds: int = 60) -> RedisSkillResultCache:
    """
    获取 Redis Skill 缓存实例（单例）
    
    Args:
        redis_url: Redis 连接 URL
        ttl_seconds: 默认过期时间
    
    Returns:
        RedisSkillResultCache: 缓存实例
    """
    global _redis_skill_cache
    if _redis_skill_cache is None:
        _redis_skill_cache = RedisSkillResultCache(redis_url, ttl_seconds)
    return _redis_skill_cache
