from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException, Path, Query, Request, Response
from sqlalchemy.orm import Session

from automage_agents.config import load_runtime_settings
from automage_agents.server.audit import write_audit_log
from automage_agents.server.crud import (
    MODEL_REGISTRY,
    create_record,
    delete_record,
    get_record,
    list_records,
    update_record,
)
from automage_agents.server.daily_report_api import router as daily_report_router
from automage_agents.server.deps import get_db_session
from automage_agents.server.middleware import RequestTrackingMiddleware
from automage_agents.server.schemas import (
    AgentInitRequest,
    ApiEnvelope,
    CrudWriteRequest,
    DecisionCommitRequest,
    ManagerReportRequest,
    StaffReportRequest,
)
from automage_agents.server.service import (
    build_identity,
    commit_decision,
    create_agent_session,
    create_manager_report,
    create_staff_report,
    list_tasks,
)


HTTP_400_RESPONSE = {
    400: {
        "description": "请求参数或字段内容不符合要求",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Unknown or immutable fields: id",
                }
            }
        },
    }
}

HTTP_404_RESOURCE_RESPONSE = {
    404: {
        "description": "资源表不存在或记录不存在",
        "content": {
            "application/json": {
                "examples": {
                    "resource_not_found": {
                        "summary": "资源表不存在",
                        "value": {"detail": "resource not found"},
                    },
                    "record_not_found": {
                        "summary": "记录不存在",
                        "value": {"detail": "record not found"},
                    },
                }
            }
        },
    }
}

HTTP_404_RECORD_RESPONSE = {
    404: {
        "description": "记录不存在",
        "content": {
            "application/json": {
                "example": {
                    "detail": "record not found",
                }
            }
        },
    }
}

HTTP_422_RESPONSE = {
    422: {
        "description": "请求体验证失败",
        "content": {
            "application/json": {
                "example": {
                    "detail": [
                        {
                            "type": "missing",
                            "loc": ["body", "identity", "node_id"],
                            "msg": "Field required",
                            "input": {},
                        }
                    ]
                }
            }
        },
    }
}

HEALTH_RESPONSE = {
    200: {
        "description": "服务运行正常",
        "content": {
            "application/json": {
                "example": {
                    "status": "ok",
                }
            }
        },
    }
}

AGENT_INIT_RESPONSE = {
    200: {
        "description": "Agent 会话初始化成功",
        "content": {
            "application/json": {
                "example": {
                    "code": 200,
                    "data": {
                        "id": 4,
                        "auth_status": "active",
                        "identity": {
                            "node_id": "staff-node-swagger-001",
                            "user_id": "3",
                            "role": "staff",
                            "level": "l1_staff",
                            "department_id": "1",
                            "manager_node_id": "manager-node-swagger-001",
                            "metadata": {
                                "display_name": "张三",
                                "source": "swagger",
                            },
                        },
                    },
                    "msg": "agent initialized",
                }
            }
        },
    }
}

STAFF_REPORT_RESPONSE = {
    200: {
        "description": "员工日报快照保存成功",
        "content": {
            "application/json": {
                "example": {
                    "code": 200,
                    "data": {
                        "record": {
                            "id": 3,
                            "identity": {
                                "node_id": "staff-node-swagger-001",
                                "user_id": "3",
                                "role": "staff",
                                "level": "l1_staff",
                                "department_id": "1",
                                "manager_node_id": "manager-node-swagger-001",
                                "metadata": {
                                    "display_name": "张三",
                                    "source": "swagger",
                                },
                            },
                            "report": {
                                "schema_id": "schema_v1_staff",
                                "timestamp": "2026-05-06T15:00:00+08:00",
                                "work_progress": "完成两位重点客户回访，并更新报价说明。",
                                "issues_faced": "客户仍然关心交付周期是否稳定。",
                                "solution_attempt": "已整理交付问题并同步给经理。",
                                "need_support": True,
                                "next_day_plan": "继续推进报价确认并补充风险说明。",
                                "resource_usage": {
                                    "customer_calls": 5,
                                    "quotes_prepared": 1,
                                },
                            },
                        }
                    },
                    "msg": "staff report saved",
                }
            }
        },
    }
}

MANAGER_REPORT_RESPONSE = {
    200: {
        "description": "经理汇总快照保存成功",
        "content": {
            "application/json": {
                "example": {
                    "code": 200,
                    "data": {
                        "record": {
                            "id": 2,
                            "identity": {
                                "node_id": "manager-node-swagger-001",
                                "user_id": "2",
                                "role": "manager",
                                "level": "l2_manager",
                                "department_id": "1",
                                "manager_node_id": "executive-node-swagger-001",
                                "metadata": {
                                    "display_name": "李经理",
                                    "source": "swagger",
                                },
                            },
                            "report": {
                                "schema_id": "schema_v1_manager",
                                "dept_id": "1",
                                "overall_health": "yellow",
                                "aggregated_summary": "销售部今日重点围绕客户回访、续费推进和交付问题澄清展开。",
                                "top_3_risks": [
                                    "交付周期说明不够明确",
                                    "价格异议仍需统一口径",
                                    "关键客户决策周期偏长",
                                ],
                                "workforce_efficiency": 0.86,
                                "pending_approvals": 1,
                            },
                        }
                    },
                    "msg": "manager report saved",
                }
            }
        },
    }
}

DECISION_COMMIT_RESPONSE = {
    200: {
        "description": "决策提交成功，并可选自动生成任务",
        "content": {
            "application/json": {
                "example": {
                    "code": 200,
                    "data": {
                        "decision": {
                            "id": 2,
                            "identity": {
                                "node_id": "executive-node-swagger-001",
                                "user_id": "1",
                                "role": "executive",
                                "level": "l3_executive",
                                "department_id": "1",
                                "manager_node_id": None,
                                "metadata": {
                                    "display_name": "陈总",
                                    "source": "swagger",
                                },
                            },
                            "decision": {
                                "selected_option_id": "A",
                                "decision_summary": "先统一交付说明，再推进新的客户承诺。",
                                "task_candidates": [
                                    {
                                        "assignee_user_id": "3",
                                        "title": "补充重点客户交付说明",
                                        "description": "把交付周期、上线前提和风险提示整理成统一说明话术。",
                                        "status": "pending",
                                    }
                                ],
                            },
                        },
                        "task_queue": [
                            {
                                "task_id": "task-2-1",
                                "assignee_user_id": "3",
                                "title": "补充重点客户交付说明",
                                "description": "把交付周期、上线前提和风险提示整理成统一说明话术。",
                                "status": "pending",
                            }
                        ],
                    },
                    "msg": "decision committed",
                }
            }
        },
    }
}

TASKS_RESPONSE = {
    200: {
        "description": "任务列表查询成功",
        "content": {
            "application/json": {
                "example": {
                    "code": 200,
                    "data": {
                        "tasks": [
                            {
                                "id": 1,
                                "task_id": "queue-1",
                                "assignee_user_id": "zhangsan",
                                "title": "确认重点客户交付排期",
                                "description": "用于接口联调的队列任务",
                                "status": "pending",
                                "task_payload": {
                                    "task_ref": 1,
                                    "language": "中文",
                                },
                                "created_at": "2026-05-06T02:30:00+00:00",
                            }
                        ]
                    },
                    "msg": "tasks fetched",
                }
            }
        },
    }
}

CRUD_LIST_RESPONSE = {
    200: {
        "description": "列表查询成功",
        "content": {
            "application/json": {
                "example": {
                    "code": 200,
                    "data": {
                        "items": [
                            {
                                "id": 1,
                                "task_id": "queue-1",
                                "assignee_user_id": "zhangsan",
                                "title": "确认重点客户交付排期",
                                "description": "用于接口联调的队列任务",
                                "status": "pending",
                                "task_payload": {
                                    "task_ref": 1,
                                    "language": "中文",
                                },
                                "created_at": "2026-05-06T02:30:00+00:00",
                            }
                        ]
                    },
                    "msg": "ok",
                }
            }
        },
    }
}

CRUD_CREATE_RESPONSE = {
    201: {
        "description": "记录创建成功",
        "content": {
            "application/json": {
                "example": {
                    "code": 201,
                    "data": {
                        "item": {
                            "id": 3,
                            "task_id": "swagger-demo-task-001",
                            "assignee_user_id": "3",
                            "title": "Swagger 新建测试任务",
                            "description": "用于验证通用 CRUD 创建能力。",
                            "status": "pending",
                            "task_payload": {
                                "source": "swagger-demo",
                                "priority": "medium",
                            },
                            "created_at": "2026-05-06T03:15:00+00:00",
                        }
                    },
                    "msg": "created",
                }
            }
        },
    }
}

CRUD_GET_RESPONSE = {
    200: {
        "description": "记录详情查询成功",
        "content": {
            "application/json": {
                "example": {
                    "code": 200,
                    "data": {
                        "item": {
                            "id": 3,
                            "task_id": "swagger-demo-task-001",
                            "assignee_user_id": "3",
                            "title": "Swagger 新建测试任务",
                            "description": "用于验证通用 CRUD 创建能力。",
                            "status": "pending",
                            "task_payload": {
                                "source": "swagger-demo",
                                "priority": "medium",
                            },
                            "created_at": "2026-05-06T03:15:00+00:00",
                        }
                    },
                    "msg": "ok",
                }
            }
        },
    }
}

CRUD_UPDATE_RESPONSE = {
    200: {
        "description": "记录更新成功",
        "content": {
            "application/json": {
                "example": {
                    "code": 200,
                    "data": {
                        "item": {
                            "id": 3,
                            "task_id": "swagger-demo-task-001",
                            "assignee_user_id": "3",
                            "title": "Swagger 新建测试任务（处理中）",
                            "description": "用于验证通用 CRUD 创建能力。",
                            "status": "in_progress",
                            "task_payload": {
                                "source": "swagger-demo",
                                "priority": "medium",
                            },
                            "created_at": "2026-05-06T03:15:00+00:00",
                        }
                    },
                    "msg": "updated",
                }
            }
        },
    }
}

CRUD_DELETE_RESPONSE = {
    204: {
        "description": "记录删除成功，无响应体",
    }
}


def merge_responses(*groups: dict[int, dict]) -> dict[int, dict]:
    merged: dict[int, dict] = {}
    for group in groups:
        merged.update(group)
    return merged


app = FastAPI(
    title="AutoMage 数据库与 CRUD 接口",
    version="0.1.0",
    description=(
        "这是 AutoMage 的 PostgreSQL 数据接口服务。\n\n"
        "核心业务接口会把数据写入这些表："
        "`agent_sessions`、`staff_reports`、`manager_reports`、"
        "`agent_decision_logs`、`task_queue`。\n\n"
        "## 审计与追踪说明\n"
        "- 所有核心写接口和通用 CRUD 写接口都会写入 `audit_logs`\n"
        "- 每次请求都会生成或透传 `X-Request-Id`，并在响应头返回\n"
        "- 响应头 `X-Process-Time-Ms` 表示本次请求耗时\n"
        "- 审计日志 `payload` 中会记录本次请求的 `request_id`\n"
        "- 通用 CRUD 写接口支持通过请求头 `X-Actor-User-Id` 传入操作人\n\n"
        "## 建议联调方式\n"
        "1. 调用写接口时带上自定义 `X-Request-Id`\n"
        "2. 观察响应头中的 `X-Request-Id` 和 `X-Process-Time-Ms`\n"
        "3. 再查询 `audit_logs`，确认 `payload.request_id` 一致"
    ),
)
app.add_middleware(RequestTrackingMiddleware)
app.include_router(daily_report_router)
_settings = load_runtime_settings("configs/automage.local.toml")


@app.get(
    "/healthz",
    summary="健康检查",
    description="检查当前 API 服务是否正常运行。",
    responses=HEALTH_RESPONSE,
)
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post(
    "/api/v1/agent/init",
    response_model=ApiEnvelope,
    summary="初始化 Agent 会话",
    description="登记一个 Agent 的身份与会话信息，并写入 `agent_sessions` 表，同时记录审计日志。",
    responses=merge_responses(AGENT_INIT_RESPONSE, HTTP_422_RESPONSE),
)
def agent_init(payload: AgentInitRequest, request: Request, db: Session = Depends(get_db_session)) -> ApiEnvelope:
    identity = build_identity(payload.identity)
    data = create_agent_session(db, identity, getattr(request.state, "request_id", None))
    return ApiEnvelope(code=200, data=data, msg="agent initialized")


@app.post(
    "/api/v1/report/staff",
    response_model=ApiEnvelope,
    summary="提交员工日报快照",
    description="提交一条员工日报快照，并写入 `staff_reports` 表，同时记录审计日志。",
    responses=merge_responses(STAFF_REPORT_RESPONSE, HTTP_422_RESPONSE),
)
def post_staff_report(payload: StaffReportRequest, request: Request, db: Session = Depends(get_db_session)) -> ApiEnvelope:
    identity = build_identity(payload.identity)
    data = create_staff_report(db, identity, payload.report, getattr(request.state, "request_id", None))
    return ApiEnvelope(code=200, data={"record": data}, msg="staff report saved")


@app.post(
    "/api/v1/report/manager",
    response_model=ApiEnvelope,
    summary="提交经理汇总快照",
    description="提交一条经理汇总快照，并写入 `manager_reports` 表，同时记录审计日志。",
    responses=merge_responses(MANAGER_REPORT_RESPONSE, HTTP_422_RESPONSE),
)
def post_manager_report(
    payload: ManagerReportRequest, request: Request, db: Session = Depends(get_db_session)
) -> ApiEnvelope:
    identity = build_identity(payload.identity)
    data = create_manager_report(db, identity, payload.report, getattr(request.state, "request_id", None))
    return ApiEnvelope(code=200, data={"record": data}, msg="manager report saved")


@app.post(
    "/api/v1/decision/commit",
    response_model=ApiEnvelope,
    summary="提交决策结果",
    description="提交一条最终决策结果，写入 `agent_decision_logs`；如果带有 `task_candidates`，还会自动写入 `task_queue`。",
    responses=merge_responses(DECISION_COMMIT_RESPONSE, HTTP_422_RESPONSE),
)
def post_decision_commit(
    payload: DecisionCommitRequest, request: Request, db: Session = Depends(get_db_session)
) -> ApiEnvelope:
    identity = build_identity(payload.identity)
    data = commit_decision(db, identity, payload.decision, getattr(request.state, "request_id", None))
    return ApiEnvelope(code=200, data=data, msg="decision committed")


@app.get(
    "/api/v1/tasks",
    response_model=ApiEnvelope,
    summary="查询任务列表",
    description="从 `task_queue` 表查询任务，可按 `user_id` 和 `status` 过滤。",
    responses=merge_responses(TASKS_RESPONSE, HTTP_422_RESPONSE),
)
def get_tasks(
    user_id: str | None = Query(default=None, description="按任务负责人 user_id 过滤", examples=["3"]),
    status: str | None = Query(default=None, description="按任务状态过滤", examples=["pending"]),
    db: Session = Depends(get_db_session),
) -> ApiEnvelope:
    tasks = list_tasks(db, user_id=user_id, status=status)
    return ApiEnvelope(code=200, data={"tasks": tasks}, msg="tasks fetched")


@app.get(
    "/api/v1/crud/{resource}",
    response_model=ApiEnvelope,
    summary="通用列表查询",
    description=(
        "通用 CRUD 列表接口。当前支持的资源表有："
        "`agent_sessions`、`staff_reports`、`manager_reports`、`agent_decision_logs`、`task_queue`。"
    ),
    responses=merge_responses(CRUD_LIST_RESPONSE, HTTP_404_RESOURCE_RESPONSE, HTTP_422_RESPONSE),
)
def crud_list(
    resource: str = Path(description="资源表名，例如 task_queue 或 staff_reports"),
    limit: int = Query(default=50, ge=1, le=200, description="最多返回多少条记录", examples=[20]),
    offset: int = Query(default=0, ge=0, description="分页偏移量", examples=[0]),
    db: Session = Depends(get_db_session),
) -> ApiEnvelope:
    if resource not in MODEL_REGISTRY:
        raise HTTPException(status_code=404, detail="resource not found")
    return ApiEnvelope(code=200, data={"items": list_records(db, resource, limit=limit, offset=offset)}, msg="ok")


@app.post(
    "/api/v1/crud/{resource}",
    response_model=ApiEnvelope,
    status_code=201,
    summary="通用创建记录",
    description="通用 CRUD 创建接口，会直接往指定资源表写入一条记录，同时记录审计日志。",
    responses=merge_responses(CRUD_CREATE_RESPONSE, HTTP_400_RESPONSE, HTTP_404_RESOURCE_RESPONSE, HTTP_422_RESPONSE),
)
def crud_create(
    resource: str,
    payload: CrudWriteRequest,
    request: Request,
    db: Session = Depends(get_db_session),
) -> ApiEnvelope:
    if resource not in MODEL_REGISTRY:
        raise HTTPException(status_code=404, detail="resource not found")
    try:
        item = create_record(db, resource, payload.data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    _audit_crud_write(
        request=request,
        db=db,
        action="crud_create",
        target_type=resource,
        target_id=int(item["id"]),
        summary=f"Created record in {resource}",
        payload={"resource": resource, "data": payload.data, "result": item},
    )
    return ApiEnvelope(code=201, data={"item": item}, msg="created")


@app.get(
    "/api/v1/crud/{resource}/{record_id}",
    response_model=ApiEnvelope,
    summary="通用单条查询",
    description="通用 CRUD 详情接口，按主键 ID 读取指定资源表中的一条记录。",
    responses=merge_responses(CRUD_GET_RESPONSE, HTTP_404_RESOURCE_RESPONSE, HTTP_422_RESPONSE),
)
def crud_get(resource: str, record_id: int, db: Session = Depends(get_db_session)) -> ApiEnvelope:
    if resource not in MODEL_REGISTRY:
        raise HTTPException(status_code=404, detail="resource not found")
    item = get_record(db, resource, record_id)
    if item is None:
        raise HTTPException(status_code=404, detail="record not found")
    return ApiEnvelope(code=200, data={"item": item}, msg="ok")


@app.put(
    "/api/v1/crud/{resource}/{record_id}",
    response_model=ApiEnvelope,
    summary="通用整条更新",
    description="通用 CRUD 全量更新接口，会整体更新该记录可写字段，同时记录审计日志。",
    responses=merge_responses(CRUD_UPDATE_RESPONSE, HTTP_400_RESPONSE, HTTP_404_RESOURCE_RESPONSE, HTTP_422_RESPONSE),
)
def crud_put(
    resource: str,
    record_id: int,
    payload: CrudWriteRequest,
    request: Request,
    db: Session = Depends(get_db_session),
) -> ApiEnvelope:
    if resource not in MODEL_REGISTRY:
        raise HTTPException(status_code=404, detail="resource not found")
    try:
        item = update_record(db, resource, record_id, payload.data, partial=False)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if item is None:
        raise HTTPException(status_code=404, detail="record not found")
    _audit_crud_write(
        request=request,
        db=db,
        action="crud_put",
        target_type=resource,
        target_id=record_id,
        summary=f"Replaced record {record_id} in {resource}",
        payload={"resource": resource, "data": payload.data, "result": item},
    )
    return ApiEnvelope(code=200, data={"item": item}, msg="updated")


@app.patch(
    "/api/v1/crud/{resource}/{record_id}",
    response_model=ApiEnvelope,
    summary="通用局部更新",
    description="通用 CRUD 局部更新接口，只更新你传入的字段，同时记录审计日志。",
    responses=merge_responses(CRUD_UPDATE_RESPONSE, HTTP_400_RESPONSE, HTTP_404_RESOURCE_RESPONSE, HTTP_422_RESPONSE),
)
def crud_patch(
    resource: str,
    record_id: int,
    payload: CrudWriteRequest,
    request: Request,
    db: Session = Depends(get_db_session),
) -> ApiEnvelope:
    if resource not in MODEL_REGISTRY:
        raise HTTPException(status_code=404, detail="resource not found")
    try:
        item = update_record(db, resource, record_id, payload.data, partial=True)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if item is None:
        raise HTTPException(status_code=404, detail="record not found")
    _audit_crud_write(
        request=request,
        db=db,
        action="crud_patch",
        target_type=resource,
        target_id=record_id,
        summary=f"Patched record {record_id} in {resource}",
        payload={"resource": resource, "data": payload.data, "result": item},
    )
    return ApiEnvelope(code=200, data={"item": item}, msg="updated")


@app.delete(
    "/api/v1/crud/{resource}/{record_id}",
    status_code=204,
    summary="通用删除记录",
    description="通用 CRUD 删除接口，按主键 ID 删除指定资源表中的一条记录，同时记录审计日志。",
    responses=merge_responses(CRUD_DELETE_RESPONSE, HTTP_404_RESOURCE_RESPONSE, HTTP_422_RESPONSE),
)
def crud_delete(resource: str, record_id: int, request: Request, db: Session = Depends(get_db_session)) -> Response:
    if resource not in MODEL_REGISTRY:
        raise HTTPException(status_code=404, detail="resource not found")
    existing = get_record(db, resource, record_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="record not found")
    deleted = delete_record(db, resource, record_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="record not found")
    _audit_crud_write(
        request=request,
        db=db,
        action="crud_delete",
        target_type=resource,
        target_id=record_id,
        summary=f"Deleted record {record_id} from {resource}",
        payload={"resource": resource, "deleted_record": existing},
    )
    return Response(status_code=204)


def _audit_crud_write(
    request: Request | None,
    db: Session,
    *,
    action: str,
    target_type: str,
    target_id: int,
    summary: str,
    payload: dict,
) -> None:
    if not _settings.audit_enabled:
        return
    write_audit_log(
        db,
        org_id=_settings.audit_org_id,
        actor_user_id=_safe_int(request.headers.get("X-Actor-User-Id")) if request is not None else None,
        target_type=target_type,
        target_id=target_id,
        action=action,
        summary=summary,
        payload=payload,
    )
    db.commit()


def _safe_int(value: str | None) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None
