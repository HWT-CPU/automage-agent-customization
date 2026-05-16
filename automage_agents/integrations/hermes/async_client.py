"""
异步 Hermes Client - 支持并发执行多个 Skill

优化点：
1. 异步执行 Skill
2. 并发执行多个 Skill
3. 超时控制
4. 错误隔离
"""

from __future__ import annotations

import asyncio
from typing import Any

from automage_agents.core.models import SkillResult
from automage_agents.integrations.hermes.client import LocalHermesClient
from automage_agents.integrations.hermes.contracts import HermesInvokeRequest, HermesInvokeResponse
from automage_agents.skills.context import SkillContext


class AsyncHermesClient:
    """
    异步 Hermes Client
    
    支持并发执行多个 Skill，提升性能。
    """

    def __init__(
        self,
        staff_context: SkillContext,
        manager_context: SkillContext,
        executive_context: SkillContext,
        default_timeout_seconds: float = 30.0,
    ):
        self._sync_client = LocalHermesClient(
            staff_context, manager_context, executive_context
        )
        self.default_timeout_seconds = default_timeout_seconds

    async def invoke_skill_async(
        self,
        request: HermesInvokeRequest,
        timeout_seconds: float | None = None,
    ) -> HermesInvokeResponse:
        """
        异步调用单个 Skill
        
        Args:
            request: Hermes 请求
            timeout_seconds: 超时时间（秒），None 使用默认值
        
        Returns:
            HermesInvokeResponse: 响应
        """
        timeout = timeout_seconds if timeout_seconds is not None else self.default_timeout_seconds

        try:
            # 在线程池中执行同步 Skill
            response = await asyncio.wait_for(
                asyncio.to_thread(self._sync_client.invoke_skill, request),
                timeout=timeout,
            )
            return response

        except asyncio.TimeoutError:
            # 超时处理
            return HermesInvokeResponse(
                ok=False,
                skill_name=request.skill_name,
                actor_user_id=request.actor_user_id,
                result=SkillResult(
                    ok=False,
                    data={"timeout_seconds": timeout},
                    message=f"Skill execution timeout after {timeout}s",
                    error_code="timeout",
                ),
                trace=request.trace,
            )

        except Exception as exc:
            # 异常处理
            return HermesInvokeResponse(
                ok=False,
                skill_name=request.skill_name,
                actor_user_id=request.actor_user_id,
                result=SkillResult(
                    ok=False,
                    data={"error": str(exc)},
                    message=f"Skill execution failed: {exc}",
                    error_code="execution_error",
                ),
                trace=request.trace,
            )

    async def invoke_skills_concurrent(
        self,
        requests: list[HermesInvokeRequest],
        timeout_seconds: float | None = None,
        max_concurrency: int = 10,
    ) -> list[HermesInvokeResponse]:
        """
        并发执行多个 Skill
        
        Args:
            requests: Hermes 请求列表
            timeout_seconds: 每个 Skill 的超时时间
            max_concurrency: 最大并发数
        
        Returns:
            list[HermesInvokeResponse]: 响应列表（顺序与请求一致）
        """
        if not requests:
            return []

        # 使用信号量限制并发数
        semaphore = asyncio.Semaphore(max_concurrency)

        async def execute_with_semaphore(req: HermesInvokeRequest) -> HermesInvokeResponse:
            async with semaphore:
                return await self.invoke_skill_async(req, timeout_seconds)

        # 并发执行所有 Skill
        tasks = [execute_with_semaphore(req) for req in requests]
        responses = await asyncio.gather(*tasks, return_exceptions=False)

        return responses

    async def invoke_skills_batch(
        self,
        requests: list[HermesInvokeRequest],
        batch_size: int = 5,
        timeout_seconds: float | None = None,
    ) -> list[HermesInvokeResponse]:
        """
        分批执行多个 Skill
        
        Args:
            requests: Hermes 请求列表
            batch_size: 每批的大小
            timeout_seconds: 每个 Skill 的超时时间
        
        Returns:
            list[HermesInvokeResponse]: 响应列表
        """
        if not requests:
            return []

        responses = []

        # 分批执行
        for i in range(0, len(requests), batch_size):
            batch = requests[i : i + batch_size]
            batch_responses = await self.invoke_skills_concurrent(
                batch, timeout_seconds, max_concurrency=batch_size
            )
            responses.extend(batch_responses)

        return responses


def run_skills_concurrent(
    client: AsyncHermesClient,
    requests: list[HermesInvokeRequest],
    timeout_seconds: float | None = None,
) -> list[HermesInvokeResponse]:
    """
    同步接口：并发执行多个 Skill
    
    Args:
        client: 异步 Hermes Client
        requests: 请求列表
        timeout_seconds: 超时时间
    
    Returns:
        list[HermesInvokeResponse]: 响应列表
    """
    return asyncio.run(client.invoke_skills_concurrent(requests, timeout_seconds))
