"""
LLM Client - 统一的大语言模型客户端

支持多种 LLM 提供商：
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- 本地模型 (Ollama, vLLM)
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Literal

# 尝试导入 OpenAI，如果没有安装则使用 mock
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


@dataclass
class LLMConfig:
    """LLM 配置"""
    provider: Literal["openai", "anthropic", "ollama", "mock"] = "mock"
    model: str = "gpt-4"
    api_key: str | None = None
    api_base: str | None = None
    temperature: float = 0.7
    max_tokens: int = 2000
    timeout: int = 60


@dataclass
class LLMMessage:
    """LLM 消息"""
    role: Literal["system", "user", "assistant"]
    content: str


@dataclass
class LLMResponse:
    """LLM 响应"""
    content: str
    model: str
    usage: dict[str, int] | None = None
    finish_reason: str | None = None


class LLMClient:
    """统一的 LLM 客户端"""
    
    def __init__(self, config: LLMConfig | None = None):
        self.config = config or self._load_config_from_env()
        
    def _load_config_from_env(self) -> LLMConfig:
        """从环境变量加载配置"""
        return LLMConfig(
            provider=os.getenv("LLM_PROVIDER", "mock"),
            model=os.getenv("LLM_MODEL", "gpt-4"),
            api_key=os.getenv("LLM_API_KEY"),
            api_base=os.getenv("LLM_API_BASE"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("LLM_MAX_TOKENS", "2000")),
            timeout=int(os.getenv("LLM_TIMEOUT", "60")),
        )
    
    def chat(
        self,
        messages: list[LLMMessage],
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        """发送聊天请求"""
        if self.config.provider == "openai":
            return self._chat_openai(messages, temperature, max_tokens)
        elif self.config.provider == "anthropic":
            return self._chat_anthropic(messages, temperature, max_tokens)
        elif self.config.provider == "ollama":
            return self._chat_ollama(messages, temperature, max_tokens)
        else:
            return self._chat_mock(messages, temperature, max_tokens)
    
    def _chat_openai(
        self,
        messages: list[LLMMessage],
        temperature: float | None,
        max_tokens: int | None,
    ) -> LLMResponse:
        """OpenAI API 调用"""
        if not OPENAI_AVAILABLE:
            print("[WARNING] OpenAI library not installed. Falling back to mock mode.")
            print("[INFO] Install with: pip install openai")
            return self._chat_mock(messages, temperature, max_tokens)
        
        if not self.config.api_key:
            print("[WARNING] OpenAI API key not configured. Falling back to mock mode.")
            print("[INFO] Set LLM_API_KEY in .env file")
            return self._chat_mock(messages, temperature, max_tokens)
        
        try:
            client = openai.OpenAI(
                api_key=self.config.api_key,
                base_url=self.config.api_base,
                timeout=self.config.timeout,
            )
            
            response = client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": msg.role, "content": msg.content} for msg in messages],
                temperature=temperature or self.config.temperature,
                max_tokens=max_tokens or self.config.max_tokens,
            )
            
            choice = response.choices[0]
            return LLMResponse(
                content=choice.message.content or "",
                model=response.model,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0,
                },
                finish_reason=choice.finish_reason,
            )
        except Exception as exc:
            print(f"[ERROR] OpenAI API call failed: {exc}")
            print("[INFO] Falling back to mock mode")
            return self._chat_mock(messages, temperature, max_tokens)
    
    def _chat_anthropic(
        self,
        messages: list[LLMMessage],
        temperature: float | None,
        max_tokens: int | None,
    ) -> LLMResponse:
        """Anthropic Claude API 调用"""
        # TODO: 实现 Anthropic API 调用
        raise NotImplementedError("Anthropic provider not yet implemented")
    
    def _chat_ollama(
        self,
        messages: list[LLMMessage],
        temperature: float | None,
        max_tokens: int | None,
    ) -> LLMResponse:
        """Ollama 本地模型调用"""
        # TODO: 实现 Ollama API 调用
        raise NotImplementedError("Ollama provider not yet implemented")
    
    def _chat_mock(
        self,
        messages: list[LLMMessage],
        temperature: float | None,
        max_tokens: int | None,
    ) -> LLMResponse:
        """Mock 实现（用于测试）"""
        # 简单的规则based响应
        last_message = messages[-1].content if messages else ""
        
        if "分析" in last_message or "analyze" in last_message.lower():
            content = self._generate_mock_analysis(last_message)
        elif "决策" in last_message or "decision" in last_message.lower():
            content = self._generate_mock_decision(last_message)
        elif "汇总" in last_message or "summary" in last_message.lower():
            content = self._generate_mock_summary(last_message)
        else:
            content = "这是一个 Mock LLM 响应。请配置真实的 LLM API Key 以获得真实的 AI 分析。"
        
        return LLMResponse(
            content=content,
            model="mock-model",
            usage={"prompt_tokens": 100, "completion_tokens": 200, "total_tokens": 300},
            finish_reason="stop",
        )
    
    def _generate_mock_analysis(self, prompt: str) -> str:
        """生成 mock 分析结果"""
        return """基于日报数据的分析：

**整体评估**：
- 团队进展：良好，主要任务按计划推进
- 风险等级：中等，存在客户沟通和技术方案的不确定性
- 需要关注：客户报价周期疑虑可能影响合同签订

**关键发现**：
1. 客户跟进工作完成度高，但存在报价策略沟通障碍
2. 技术方案评审时间紧张，需要协调资源
3. 团队整体士气良好，执行力强

**建议行动**：
- 加强与客户的沟通，明确报价策略和交付周期
- 协调产品经理和技术团队，确保评审按时完成
- 持续跟进合同签订进度

注：这是 Mock 分析结果。配置真实 LLM 后将获得更深入的洞察。"""
    
    def _generate_mock_decision(self, prompt: str) -> str:
        """生成 mock 决策方案"""
        return """基于当前情况，提供两个决策方案：

**方案 A（稳健方案）**：
- 策略：优先解决客户疑虑，稳步推进
- 行动：
  1. 安排产品经理与客户深度沟通
  2. 准备详细的报价说明文档
  3. 技术方案评审延后一周，确保质量
- 优势：风险可控，客户满意度高
- 劣势：进度可能延后

**方案 B（进取方案）**：
- 策略：加速推进，并行处理多个事项
- 行动：
  1. 立即安排客户会议，现场解答疑虑
  2. 技术方案评审按原计划进行
  3. 合同签订和技术评审并行推进
- 优势：进度快，效率高
- 劣势：资源压力大，风险较高

注：这是 Mock 决策方案。配置真实 LLM 后将获得更智能的决策建议。"""
    
    def _generate_mock_summary(self, prompt: str) -> str:
        """生成 mock 汇总"""
        return """团队工作汇总：

**进展概况**：
团队整体进展良好，主要工作按计划推进。客户跟进和需求分析工作完成度高，项目推进顺利。

**风险提示**：
1. 客户对报价周期存在疑虑，可能影响合同签订进度
2. 技术方案评审时间紧张，需要协调资源确保按时完成

**下一步计划**：
继续推进合同签订，完成技术方案评审，加强与客户的沟通。

注：这是 Mock 汇总。配置真实 LLM 后将获得更全面的分析。"""


# 全局单例
_default_client: LLMClient | None = None


def get_llm_client() -> LLMClient:
    """获取全局 LLM 客户端"""
    global _default_client
    if _default_client is None:
        _default_client = LLMClient()
    return _default_client


def set_llm_client(client: LLMClient) -> None:
    """设置全局 LLM 客户端"""
    global _default_client
    _default_client = client
