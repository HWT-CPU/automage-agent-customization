"""
缓存层 - 优化频繁调用的 Skill 和数据查询

优化点：
1. Skill 结果缓存（可选）
2. 用户配置缓存
3. 减少重复的数据库查询
"""

from __future__ import annotations

import hashlib
import json
import time
from typing import Any, Callable, TypeVar

from automage_agents.core.models import SkillResult

T = TypeVar("T")


class SimpleCache:
    """简单的内存缓存实现"""

    def __init__(self, ttl_seconds: int = 300):
        self._cache: dict[str, tuple[Any, float]] = {}
        self.ttl_seconds = ttl_seconds

    def get(self, key: str) -> Any | None:
        """获取缓存值"""
        if key not in self._cache:
            return None

        value, expire_at = self._cache[key]
        if time.time() > expire_at:
            del self._cache[key]
            return None

        return value

    def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> None:
        """设置缓存值"""
        ttl = ttl_seconds if ttl_seconds is not None else self.ttl_seconds
        expire_at = time.time() + ttl
        self._cache[key] = (value, expire_at)

    def delete(self, key: str) -> None:
        """删除缓存值"""
        self._cache.pop(key, None)

    def clear(self) -> None:
        """清空所有缓存"""
        self._cache.clear()

    def size(self) -> int:
        """获取缓存大小"""
        return len(self._cache)


class SkillResultCache:
    """Skill 结果缓存 - 用于缓存幂等的只读 Skill"""

    def __init__(self, ttl_seconds: int = 60):
        self._cache = SimpleCache(ttl_seconds)
        # 可缓存的 Skill 列表（只读操作）
        self._cacheable_skills = {
            "fetch_my_tasks",
            "read_staff_daily_report",
            "search_feishu_knowledge",
            "analyze_team_reports",
        }

    def get_cache_key(self, skill_name: str, actor_user_id: str, payload: dict[str, Any]) -> str:
        """生成缓存键"""
        # 将 payload 序列化为稳定的字符串
        payload_str = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        key_str = f"{skill_name}:{actor_user_id}:{payload_str}"
        return hashlib.md5(key_str.encode()).hexdigest()

    def is_cacheable(self, skill_name: str) -> bool:
        """判断 Skill 是否可缓存"""
        return skill_name in self._cacheable_skills

    def get(self, skill_name: str, actor_user_id: str, payload: dict[str, Any]) -> SkillResult | None:
        """获取缓存的 Skill 结果"""
        if not self.is_cacheable(skill_name):
            return None

        cache_key = self.get_cache_key(skill_name, actor_user_id, payload)
        return self._cache.get(cache_key)

    def set(
        self,
        skill_name: str,
        actor_user_id: str,
        payload: dict[str, Any],
        result: SkillResult,
        ttl_seconds: int | None = None,
    ) -> None:
        """缓存 Skill 结果"""
        if not self.is_cacheable(skill_name) or not result.ok:
            return

        cache_key = self.get_cache_key(skill_name, actor_user_id, payload)
        self._cache.set(cache_key, result, ttl_seconds)

    def invalidate(self, skill_name: str, actor_user_id: str) -> None:
        """使指定用户的 Skill 缓存失效"""
        # 简单实现：清空所有缓存
        # 生产环境可以使用更精细的失效策略
        self._cache.clear()

    def clear(self) -> None:
        """清空所有缓存"""
        self._cache.clear()


def cached(ttl_seconds: int = 60):
    """
    缓存装饰器 - 用于缓存函数结果
    
    使用示例:
    ```python
    @cached(ttl_seconds=300)
    def expensive_operation(param: str) -> dict:
        # 耗时操作
        return result
    ```
    """
    cache = SimpleCache(ttl_seconds)

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        def wrapper(*args, **kwargs) -> T:
            # 生成缓存键
            cache_key = f"{func.__name__}:{args}:{kwargs}"
            cache_key_hash = hashlib.md5(cache_key.encode()).hexdigest()

            # 尝试从缓存获取
            cached_result = cache.get(cache_key_hash)
            if cached_result is not None:
                return cached_result

            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            cache.set(cache_key_hash, result)
            return result

        return wrapper

    return decorator


# 全局缓存实例
skill_result_cache = SkillResultCache(ttl_seconds=60)
