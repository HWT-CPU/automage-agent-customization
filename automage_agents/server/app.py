from __future__ import annotations

from fastapi import Depends, FastAPI, HTTPException, Path, Query, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from automage_agents.config import load_runtime_settings
from automage_agents.core.enums import AgentRole
from automage_agents.server.audit import write_audit_log
from automage_agents.server.auth import (
    AuthenticatedActor,
    assert_actor_has_role,
    assert_identity_matches_actor,
    assert_audit_log_access,
    assert_manager_report_payload_allowed,
    assert_task_create_payload_allowed,
    assert_task_update_allowed,
    filter_tasks_for_actor,
    filter_audit_logs_for_actor,
    filter_manager_reports_for_actor,
    filter_staff_reports_for_actor,
    get_current_actor,
    require_roles,
    resolve_task_query_scope,
)
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
from automage_agents.server.middleware import AbuseProtectionMiddleware, RequestTrackingMiddleware
from automage_agents.server.schemas import (
    AgentInitRequest,
    ApiConflictEnvelope,
    ApiEnvelope,
    CrudWriteRequest,
    DecisionCommitRequest,
    DreamRunRequest,
    ManagerReportRequest,
    StaffReportRequest,
    TaskCreateRequest,
    TaskUpdateRequest,
)
from automage_agents.server.service import (
    build_identity,
    commit_decision,
    ConflictError,
    create_agent_session,
    create_manager_report,
    create_staff_report,
    create_tasks,
    get_task_by_task_id,
    list_audit_logs,
    list_manager_reports,
    list_staff_reports,
    list_tasks,
    run_dream_from_summary,
    update_task,
)


HTTP_400_RESPONSE = {
    400: {
        "description": "请求体不合法。",
        "content": {
            "application/json": {
                "example": {"detail": "请求体不合法，缺少必要字段 id"}
            }
        },
    }
}

HTTP_404_RESOURCE_RESPONSE = {
    404: {
        "description": "资源不存在。",
        "content": {
            "application/json": {
                "examples": {
                    "resource_not_found": {
                        "summary": "资源不存在",
                        "value": {"detail": "资源不存在"},
                    },
                    "record_not_found": {
                        "summary": "记录不存在",
                        "value": {"detail": "记录不存在"},
                    },
                }
            }
        },
    }
}

HTTP_404_RECORD_RESPONSE = {
    404: {
        "description": "记录不存在。",
        "content": {
            "application/json": {
                "example": {"detail": "记录不存在"}
            }
        },
    }
}

HTTP_422_RESPONSE = {
    422: {
        "description": "请求校验失败。",
        "content": {
            "application/json": {
                "example": {
                    "detail": [
                        {
                            "type": "missing",
                            "loc": ["body", "identity", "node_id"],
                            "msg": "字段不能为空",
                            "input": {},
                        }
                    ]
                }
            }
        },
    }
}

HTTP_409_CONFLICT_RESPONSE = {
    409: {
        "description": "请求冲突，通常表示幂等键重复但请求内容不一致，或重复提交命中了已存在记录。",
        "model": ApiConflictEnvelope,
        "content": {
            "application/json": {
                "examples": {
                    "staff_report_conflict": {
                        "summary": "员工日报重复提交冲突",
                        "value": {
                            "code": 409,
                            "data": None,
                            "msg": "员工日报提交冲突",
                            "error": {
                                "error_type": "conflict",
                                "error_code": "staff_report_conflict",
                                "message": "同一员工在同一日期的日报已存在，且提交内容不一致。",
                                "conflict_target": "staff_report:org_id+user_id+record_date",
                                "request_id": "req_staff_conflict_001",
                            },
                        },
                    },
                    "decision_commit_conflict": {
                        "summary": "正式决策提交冲突",
                        "value": {
                            "code": 409,
                            "data": None,
                            "msg": "正式决策提交冲突",
                            "error": {
                                "error_type": "conflict",
                                "error_code": "decision_commit_conflict",
                                "message": "正式决策提交触发了已存在任务的冲突校验，请确认任务候选是否重复。",
                                "conflict_target": "decision_commit:task_candidates",
                                "request_id": "req_decision_conflict_001",
                            },
                        },
                    },
                    "task_create_conflict": {
                        "summary": "任务创建冲突",
                        "value": {
                            "code": 409,
                            "data": None,
                            "msg": "任务创建冲突",
                            "error": {
                                "error_type": "conflict",
                                "error_code": "task_create_conflict",
                                "message": "任务 ID 已存在，但本次提交内容与已有任务不一致。",
                                "conflict_target": "task_create:task_id",
                                "request_id": "req_task_create_conflict_001",
                            },
                        },
                    },
                    "task_update_conflict": {
                        "summary": "任务更新冲突",
                        "value": {
                            "code": 409,
                            "data": None,
                            "msg": "任务更新冲突",
                            "error": {
                                "error_type": "conflict",
                                "error_code": "task_update_conflict",
                                "message": "同一 request_id 已用于该任务的其他更新内容，不能重复覆盖。",
                                "conflict_target": "task_update:task_id+request_id",
                                "request_id": "req_task_update_conflict_001",
                            },
                        },
                    },
                }
            }
        },
    }
}

HTTP_403_RESPONSE = {
    403: {
        "description": "无权访问或操作该资源，包含角色不允许和超出 RBAC 范围两类场景。",
        "content": {
            "application/json": {
                "examples": {
                    "role_forbidden": {
                        "summary": "角色不允许",
                        "value": {"detail": "Role manager is not allowed to access this resource"},
                    },
                    "rbac_scope_forbidden": {
                        "summary": "超出 RBAC 范围",
                        "value": {"detail": "Manager report is outside your RBAC scope"},
                    },
                    "task_update_forbidden": {
                        "summary": "任务更新越权",
                        "value": {"detail": "You are not allowed to update this task"},
                    },
                }
            }
        },
    }
}


def merge_responses(*groups: dict[int, dict]) -> dict[int, dict]:
    merged: dict[int, dict] = {}
    for group in groups:
        merged.update(group)
    return merged


def normalize_error_detail(message: str) -> str:
    return message.replace("Unknown or immutable fields", "Unknown or immutable fields").replace(
        "Missing required fields", "Missing required fields"
    )


def build_conflict_response(
    request: Request,
    *,
    error_code: str,
    message: str,
    conflict_target: str,
    msg: str,
) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content=ApiConflictEnvelope(
            code=409,
            data=None,
            msg=msg,
            error={
                "error_type": "conflict",
                "error_code": error_code,
                "message": message,
                "conflict_target": conflict_target,
                "request_id": getattr(request.state, "request_id", None),
            },
        ).model_dump(),
    )


app = FastAPI(
    title="AutoMage 中文版 CRUD API",
    version="0.2.0",
    description=(
        "AutoMage 中文联调 API 文档。\n\n"
        "当前已统一员工日报、经理汇总、任务、审计日志与通用 CRUD 的 Swagger 中文描述。\n"
    ),
)
app.add_middleware(RequestTrackingMiddleware)
app.add_middleware(AbuseProtectionMiddleware)
app.include_router(daily_report_router)
_settings = load_runtime_settings("configs/automage.local.toml")

REPORT_READ_ROLES = require_roles(AgentRole.STAFF, AgentRole.MANAGER, AgentRole.EXECUTIVE)
MANAGER_WRITE_ROLES = require_roles(AgentRole.MANAGER, AgentRole.EXECUTIVE)
EXECUTIVE_ONLY = require_roles(AgentRole.EXECUTIVE)


@app.get("/healthz", summary="健康检查")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post(
    "/api/v1/agent/init",
    response_model=ApiEnvelope,
    summary="初始化 Agent 会话",
    responses=merge_responses(HTTP_422_RESPONSE),
)
def agent_init(payload: AgentInitRequest, request: Request, db: Session = Depends(get_db_session)) -> ApiEnvelope:
    actor = get_current_actor(request)
    assert_identity_matches_actor(actor, payload.identity, db=db)
    identity = build_identity(payload.identity)
    data = create_agent_session(db, identity, getattr(request.state, "request_id", None))
    return ApiEnvelope(code=200, data=data, msg="Agent 会话初始化成功")


@app.post(
    "/api/v1/report/staff",
    response_model=ApiEnvelope,
    summary="提交员工日报",
    description="写入员工日报快照，并同步关联正式日报落表数据。",
    responses=merge_responses(HTTP_409_CONFLICT_RESPONSE, HTTP_422_RESPONSE),
)
def post_staff_report(payload: StaffReportRequest, request: Request, db: Session = Depends(get_db_session)) -> ApiEnvelope:
    actor = get_current_actor(request)
    assert_actor_has_role(actor, AgentRole.STAFF, db=db)
    assert_identity_matches_actor(actor, payload.identity, db=db)
    identity = build_identity(payload.identity)
    try:
        data = create_staff_report(db, identity, payload.report, getattr(request.state, "request_id", None))
    except ConflictError as exc:
        return build_conflict_response(
            request,
            error_code="staff_report_conflict",
            message=str(exc),
            conflict_target="staff_report:org_id+user_id+record_date",
            msg="员工日报提交冲突",
        )
    return ApiEnvelope(code=200, data={"record": data}, msg="员工日报提交成功")


@app.get(
    "/api/v1/report/staff",
    response_model=ApiEnvelope,
    summary="查询员工日报列表",
    description="按组织、部门、日期和用户维度查询员工日报列表。",
    responses=merge_responses(HTTP_422_RESPONSE),
)
def get_staff_reports(
    org_id: str | None = Query(default=None),
    department_id: str | None = Query(default=None),
    record_date: str | None = Query(default=None),
    user_id: str | None = Query(default=None),
    actor: AuthenticatedActor | None = Depends(REPORT_READ_ROLES),
    db: Session = Depends(get_db_session),
) -> ApiEnvelope:
    reports = list_staff_reports(
        db,
        org_id=org_id,
        department_id=department_id,
        record_date=record_date,
        user_id=user_id,
    )
    reports = filter_staff_reports_for_actor(actor, reports)
    return ApiEnvelope(code=200, data={"reports": reports}, msg="员工日报列表查询成功")


@app.post(
    "/api/v1/report/manager",
    response_model=ApiEnvelope,
    summary="提交经理汇总",
    description="写入经理汇总快照，供后续决策与任务拆分使用。",
    responses=merge_responses(HTTP_403_RESPONSE, HTTP_422_RESPONSE),
)
def post_manager_report(
    payload: ManagerReportRequest,
    request: Request,
    actor: AuthenticatedActor | None = Depends(MANAGER_WRITE_ROLES),
    db: Session = Depends(get_db_session),
) -> ApiEnvelope:
    assert_manager_report_payload_allowed(actor, payload.report, db=db)
    assert_identity_matches_actor(actor, payload.identity, db=db)
    identity = build_identity(payload.identity)
    data = create_manager_report(db, identity, payload.report, getattr(request.state, "request_id", None))
    return ApiEnvelope(code=200, data={"record": data}, msg="经理汇总提交成功")


@app.get(
    "/api/v1/report/manager",
    response_model=ApiEnvelope,
    summary="查询经理汇总列表",
    description="按组织、日期、部门和经理用户查询经理汇总列表。",
    responses=merge_responses(HTTP_422_RESPONSE),
)
def get_manager_reports(
    org_id: str | None = Query(default=None),
    summary_date: str | None = Query(default=None),
    dept_id: str | None = Query(default=None),
    manager_user_id: str | None = Query(default=None),
    actor: AuthenticatedActor | None = Depends(MANAGER_WRITE_ROLES),
    db: Session = Depends(get_db_session),
) -> ApiEnvelope:
    reports = list_manager_reports(
        db,
        org_id=org_id,
        summary_date=summary_date,
        dept_id=dept_id,
        manager_user_id=manager_user_id,
    )
    reports = filter_manager_reports_for_actor(actor, reports)
    return ApiEnvelope(code=200, data={"reports": reports}, msg="经理汇总列表查询成功")


@app.post(
    "/internal/dream/run",
    response_model=ApiEnvelope,
    summary="生成 Dream 决策草稿",
    description="基于经理汇总摘要生成 Dream 决策草稿，供高层确认。",
    responses=merge_responses(HTTP_403_RESPONSE, HTTP_422_RESPONSE, HTTP_404_RECORD_RESPONSE),
)
def post_dream_run(
    payload: DreamRunRequest,
    request: Request,
    actor: AuthenticatedActor | None = Depends(EXECUTIVE_ONLY),
    db: Session = Depends(get_db_session),
) -> ApiEnvelope:
    if actor is None:
        raise HTTPException(status_code=403, detail="仅 executive 角色可调用")
    data = run_dream_from_summary(
        db,
        summary_id=payload.summary_id,
        actor_identity=actor.identity,
        request_id=getattr(request.state, "request_id", None),
    )
    return ApiEnvelope(code=200, data=data, msg="Dream 决策草稿生成成功")


@app.post(
    "/api/v1/decision/commit",
    response_model=ApiEnvelope,
    summary="提交正式决策",
    description="提交高层正式决策，并沉淀可下发的任务候选。",
    responses=merge_responses(HTTP_403_RESPONSE, HTTP_409_CONFLICT_RESPONSE, HTTP_422_RESPONSE),
)
def post_decision_commit(
    payload: DecisionCommitRequest,
    request: Request,
    actor: AuthenticatedActor | None = Depends(EXECUTIVE_ONLY),
    db: Session = Depends(get_db_session),
) -> ApiEnvelope:
    assert_identity_matches_actor(actor, payload.identity, db=db)
    identity = build_identity(payload.identity)
    try:
        data = commit_decision(db, identity, payload.decision, getattr(request.state, "request_id", None))
    except ConflictError as exc:
        return build_conflict_response(
            request,
            error_code="decision_commit_conflict",
            message=str(exc),
            conflict_target="decision_commit:task_candidates",
            msg="正式决策提交冲突",
        )
    return ApiEnvelope(code=200, data=data, msg="正式决策提交成功")


@app.post(
    "/api/v1/tasks",
    response_model=ApiEnvelope,
    summary="创建正式任务",
    description="创建正式任务，并同步写入兼容镜像 task_queue。",
    responses=merge_responses(HTTP_403_RESPONSE, HTTP_409_CONFLICT_RESPONSE, HTTP_422_RESPONSE),
)
def post_tasks(
    payload: TaskCreateRequest,
    request: Request,
    actor: AuthenticatedActor | None = Depends(MANAGER_WRITE_ROLES),
    db: Session = Depends(get_db_session),
) -> ApiEnvelope:
    assert_task_create_payload_allowed(actor, payload.tasks, db=db)
    try:
        tasks = create_tasks(db, tasks=payload.tasks, request_id=getattr(request.state, "request_id", None))
    except ConflictError as exc:
        return build_conflict_response(
            request,
            error_code="task_create_conflict",
            message=str(exc),
            conflict_target="task_create:task_id",
            msg="任务创建冲突",
        )
    return ApiEnvelope(code=200, data={"tasks": tasks}, msg="任务创建成功")


@app.get(
    "/api/v1/tasks",
    response_model=ApiEnvelope,
    summary="查询任务列表",
    description="基于 tasks 与 task_assignments 查询任务列表，并按角色与节点做隔离。",
    responses=merge_responses(HTTP_422_RESPONSE),
)
def get_tasks(
    user_id: str | None = Query(default=None, description="任务所属用户 ID 别名参数"),
    assignee_user_id: str | None = Query(default=None, description="任务执行人用户 ID，和 user_id 口径兼容"),
    status: str | None = Query(default=None, description="任务状态过滤条件"),
    actor: AuthenticatedActor | None = Depends(REPORT_READ_ROLES),
    db: Session = Depends(get_db_session),
) -> ApiEnvelope:
    user_id, assignee_user_id = resolve_task_query_scope(actor, user_id=user_id, assignee_user_id=assignee_user_id)
    tasks = list_tasks(db, user_id=user_id, assignee_user_id=assignee_user_id, status=status)
    tasks = filter_tasks_for_actor(actor, tasks)
    return ApiEnvelope(code=200, data={"tasks": tasks}, msg="任务列表查询成功")


@app.patch(
    "/api/v1/tasks/{task_id}",
    response_model=ApiEnvelope,
    summary="更新任务",
    description="更新正式任务状态、标题、说明或附加任务载荷，并记录 task update。",
    responses=merge_responses(HTTP_403_RESPONSE, HTTP_404_RECORD_RESPONSE, HTTP_409_CONFLICT_RESPONSE, HTTP_422_RESPONSE),
)
def patch_task(
    task_id: str,
    payload: TaskUpdateRequest,
    request: Request,
    actor: AuthenticatedActor | None = Depends(REPORT_READ_ROLES),
    db: Session = Depends(get_db_session),
) -> ApiEnvelope:
    existing_task = get_task_by_task_id(db, task_id)
    if existing_task is None:
        raise HTTPException(status_code=404, detail="记录不存在")
    assert_task_update_allowed(actor, existing_task, db=db)
    try:
        task = update_task(
            db,
            task_id=task_id,
            status=payload.status,
            title=payload.title,
            description=payload.description,
            task_payload=payload.task_payload,
            request_id=getattr(request.state, "request_id", None),
            actor_user_id=actor.identity.user_id if actor is not None else None,
        )
    except ConflictError as exc:
        return build_conflict_response(
            request,
            error_code="task_update_conflict",
            message=str(exc),
            conflict_target="task_update:task_id+request_id",
            msg="任务更新冲突",
        )
    return ApiEnvelope(code=200, data={"task": task}, msg="任务更新成功")


@app.get(
    "/api/v1/audit-logs",
    response_model=ApiEnvelope,
    summary="查询审计日志",
    description="按对象类型、操作人和时间范围查询审计日志。",
    responses=merge_responses(HTTP_422_RESPONSE),
)
def get_audit_logs(
    target_type: str | None = Query(default=None),
    actor_user_id: str | None = Query(default=None),
    started_at: str | None = Query(default=None),
    ended_at: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    actor: AuthenticatedActor | None = Depends(REPORT_READ_ROLES),
    db: Session = Depends(get_db_session),
) -> ApiEnvelope:
    assert_audit_log_access(actor, target_type=target_type, actor_user_id=actor_user_id, db=db)
    logs = list_audit_logs(
        db,
        target_type=target_type,
        actor_user_id=actor_user_id,
        started_at=started_at,
        ended_at=ended_at,
        limit=limit,
    )
    logs = filter_audit_logs_for_actor(actor, logs)
    return ApiEnvelope(code=200, data={"items": logs}, msg="审计日志列表查询成功")


@app.get(
    "/api/v1/crud/{resource}",
    response_model=ApiEnvelope,
    summary="通用列表查询",
    description="按资源名查询通用表数据列表。",
    responses=merge_responses(HTTP_404_RESOURCE_RESPONSE, HTTP_422_RESPONSE),
)
def crud_list(
    resource: str = Path(description="资源名，例如 tasks、task_assignments、task_updates、staff_reports"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    actor: AuthenticatedActor | None = Depends(EXECUTIVE_ONLY),
    db: Session = Depends(get_db_session),
) -> ApiEnvelope:
    if resource not in MODEL_REGISTRY:
        raise HTTPException(status_code=404, detail="资源不存在")
    return ApiEnvelope(code=200, data={"items": list_records(db, resource, limit=limit, offset=offset)}, msg="查询成功")


@app.post(
    "/api/v1/crud/{resource}",
    response_model=ApiEnvelope,
    status_code=201,
    summary="通用创建记录",
    description="按资源名创建一条新记录，并写入审计日志。",
    responses=merge_responses(HTTP_400_RESPONSE, HTTP_404_RESOURCE_RESPONSE, HTTP_422_RESPONSE),
)
def crud_create(
    resource: str,
    payload: CrudWriteRequest,
    request: Request,
    actor: AuthenticatedActor | None = Depends(EXECUTIVE_ONLY),
    db: Session = Depends(get_db_session),
) -> ApiEnvelope:
    if resource not in MODEL_REGISTRY:
        raise HTTPException(status_code=404, detail="资源不存在")
    try:
        item = create_record(db, resource, payload.data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=normalize_error_detail(str(exc))) from exc
    _audit_crud_write(
        request=request,
        db=db,
        action="crud_create",
        target_type=resource,
        target_id=int(item["id"]),
        summary=f"创建 {resource} 资源记录",
        payload={"resource": resource, "data": payload.data, "result": item},
    )
    return ApiEnvelope(code=201, data={"item": item}, msg="创建成功")


@app.get(
    "/api/v1/crud/{resource}/{record_id}",
    response_model=ApiEnvelope,
    summary="通用单条查询",
    description="按资源名和记录 ID 查询单条记录。",
    responses=merge_responses(HTTP_404_RESOURCE_RESPONSE, HTTP_422_RESPONSE),
)
def crud_get(
    resource: str,
    record_id: int,
    actor: AuthenticatedActor | None = Depends(EXECUTIVE_ONLY),
    db: Session = Depends(get_db_session),
) -> ApiEnvelope:
    if resource not in MODEL_REGISTRY:
        raise HTTPException(status_code=404, detail="资源不存在")
    item = get_record(db, resource, record_id)
    if item is None:
        raise HTTPException(status_code=404, detail="记录不存在")
    return ApiEnvelope(code=200, data={"item": item}, msg="查询成功")


@app.put(
    "/api/v1/crud/{resource}/{record_id}",
    response_model=ApiEnvelope,
    summary="通用整条替换",
    description="按资源名和记录 ID 整条替换记录，并写入审计日志。",
    responses=merge_responses(HTTP_400_RESPONSE, HTTP_404_RESOURCE_RESPONSE, HTTP_422_RESPONSE),
)
def crud_put(
    resource: str,
    record_id: int,
    payload: CrudWriteRequest,
    request: Request,
    actor: AuthenticatedActor | None = Depends(EXECUTIVE_ONLY),
    db: Session = Depends(get_db_session),
) -> ApiEnvelope:
    if resource not in MODEL_REGISTRY:
        raise HTTPException(status_code=404, detail="资源不存在")
    try:
        item = update_record(db, resource, record_id, payload.data, partial=False)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=normalize_error_detail(str(exc))) from exc
    if item is None:
        raise HTTPException(status_code=404, detail="记录不存在")
    _audit_crud_write(
        request=request,
        db=db,
        action="crud_put",
        target_type=resource,
        target_id=record_id,
        summary=f"整条替换 {resource} 资源记录 {record_id}",
        payload={"resource": resource, "data": payload.data, "result": item},
    )
    return ApiEnvelope(code=200, data={"item": item}, msg="更新成功")


@app.patch(
    "/api/v1/crud/{resource}/{record_id}",
    response_model=ApiEnvelope,
    summary="通用局部更新",
    description="按资源名和记录 ID 局部更新记录，并写入审计日志。",
    responses=merge_responses(HTTP_400_RESPONSE, HTTP_404_RESOURCE_RESPONSE, HTTP_422_RESPONSE),
)
def crud_patch(
    resource: str,
    record_id: int,
    payload: CrudWriteRequest,
    request: Request,
    actor: AuthenticatedActor | None = Depends(EXECUTIVE_ONLY),
    db: Session = Depends(get_db_session),
) -> ApiEnvelope:
    if resource not in MODEL_REGISTRY:
        raise HTTPException(status_code=404, detail="资源不存在")
    try:
        item = update_record(db, resource, record_id, payload.data, partial=True)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=normalize_error_detail(str(exc))) from exc
    if item is None:
        raise HTTPException(status_code=404, detail="记录不存在")
    _audit_crud_write(
        request=request,
        db=db,
        action="crud_patch",
        target_type=resource,
        target_id=record_id,
        summary=f"局部更新 {resource} 资源记录 {record_id}",
        payload={"resource": resource, "data": payload.data, "result": item},
    )
    return ApiEnvelope(code=200, data={"item": item}, msg="更新成功")


@app.delete(
    "/api/v1/crud/{resource}/{record_id}",
    status_code=204,
    summary="通用删除记录",
    description="按资源名和记录 ID 删除记录，并写入审计日志。",
    responses=merge_responses(HTTP_404_RESOURCE_RESPONSE, HTTP_422_RESPONSE),
)
def crud_delete(
    resource: str,
    record_id: int,
    request: Request,
    actor: AuthenticatedActor | None = Depends(EXECUTIVE_ONLY),
    db: Session = Depends(get_db_session),
) -> Response:
    if resource not in MODEL_REGISTRY:
        raise HTTPException(status_code=404, detail="资源不存在")
    existing = get_record(db, resource, record_id)
    if existing is None:
        raise HTTPException(status_code=404, detail="记录不存在")
    deleted = delete_record(db, resource, record_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="记录不存在")
    _audit_crud_write(
        request=request,
        db=db,
        action="crud_delete",
        target_type=resource,
        target_id=record_id,
        summary=f"删除 {resource} 资源记录 {record_id}",
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

