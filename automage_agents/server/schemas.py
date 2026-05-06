from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class IdentityPayload(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        json_schema_extra={
            "example": {
                "node_id": "staff-node-swagger-001",
                "user_id": "3",
                "role": "staff",
                "level": "l1_staff",
                "department_id": "1",
                "manager_node_id": "manager-node-swagger-001",
                "metadata": {
                    "display_name": "\u5f20\u4e09",
                    "source": "swagger",
                },
            }
        },
    )

    node_id: str = Field(description="Agent \u8282\u70b9 ID")
    user_id: str = Field(description="\u4e1a\u52a1\u7528\u6237 ID")
    role: str = Field(description="Agent \u89d2\u8272\uff0c\u4f8b\u5982 staff / manager / executive")
    level: str = Field(description="Agent \u5c42\u7ea7\uff0c\u4f8b\u5982 l1_staff / l2_manager / l3_executive")
    department_id: str | None = Field(default=None, description="\u6240\u5c5e\u90e8\u95e8 ID")
    manager_node_id: str | None = Field(default=None, description="\u4e0a\u7ea7 Agent \u8282\u70b9 ID")
    metadata: dict[str, Any] = Field(default_factory=dict, description="\u6269\u5c55\u5143\u6570\u636e")


class AgentInitRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "identity": {
                    "node_id": "staff-node-swagger-001",
                    "user_id": "3",
                    "role": "staff",
                    "level": "l1_staff",
                    "department_id": "1",
                    "manager_node_id": "manager-node-swagger-001",
                    "metadata": {
                        "display_name": "\u5f20\u4e09",
                        "source": "swagger",
                    },
                }
            }
        }
    )

    identity: IdentityPayload = Field(description="\u5f85\u521d\u59cb\u5316\u7684 Agent \u8eab\u4efd\u4fe1\u606f")


class StaffReportRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "identity": {
                    "node_id": "staff-node-swagger-001",
                    "user_id": "3",
                    "role": "staff",
                    "level": "l1_staff",
                    "department_id": "1",
                    "manager_node_id": "manager-node-swagger-001",
                    "metadata": {
                        "display_name": "\u5f20\u4e09",
                        "source": "swagger",
                    },
                },
                "report": {
                    "schema_id": "schema_v1_staff",
                    "timestamp": "2026-05-06T15:00:00+08:00",
                    "work_progress": "\u5b8c\u6210\u4e24\u4f4d\u91cd\u70b9\u5ba2\u6237\u56de\u8bbf\uff0c\u5e76\u66f4\u65b0\u62a5\u4ef7\u8bf4\u660e\u3002",
                    "issues_faced": "\u5ba2\u6237\u4ecd\u7136\u5173\u5fc3\u4ea4\u4ed8\u5468\u671f\u662f\u5426\u7a33\u5b9a\u3002",
                    "solution_attempt": "\u5df2\u6574\u7406\u4ea4\u4ed8\u95ee\u9898\u5e76\u540c\u6b65\u7ed9\u7ecf\u7406\u3002",
                    "need_support": True,
                    "next_day_plan": "\u7ee7\u7eed\u63a8\u8fdb\u62a5\u4ef7\u786e\u8ba4\u5e76\u8865\u5145\u98ce\u9669\u8bf4\u660e\u3002",
                    "resource_usage": {
                        "customer_calls": 5,
                        "quotes_prepared": 1,
                    },
                },
            }
        }
    )

    identity: IdentityPayload = Field(description="\u63d0\u4ea4\u65e5\u62a5\u7684\u5458\u5de5 Agent \u8eab\u4efd\u4fe1\u606f")
    report: dict[str, Any] = Field(description="\u5458\u5de5\u65e5\u62a5\u5185\u5bb9")


class ManagerReportRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "identity": {
                    "node_id": "manager-node-swagger-001",
                    "user_id": "2",
                    "role": "manager",
                    "level": "l2_manager",
                    "department_id": "1",
                    "manager_node_id": "executive-node-swagger-001",
                    "metadata": {
                        "display_name": "\u674e\u7ecf\u7406",
                        "source": "swagger",
                    },
                },
                "report": {
                    "schema_id": "schema_v1_manager",
                    "dept_id": "1",
                    "overall_health": "yellow",
                    "aggregated_summary": "\u9500\u552e\u90e8\u4eca\u65e5\u91cd\u70b9\u56f4\u7ed5\u5ba2\u6237\u56de\u8bbf\u3001\u7eed\u8d39\u63a8\u8fdb\u548c\u4ea4\u4ed8\u95ee\u9898\u6f84\u6e05\u5c55\u5f00\u3002",
                    "top_3_risks": [
                        "\u4ea4\u4ed8\u5468\u671f\u8bf4\u660e\u4e0d\u591f\u660e\u786e",
                        "\u4ef7\u683c\u5f02\u8bae\u4ecd\u9700\u7edf\u4e00\u53e3\u5f84",
                        "\u5173\u952e\u5ba2\u6237\u51b3\u7b56\u5468\u671f\u504f\u957f",
                    ],
                    "workforce_efficiency": 0.86,
                    "pending_approvals": 1,
                },
            }
        }
    )

    identity: IdentityPayload = Field(description="\u63d0\u4ea4\u7ecf\u7406\u65e5\u62a5\u7684 Agent \u8eab\u4efd\u4fe1\u606f")
    report: dict[str, Any] = Field(description="\u7ecf\u7406\u65e5\u62a5\u5185\u5bb9")


class DecisionCommitRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "identity": {
                    "node_id": "executive-node-swagger-001",
                    "user_id": "1",
                    "role": "executive",
                    "level": "l3_executive",
                    "department_id": "1",
                    "manager_node_id": None,
                    "metadata": {
                        "display_name": "\u9648\u603b",
                        "source": "swagger",
                    },
                },
                "decision": {
                    "selected_option_id": "A",
                    "decision_summary": "\u5148\u7edf\u4e00\u4ea4\u4ed8\u8bf4\u660e\uff0c\u518d\u63a8\u8fdb\u65b0\u7684\u5ba2\u6237\u627f\u8bfa\u3002",
                    "task_candidates": [
                        {
                            "assignee_user_id": "3",
                            "title": "\u8865\u5145\u91cd\u70b9\u5ba2\u6237\u4ea4\u4ed8\u8bf4\u660e",
                            "description": "\u628a\u4ea4\u4ed8\u5468\u671f\u3001\u4e0a\u7ebf\u524d\u63d0\u548c\u98ce\u9669\u63d0\u793a\u6574\u7406\u6210\u7edf\u4e00\u8bf4\u660e\u8bdd\u672f\u3002",
                            "status": "pending",
                        }
                    ],
                },
            }
        }
    )

    identity: IdentityPayload = Field(description="\u63d0\u4ea4\u51b3\u7b56\u7684\u9ad8\u5c42 Agent \u8eab\u4efd\u4fe1\u606f")
    decision: dict[str, Any] = Field(description="\u51b3\u7b56\u5185\u5bb9\u4e0e\u5f85\u4e0b\u53d1\u4efb\u52a1")


class ApiEnvelope(BaseModel):
    code: int | str = Field(default=200, description="\u4e1a\u52a1\u72b6\u6001\u7801")
    data: dict[str, Any] | list[Any] | None = Field(default=None, description="\u8fd4\u56de\u6570\u636e")
    msg: str = Field(default="ok", description="\u8fd4\u56de\u6d88\u606f")


class CrudWriteRequest(BaseModel):
    model_config = ConfigDict(
        extra="allow",
        json_schema_extra={
            "example": {
                "data": {
                    "task_id": "swagger-demo-task-001",
                    "assignee_user_id": "3",
                    "title": "Swagger \u65b0\u5efa\u6d4b\u8bd5\u4efb\u52a1",
                    "description": "\u7528\u4e8e\u9a8c\u8bc1\u901a\u7528 CRUD \u521b\u5efa\u80fd\u529b\u3002",
                    "status": "pending",
                    "task_payload": {
                        "source": "swagger-demo",
                        "priority": "medium",
                    },
                }
            }
        },
    )

    data: dict[str, Any] = Field(description="\u5f85\u5199\u5165\u6216\u66f4\u65b0\u7684\u5b57\u6bb5\u6570\u636e")
