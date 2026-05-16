from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from automage_agents.core.enums import AgentLevel, AgentRole


class IdentityPayload(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "node_id": "staff_agent_mvp_001",
                "user_id": "user_agent_001",
                "role": "staff",
                "level": "l1_staff",
                "department_id": "dept_mvp_core",
                "manager_node_id": "manager_agent_mvp_001",
                "metadata": {
                    "display_name": "张三",
                    "source": "swagger",
                },
            }
        },
    )

    node_id: str = Field(description="Agent 节点 ID")
    user_id: str = Field(description="业务用户 ID")
    role: AgentRole = Field(description="Agent 角色，例如 staff / manager / executive")
    level: AgentLevel = Field(description="Agent 层级，例如 l1_staff / l2_manager / l3_executive")
    department_id: str | None = Field(default=None, description="所属部门 ID")
    manager_node_id: str | None = Field(default=None, description="上级管理节点 ID")
    metadata: dict[str, Any] = Field(default_factory=dict, description="扩展元数据")


class AgentInitRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "identity": {
                    "node_id": "staff_agent_mvp_001",
                    "user_id": "user_agent_001",
                    "role": "staff",
                    "level": "l1_staff",
                    "department_id": "dept_mvp_core",
                    "manager_node_id": "manager_agent_mvp_001",
                    "metadata": {
                        "display_name": "张三",
                        "source": "swagger",
                    },
                }
            }
        }
    )

    identity: IdentityPayload = Field(description="待初始化的 Agent 身份信息")


class StaffReportRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "identity": {
                    "node_id": "staff_agent_mvp_001",
                    "user_id": "user_agent_001",
                    "role": "staff",
                    "level": "l1_staff",
                    "department_id": "dept_mvp_core",
                    "manager_node_id": "manager_agent_mvp_001",
                    "metadata": {
                        "display_name": "张三",
                        "source": "swagger",
                    },
                },
                "report": {
                    "schema_id": "schema_v1_staff",
                    "schema_version": "1.0.0",
                    "timestamp": "2026-05-06T15:00:00+08:00",
                    "org_id": "org_automage_mvp",
                    "department_id": "dept_mvp_core",
                    "user_id": "user_agent_001",
                    "node_id": "staff_agent_mvp_001",
                    "record_date": "2026-05-06",
                    "work_progress": "已完成本地 mock 流程联调。",
                    "issues_faced": [],
                    "need_support": False,
                    "next_day_plan": "继续补齐真实 API 联调。",
                    "risk_level": "medium",
                    "signature": {
                        "confirm_status": "confirmed",
                        "confirmed_by": "user_agent_001",
                    },
                },
            }
        }
    )

    identity: IdentityPayload = Field(description="提交日报的员工 Agent 身份信息")
    report: dict[str, Any] = Field(description="员工日报内容")

    @model_validator(mode="after")
    def validate_staff_report(self) -> "StaffReportRequest":
        required = ["org_id", "department_id", "record_date", "work_progress", "risk_level"]
        missing = [field for field in required if self.report.get(field) in (None, "")]
        if missing:
            raise ValueError(f"Missing required report fields: {', '.join(missing)}")
        risk_level = str(self.report.get("risk_level")).lower()
        if risk_level not in {"low", "medium", "high", "critical"}:
            raise ValueError("risk_level must be one of: low, medium, high, critical")
        return self


class ManagerReportRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "identity": {
                    "node_id": "manager_agent_mvp_001",
                    "user_id": "user_manager_001",
                    "role": "manager",
                    "level": "l2_manager",
                    "department_id": "dept_mvp_core",
                    "manager_node_id": "executive_agent_boss_001",
                    "metadata": {
                        "display_name": "李经理",
                        "source": "swagger",
                    },
                },
                "report": {
                    "schema_id": "schema_v1_manager",
                    "schema_version": "1.0.0",
                    "timestamp": "2026-05-06T18:00:00+08:00",
                    "org_id": "org_automage_mvp",
                    "dept_id": "dept_mvp_core",
                    "manager_user_id": "user_manager_001",
                    "manager_node_id": "manager_agent_mvp_001",
                    "summary_date": "2026-05-06",
                    "staff_report_count": 2,
                    "missing_report_count": 0,
                    "overall_health": "yellow",
                    "aggregated_summary": "当前主链路已能跑通 mock 闭环，真实 API 仍需继续联调。",
                    "top_3_risks": [
                        "真实 API 端到端联调尚未完成",
                        "任务查询口径仍需统一",
                        "部分落表规则待最终冻结",
                    ],
                    "pending_approvals": 1,
                    "source_record_ids": [
                        "WR-20260506-STAFF-NORMAL-001",
                        "WR-20260506-STAFF-HIGHRISK-001",
                    ],
                    "signature": {
                        "confirm_status": "confirmed",
                        "confirmed_by": "user_manager_001",
                    },
                },
            }
        }
    )

    identity: IdentityPayload = Field(description="提交汇总的经理 Agent 身份信息")
    report: dict[str, Any] = Field(description="经理汇总内容")

    @model_validator(mode="after")
    def validate_manager_report(self) -> "ManagerReportRequest":
        required = ["org_id", "dept_id", "summary_date", "aggregated_summary"]
        missing = [field for field in required if self.report.get(field) in (None, "")]
        if missing:
            raise ValueError(f"Missing required report fields: {', '.join(missing)}")
        overall_health = str(self.report.get("overall_health") or "").lower()
        if overall_health and overall_health not in {"green", "yellow", "red"}:
            raise ValueError("overall_health must be one of: green, yellow, red")
        return self


class BetaApplicationCreateRequest(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        json_schema_extra={
            "example": {
                "name": "熊锦文",
                "company_name": "AutoMage",
                "contact": "13800138000",
                "team_size": "11-50人",
                "source": "landing_page",
                "notes": "希望申请第一批内测名额。",
            }
        },
    )

    name: str = Field(description="申请人姓名")
    company_name: str | None = Field(default=None, description="公司名称")
    company: str | None = Field(default=None, description="公司名称别名字段")
    contact: str | None = Field(default=None, description="手机号或微信")
    phone_or_wechat: str | None = Field(default=None, description="手机号或微信别名字段")
    mobile_or_wechat: str | None = Field(default=None, description="手机号或微信别名字段")
    phone: str | None = Field(default=None, description="手机号别名字段")
    wechat: str | None = Field(default=None, description="微信别名字段")
    team_size: str | int | None = Field(default=None, description="团队人数")
    team_members: str | int | None = Field(default=None, description="团队人数别名字段")
    source: str | None = Field(default="landing_page", description="来源")
    notes: str | None = Field(default=None, description="备注")
    meta: dict[str, Any] = Field(default_factory=dict, description="附加元数据")

    @model_validator(mode="after")
    def validate_beta_application(self) -> "BetaApplicationCreateRequest":
        if not str(self.name).strip():
            raise ValueError("name is required")
        company_name = self.company_name or self.company
        if not str(company_name or "").strip():
            raise ValueError("company_name is required")
        contact = self.contact or self.phone_or_wechat or self.mobile_or_wechat or self.phone or self.wechat
        if not str(contact or "").strip():
            raise ValueError("contact is required")
        team_size = self.team_size if self.team_size is not None else self.team_members
        if team_size in (None, ""):
            raise ValueError("team_size is required")
        return self


class DecisionCommitRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "identity": {
                    "node_id": "executive_agent_boss_001",
                    "user_id": "user_executive_001",
                    "role": "executive",
                    "level": "l3_executive",
                    "department_id": "dept_mvp_core",
                    "manager_node_id": None,
                    "metadata": {
                        "display_name": "陈总",
                        "source": "swagger",
                    },
                },
                "decision": {
                    "selected_option_id": "A",
                    "decision_summary": "优先完成 Staff、Manager、Task 三条最小真实链路。",
                    "task_candidates": [
                        {
                            "task_id": "TASK-20260507-BACKEND-001",
                            "assignee_user_id": "user_backend_001",
                            "assignee_node_id": "staff_agent_backend_001",
                            "manager_user_id": "user_manager_001",
                            "manager_node_id": "manager_agent_mvp_001",
                            "department_id": "dept_mvp_core",
                            "title": "补齐后端联调任务说明",
                            "description": "整理真实接口请求体、响应体和错误码。",
                            "status": "pending",
                        }
                    ],
                },
            }
        }
    )

    identity: IdentityPayload = Field(description="提交决策的高层 Agent 身份信息")
    decision: dict[str, Any] = Field(description="正式决策内容与待下发任务")

    @model_validator(mode="after")
    def validate_decision_payload(self) -> "DecisionCommitRequest":
        if not self.decision.get("decision_summary") and not self.decision.get("description"):
            raise ValueError("decision_summary or description is required")
        task_candidates = self.decision.get("task_candidates") or []
        if not isinstance(task_candidates, list):
            raise ValueError("task_candidates must be a list when provided")
        return self


class DreamRunRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "summary_id": "MSUM-20260506-NEED-EXEC-001"
            }
        }
    )

    summary_id: str = Field(description="经理汇总或待决策摘要 ID")


class TaskCreateRequest(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        json_schema_extra={
            "example": {
                "schema_id": "mock_v1_generated_tasks",
                "schema_version": "1.0.0",
                "generated_at": "2026-05-06T21:45:00+08:00",
                "org_id": "org_automage_mvp",
                "source_decision_id": "DEC-20260506-001",
                "tasks": [
                    {
                        "schema_id": "schema_v1_task",
                        "schema_version": "1.0.0",
                        "task_id": "TASK-20260507-BACKEND-001",
                        "org_id": "org_automage_mvp",
                        "department_id": "dept_mvp_core",
                        "task_title": "提供最小 API 联调样例",
                        "task_description": "覆盖 Staff 写入、Staff 列表读取、Task 查询三个接口。",
                        "source_type": "executive_decision",
                        "source_id": "DEC-20260506-001",
                        "source_summary_id": "MSUM-20260506-NEED-EXEC-001",
                        "creator_user_id": "user_executive_001",
                        "created_by_node_id": "executive_agent_boss_001",
                        "manager_user_id": "user_manager_001",
                        "manager_node_id": "manager_agent_mvp_001",
                        "assignee_user_id": "user_backend_001",
                        "assignee_node_id": "staff_agent_backend_001",
                        "priority": "critical",
                        "status": "pending",
                        "confirm_required": False,
                    }
                ],
            }
        },
    )

    tasks: list[dict[str, Any]] = Field(description="待创建的正式任务数组")

    @model_validator(mode="after")
    def validate_tasks(self) -> "TaskCreateRequest":
        if not self.tasks:
            raise ValueError("tasks must not be empty")
        for index, task in enumerate(self.tasks, start=1):
            required = [
                "task_id",
                "org_id",
                "department_id",
                "task_title",
                "task_description",
                "creator_user_id",
                "manager_user_id",
                "assignee_user_id",
                "status",
            ]
            missing = [field for field in required if task.get(field) in (None, "")]
            if missing:
                raise ValueError(f"Task #{index} missing required fields: {', '.join(missing)}")
            status = str(task.get("status")).lower()
            if status not in {"pending", "not_started", "in_progress", "doing", "done", "completed", "closed"}:
                raise ValueError(f"Task #{index} has unsupported status: {task.get('status')}")
            priority = str(task.get("priority") or "medium").lower()
            if priority not in {"critical", "high", "medium", "normal", "low"}:
                raise ValueError(f"Task #{index} has unsupported priority: {task.get('priority')}")
        return self


class TaskUpdateRequest(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        json_schema_extra={
            "example": {
                "status": "in_progress",
                "title": "提供最小 API 联调样例（处理中）",
                "description": "先完成后端 Swagger 示例和权限说明同步。",
            }
        },
    )

    status: Literal["pending", "not_started", "in_progress", "doing", "done", "completed", "closed"] | None = Field(
        default=None, description="任务状态"
    )
    title: str | None = Field(default=None, description="任务标题")
    description: str | None = Field(default=None, description="任务说明")
    task_payload: dict[str, Any] | None = Field(default=None, description="附加任务载荷")

    @model_validator(mode="after")
    def validate_mutation(self) -> "TaskUpdateRequest":
        if self.status is None and self.title is None and self.description is None and self.task_payload is None:
            raise ValueError("At least one field must be provided to update the task")
        return self


class ApiEnvelope(BaseModel):
    code: int | str = Field(default=200, description="业务状态码")
    data: dict[str, Any] | list[Any] | None = Field(default=None, description="返回数据")
    msg: str = Field(default="ok", description="返回消息")


class ApiConflictErrorDetail(BaseModel):
    error_type: Literal["conflict"] = Field(default="conflict", description="错误类型，固定为 conflict")
    error_code: str = Field(description="稳定错误码，便于前端按场景处理")
    message: str = Field(description="面向调用方的中文错误说明")
    conflict_target: str = Field(description="冲突对象或幂等判定口径")
    request_id: str | None = Field(default=None, description="本次请求的 request_id，便于排查")


class ApiConflictEnvelope(BaseModel):
    code: int = Field(default=409, description="业务状态码，冲突场景固定为 409")
    data: None = Field(default=None, description="冲突场景下固定为空")
    msg: str = Field(default="请求冲突", description="返回消息")
    error: ApiConflictErrorDetail = Field(description="冲突错误详情")


class CrudWriteRequest(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        json_schema_extra={
            "example": {
                "data": {
                    "public_id": "TASK-20260507-BACKEND-001",
                    "org_id": "org_automage_mvp",
                    "department_id": "dept_mvp_core",
                    "creator_user_id": "user_executive_001",
                    "title": "提供最小 API 联调样例",
                    "description": "覆盖 Staff 写入、Staff 列表读取、Task 查询三个接口。",
                    "status": "pending",
                    "priority": "critical",
                    "meta": {
                        "source_type": "executive_decision",
                        "manager_user_id": "user_manager_001",
                        "manager_node_id": "manager_agent_mvp_001",
                        "assignee_user_id": "user_backend_001",
                        "assignee_node_id": "staff_agent_backend_001",
                    },
                }
            }
        },
    )

    data: dict[str, Any] = Field(description="待写入或更新的字段数据")

