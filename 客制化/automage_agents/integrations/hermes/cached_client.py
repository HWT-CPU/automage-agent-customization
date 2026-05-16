"""
带缓存的 Hermes Client - 优化频繁调用的只读 Skill

优化点：
1. 自动缓存只读 Skill 结果
2. 智能缓存失效
3. 性能监控
"""

from __future__ import annotations

import time
from typing import Any

from automage_agents.api.cache import skill_result_cache
from automage_agents.integrations.hermes.client import LocalHermesClient
from automage_agents.integrations.hermes.contracts import HermesInvokeRequest, HermesInvokeResponse
from automage_agents.skills.context import SkillContext


class CachedHermesClient:
    """
    带缓存的 Hermes Client
    
    自动缓存只读 Skill 的结果，提升性能。
    """

    def __init__(
        self,
        staff_context: SkillContext,
        manager_context: SkillContext,
        executive_context: SkillContext,
        enable_cache: bool = True,
        cache_ttl_seconds: int = 60,
    ):
        self._inner_client = LocalHermesClient(
            staff_context, manager_context, executive_context
        )
        self.enable_cache = enable_cache
        self.cache_ttl_seconds = cache_ttl_seconds
        
        # 性能统计
        self._stats = {
            "total_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "total_duration_ms": 0.0,
        }

    def invoke_skill(self, request: HermesInvokeRequest) -> HermesInvokeResponse:
        """
        调用 Skill（带缓存）
        
        Args:
            request: Hermes 请求
        
        Returns:
            HermesInvokeResponse: 响应
        """
        self._stats["total_requests"] += 1
        start_time = time.time()

        # 尝试从缓存获取
        if self.enable_cache:
            cached_result = skill_result_cache.get(
                request.skill_name,
                request.actor_user_id,
                request.payload,
            )
            
            if cached_result is not None:
                self._stats["cache_hits"] += 1
                duration_ms = (time.time() - start_time) * 1000
                self._stats["total_duration_ms"] += duration_ms
                
                # 返回缓存的结果
                return HermesInvokeResponse(
                    ok=cached_result.ok,
                    skill_name=request.skill_name,
                    actor_user_id=request.actor_user_id,
                    result=cached_result,
                    trace=request.trace,
                )

        # 缓存未命中，调用实际的 Skill
        self._stats["cache_misses"] += 1
        response = self._inner_client.invoke_skill(request)
        
        duration_ms = (time.time() - start_time) * 1000
        self._stats["total_duration_ms"] += duration_ms

        # 缓存结果（如果适用）
        if self.enable_cache and response.ok:
            skill_result_cache.set(
                request.skill_name,
                request.actor_user_id,
                request.payload,
                response.result,
                self.cache_ttl_seconds,
            )

        return response

    def invalidate_cache(self, skill_name: str | None = None, actor_user_id: str | None = None) -> None:
        """
        使缓存失效
        
        Args:
            skill_name: Skill 名称（可选）
            actor_user_id: 用户 ID（可选）
        """
        if skill_name and actor_user_id:
            skill_result_cache.invalidate(skill_name, actor_user_id)
        else:
            skill_result_cache.clear()

    def get_stats(self) -> dict[str, Any]:
        """
        获取性能统计
        
        Returns:
            dict: 统计信息
        """
        total_requests = self._stats["total_requests"]
        cache_hits = self._stats["cache_hits"]
        
        return {
            "total_requests": total_requests,
            "cache_hits": cache_hits,
            "cache_misses": self._stats["cache_misses"],
            "cache_hit_rate": cache_hits / total_requests if total_requests > 0 else 0.0,
            "avg_duration_ms": (
                self._stats["total_duration_ms"] / total_requests
                if total_requests > 0
                else 0.0
            ),
        }

    def reset_stats(self) -> None:
        """重置统计信息"""
        self._stats = {
            "total_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "total_duration_ms": 0.0,
        }
