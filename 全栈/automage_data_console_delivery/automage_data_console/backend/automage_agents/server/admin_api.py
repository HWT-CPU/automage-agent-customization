"""Admin API — 中控台统计、用户管理、系统监控"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, text
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from automage_agents.db.models import UserModel
from automage_agents.server.auth import AuthenticatedActor, get_current_actor, assert_actor_has_role
from automage_agents.core.enums import AgentRole
from automage_agents.server.deps import get_db_session

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])


@router.get("/stats/department", summary="部门统计")
def department_stats(
    actor: AuthenticatedActor | None = Depends(get_current_actor),
    db: Session = Depends(get_db_session),
):
    """返回部门全景数据：员工数、日报提交率、任务完成率、异常数"""
    assert_actor_has_role(actor, AgentRole.MANAGER, AgentRole.EXECUTIVE, db=db)

    dept_id = actor.identity.department_id if actor else None

    # 员工总数
    total_users = db.query(func.count(UserModel.id)).filter(
        UserModel.deleted_at.is_(None), UserModel.status == 1
    ).scalar() or 0

    # 日报统计
    today = func.current_date()
    reports_today = db.execute(text(
        "SELECT COUNT(*) FROM work_records WHERE record_date = CURRENT_DATE AND deleted_at IS NULL"
    )).scalar() or 0

    # 任务统计
    total_tasks = db.execute(text("SELECT COUNT(*) FROM tasks WHERE deleted_at IS NULL")).scalar() or 0
    done_tasks = db.execute(text(
        "SELECT COUNT(*) FROM tasks WHERE deleted_at IS NULL AND status IN (3, 4)"
    )).scalar() or 0
    completion_rate = round(done_tasks / total_tasks * 100) if total_tasks > 0 else 0

    # 异常统计
    open_incidents = db.execute(text(
        "SELECT COUNT(*) FROM incidents WHERE deleted_at IS NULL AND status IN (0, 1)"
    )).scalar() or 0

    # 按部门统计
    dept_stats = db.execute(text("""
        SELECT d.name, COUNT(u.id)
        FROM departments d
        LEFT JOIN users u ON u.deleted_at IS NULL AND u.status = 1
        LEFT JOIN department_members dm ON dm.department_id = d.id AND dm.user_id = u.id
        WHERE d.deleted_at IS NULL
        GROUP BY d.id, d.name
    """)).fetchall()

    return {
        "code": 200,
        "data": {
            "total_users": total_users,
            "reports_today": reports_today,
            "total_tasks": total_tasks,
            "done_tasks": done_tasks,
            "completion_rate": completion_rate,
            "open_incidents": open_incidents,
            "departments": [{"name": r[0], "user_count": r[1]} for r in dept_stats],
        },
        "msg": "ok",
    }


@router.get("/stats/system", summary="系统统计")
def system_stats(
    actor: AuthenticatedActor | None = Depends(get_current_actor),
    db: Session = Depends(get_db_session),
):
    """返回系统运行数据：API 调用量、DB 连接、审计日志数"""
    assert_actor_has_role(actor, AgentRole.MANAGER, AgentRole.EXECUTIVE, db=db)

    audit_count = db.execute(text("SELECT COUNT(*) FROM audit_logs")).scalar() or 0
    session_count = db.execute(text("SELECT COUNT(*) FROM agent_sessions")).scalar() or 0
    task_queue_count = db.execute(text("SELECT COUNT(*) FROM task_queue")).scalar() or 0

    return {
        "code": 200,
        "data": {
            "audit_logs": audit_count,
            "agent_sessions": session_count,
            "task_queue": task_queue_count,
            "backend": "FastAPI + PostgreSQL + Redis",
            "mode": "production",
        },
        "msg": "ok",
    }


@router.get("/users", summary="用户列表")
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = None,
    role: str | None = None,
    actor: AuthenticatedActor | None = Depends(get_current_actor),
    db: Session = Depends(get_db_session),
):
    """分页查询用户列表，支持搜索和角色筛选"""
    assert_actor_has_role(actor, AgentRole.MANAGER, AgentRole.EXECUTIVE, db=db)

    query = db.query(UserModel).filter(UserModel.deleted_at.is_(None))

    if search:
        query = query.filter(
            (UserModel.username.ilike(f"%{search}%")) |
            (UserModel.display_name.ilike(f"%{search}%"))
        )

    if role:
        query = query.filter(UserModel.meta["role"].astext == role)

    total = query.count()
    users = query.order_by(UserModel.id).offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for u in users:
        meta = u.meta or {}
        items.append({
            "id": str(u.id),
            "username": u.username,
            "display_name": u.display_name,
            "role": meta.get("role", "staff"),
            "level": meta.get("level", "l1_staff"),
            "department_id": meta.get("department_id", ""),
            "status": u.status,
            "last_login_at": u.last_login_at.isoformat() if u.last_login_at else None,
        })

    return {
        "code": 200,
        "data": {"items": items, "total": total, "page": page, "page_size": page_size},
        "msg": "ok",
    }


@router.get("/users/{user_id}/reports", summary="用户日报统计")
def user_report_stats(
    user_id: int,
    days: int = Query(7, ge=1, le=30),
    actor: AuthenticatedActor | None = Depends(get_current_actor),
    db: Session = Depends(get_db_session),
):
    """查询指定用户最近 N 天的日报提交情况"""
    assert_actor_has_role(actor, AgentRole.MANAGER, AgentRole.EXECUTIVE, db=db)

    rows = db.execute(text("""
        SELECT record_date, COUNT(*) as cnt
        FROM work_records
        WHERE user_id = :uid AND deleted_at IS NULL
          AND record_date >= CURRENT_DATE - :days
        GROUP BY record_date
        ORDER BY record_date DESC
    """), {"uid": user_id, "days": days}).fetchall()

    return {
        "code": 200,
        "data": {
            "user_id": user_id,
            "days": days,
            "records": [{"date": str(r[0]), "count": r[1]} for r in rows],
        },
        "msg": "ok",
    }


@router.get("/audit", summary="审计日志查询")
def audit_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    action: str | None = None,
    target_type: str | None = None,
    actor_user_id: str | None = None,
    actor: AuthenticatedActor | None = Depends(get_current_actor),
    db: Session = Depends(get_db_session),
):
    """增强审计日志查询，支持多维度筛选"""
    assert_actor_has_role(actor, AgentRole.MANAGER, AgentRole.EXECUTIVE, db=db)

    conditions = ["1=1"]
    params = {}
    if action:
        conditions.append("action = :action")
        params["action"] = action
    if target_type:
        conditions.append("target_type = :target_type")
        params["target_type"] = target_type
    if actor_user_id:
        conditions.append("actor_user_id = (SELECT id FROM users WHERE username = :auid)")
        params["auid"] = actor_user_id

    where = " AND ".join(conditions)

    total = db.execute(text(f"SELECT COUNT(*) FROM audit_logs WHERE {where}"), params).scalar() or 0
    rows = db.execute(text(
        f"SELECT id, action, target_type, target_id, summary, event_at, actor_user_id "
        f"FROM audit_logs WHERE {where} ORDER BY event_at DESC "
        f"LIMIT :limit OFFSET :offset"
    ), {**params, "limit": page_size, "offset": (page - 1) * page_size}).fetchall()

    items = [{
        "id": r[0], "action": r[1], "target_type": r[2],
        "target_id": r[3], "summary": r[4],
        "event_at": str(r[5]), "actor_user_id": r[6],
    } for r in rows]

    return {"code": 200, "data": {"items": items, "total": total, "page": page}, "msg": "ok"}
