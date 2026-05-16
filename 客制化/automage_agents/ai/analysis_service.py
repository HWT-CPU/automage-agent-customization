"""
AI Analysis Service - 使用 LLM 进行真实的业务分析

提供以下能力：
1. 分析团队日报，提取关键信息和风险
2. 生成 Manager 汇总报告
3. 生成 Executive 决策方案（A/B 方案）
"""

from __future__ import annotations

import json
from typing import Any

from automage_agents.ai.llm_client import LLMClient, LLMMessage, get_llm_client


class AnalysisService:
    """AI 分析服务"""
    
    def __init__(self, llm_client: LLMClient | None = None):
        self.llm = llm_client or get_llm_client()
    
    def analyze_team_reports(
        self,
        reports: list[dict[str, Any]],
        department: str,
        date: str,
        knowledge_context: str = "",
    ) -> dict[str, Any]:
        """
        分析团队日报，生成结构化洞察
        
        返回：
        {
            "overall_health": "green|yellow|red",
            "aggregated_summary": "综合汇总文本",
            "top_3_risks": [{"risk_title": "...", "description": "...", "severity": "...", "suggested_action": "..."}],
            "escalation_required": true|false,
            "key_achievements": ["..."],
            "blocked_items": ["..."],
        }
        """
        # 构建分析 prompt
        system_prompt = self._build_analysis_system_prompt(knowledge_context)
        user_prompt = self._build_analysis_user_prompt(reports, department, date)
        
        # 调用 LLM
        messages = [
            LLMMessage(role="system", content=system_prompt),
            LLMMessage(role="user", content=user_prompt),
        ]
        
        response = self.llm.chat(messages, temperature=0.3)
        
        # 解析响应
        return self._parse_analysis_response(response.content)
    
    def generate_manager_summary(
        self,
        analysis: dict[str, Any],
        department: str,
        date: str,
        knowledge_context: str = "",
    ) -> str:
        """
        基于分析结果生成 Manager 汇总文本
        """
        system_prompt = "你是一位经验丰富的部门经理，擅长撰写简洁、专业的工作汇总报告。"
        
        if knowledge_context:
            system_prompt += f"\n\n参考知识库：\n{knowledge_context[:1000]}"
        
        user_prompt = f"""请基于以下分析结果，生成一份部门工作汇总报告：

部门：{department}
日期：{date}

分析结果：
{json.dumps(analysis, ensure_ascii=False, indent=2)}

要求：
1. 语言简洁专业，突出重点
2. 先总结整体进展，再说明风险和问题
3. 给出明确的下一步建议
4. 字数控制在 200-300 字
"""
        
        messages = [
            LLMMessage(role="system", content=system_prompt),
            LLMMessage(role="user", content=user_prompt),
        ]
        
        response = self.llm.chat(messages, temperature=0.5)
        return response.content.strip()
    
    def generate_decision_options(
        self,
        manager_summary: dict[str, Any],
        department: str,
        date: str,
        knowledge_context: str = "",
    ) -> dict[str, Any]:
        """
        基于 Manager 汇总生成 A/B 决策方案
        
        返回：
        {
            "option_a": {
                "title": "方案标题",
                "strategy": "策略说明",
                "tasks": ["任务1", "任务2"],
                "priority": "high|medium|low",
            },
            "option_b": {...},
            "recommendation": "推荐说明",
        }
        """
        system_prompt = self._build_decision_system_prompt(knowledge_context)
        user_prompt = self._build_decision_user_prompt(manager_summary, department, date)
        
        messages = [
            LLMMessage(role="system", content=system_prompt),
            LLMMessage(role="user", content=user_prompt),
        ]
        
        response = self.llm.chat(messages, temperature=0.7)
        
        return self._parse_decision_response(response.content, manager_summary)
    
    def _build_analysis_system_prompt(self, knowledge_context: str) -> str:
        prompt = """你是 AutoMage 企业工作流平台的核心智能体「墨智」，负责分析团队日报并提取关键信息。

你的任务：
1. 理解每份日报的进展、问题、风险
2. 提取结构化洞察
3. 判断整体健康度（green/yellow/red）
4. 识别 top 3 风险
5. 判断是否需要上报给 Executive

评估标准：
- Green: 进展顺利，无重大风险
- Yellow: 存在中等风险或阻塞，需要关注
- Red: 存在高风险或严重阻塞，需要立即处理

输出格式（JSON）：
{
  "overall_health": "green|yellow|red",
  "aggregated_summary": "综合汇总文本（200字以内）",
  "top_3_risks": [
    {
      "risk_title": "风险标题",
      "description": "风险描述",
      "severity": "low|medium|high",
      "suggested_action": "建议行动"
    }
  ],
  "escalation_required": true|false,
  "key_achievements": ["关键成果1", "关键成果2"],
  "blocked_items": ["阻塞项1", "阻塞项2"]
}
"""
        
        if knowledge_context:
            prompt += f"\n\n参考知识库（用于理解业务背景）：\n{knowledge_context[:1500]}"
        
        return prompt
    
    def _build_analysis_user_prompt(
        self,
        reports: list[dict[str, Any]],
        department: str,
        date: str,
    ) -> str:
        # 提取日报关键信息
        reports_text = []
        for i, report in enumerate(reports, 1):
            user_id = report.get("user_id", "unknown")
            work_progress = report.get("work_progress", "")
            issues_faced = report.get("issues_faced", "")
            next_day_plan = report.get("next_day_plan", "")
            
            reports_text.append(f"""
日报 {i} - 员工 {user_id}：
工作进展：{work_progress}
遇到问题：{issues_faced}
明日计划：{next_day_plan}
""")
        
        return f"""请分析以下团队日报：

部门：{department}
日期：{date}
日报数量：{len(reports)}

{''.join(reports_text)}

请输出 JSON 格式的分析结果。"""
    
    def _build_decision_system_prompt(self, knowledge_context: str) -> str:
        prompt = """你是 AutoMage 企业工作流平台的决策智能体，负责为 Executive 生成 A/B 决策方案。

你的任务：
1. 基于 Manager 汇总的风险和问题，生成两个不同的决策方案
2. 方案 A：偏稳健/保守方向，优先解决确定性问题
3. 方案 B：偏进取/变革方向，优先抓住高价值机会
4. 每个方案包含：策略说明、执行任务、优先级

输出格式（JSON）：
{
  "option_a": {
    "title": "稳健方案标题（10字以内）",
    "strategy": "策略说明（100字以内）",
    "tasks": ["具体任务1", "具体任务2", "具体任务3"],
    "priority": "high|medium|low"
  },
  "option_b": {
    "title": "进取方案标题（10字以内）",
    "strategy": "策略说明（100字以内）",
    "tasks": ["具体任务1", "具体任务2", "具体任务3"],
    "priority": "high|medium|low"
  },
  "recommendation": "推荐说明（50字以内，说明两个方案的权衡）"
}
"""
        
        if knowledge_context:
            prompt += f"\n\n参考知识库（用于理解业务背景）：\n{knowledge_context[:1500]}"
        
        return prompt
    
    def _build_decision_user_prompt(
        self,
        manager_summary: dict[str, Any],
        department: str,
        date: str,
    ) -> str:
        overall_health = manager_summary.get("overall_health", "unknown")
        aggregated_summary = manager_summary.get("aggregated_summary", "")
        top_3_risks = manager_summary.get("top_3_risks", [])
        
        risks_text = []
        for i, risk in enumerate(top_3_risks[:3], 1):
            if isinstance(risk, dict):
                title = risk.get("risk_title", "")
                desc = risk.get("description", "")
                severity = risk.get("severity", "")
                risks_text.append(f"{i}. [{severity}] {title}: {desc}")
            elif isinstance(risk, str):
                risks_text.append(f"{i}. {risk}")
        
        return f"""请基于以下 Manager 汇总，生成 A/B 决策方案：

部门：{department}
日期：{date}
健康度：{overall_health}

汇总：
{aggregated_summary}

Top 3 风险：
{''.join(risks_text) if risks_text else '无'}

请输出 JSON 格式的决策方案。"""
    
    def _parse_analysis_response(self, content: str) -> dict[str, Any]:
        """解析 LLM 分析响应"""
        try:
            # 尝试提取 JSON
            json_start = content.find("{")
            json_end = content.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                return json.loads(json_str)
        except Exception:
            pass
        
        # 如果解析失败，返回默认结构
        return {
            "overall_health": "yellow",
            "aggregated_summary": content[:300],
            "top_3_risks": [],
            "escalation_required": False,
            "key_achievements": [],
            "blocked_items": [],
        }
    
    def _parse_decision_response(
        self,
        content: str,
        manager_summary: dict[str, Any],
    ) -> dict[str, Any]:
        """解析 LLM 决策响应"""
        try:
            # 尝试提取 JSON
            json_start = content.find("{")
            json_end = content.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                parsed = json.loads(json_str)
                
                # 转换为标准格式
                summary_id = manager_summary.get("summary_public_id", "pending")
                
                return {
                    "decision_options": [
                        {
                            "option_id": "A",
                            "title": parsed.get("option_a", {}).get("title", "稳健执行方案"),
                            "summary": parsed.get("option_a", {}).get("strategy", ""),
                            "task_candidates": [
                                {"title": task, "priority": parsed.get("option_a", {}).get("priority", "medium")}
                                for task in parsed.get("option_a", {}).get("tasks", [])
                            ],
                            "source_summary_id": summary_id,
                        },
                        {
                            "option_id": "B",
                            "title": parsed.get("option_b", {}).get("title", "进取执行方案"),
                            "summary": parsed.get("option_b", {}).get("strategy", ""),
                            "task_candidates": [
                                {"title": task, "priority": parsed.get("option_b", {}).get("priority", "medium")}
                                for task in parsed.get("option_b", {}).get("tasks", [])
                            ],
                            "source_summary_id": summary_id,
                        },
                    ],
                    "recommendation": parsed.get("recommendation", ""),
                }
        except Exception:
            pass
        
        # 如果解析失败，返回默认方案
        summary_id = manager_summary.get("summary_public_id", "pending")
        return {
            "decision_options": [
                {
                    "option_id": "A",
                    "title": "稳健执行方案",
                    "summary": "优先解决确定性问题，降低执行风险",
                    "task_candidates": [],
                    "source_summary_id": summary_id,
                },
                {
                    "option_id": "B",
                    "title": "进取执行方案",
                    "summary": "优先抓住高价值机会，加速资源投入",
                    "task_candidates": [],
                    "source_summary_id": summary_id,
                },
            ],
            "recommendation": content[:200],
        }


# 全局单例
_default_service: AnalysisService | None = None


def get_analysis_service() -> AnalysisService:
    """获取全局分析服务"""
    global _default_service
    if _default_service is None:
        _default_service = AnalysisService()
    return _default_service
