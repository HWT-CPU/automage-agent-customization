"""员工入职 API — 自助注册、信息采集、审批激活"""

from __future__ import annotations

import secrets
import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

import bcrypt
from automage_agents.db.models import UserModel
from automage_agents.server.deps import get_db_session

router = APIRouter(prefix="/api/v1/onboarding", tags=["onboarding"])


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=64, description="用户名")
    password: str = Field(..., min_length=4, max_length=128, description="密码")
    display_name: str = Field(..., min_length=1, max_length=128, description="显示姓名")
    phone: str | None = Field(default=None, max_length=32, description="手机号（用于飞书绑定）")
    email: str | None = Field(default=None, max_length=256)
    department_id: str = Field(default="dept_mvp_core", description="部门 ID")
    job_title: str | None = Field(default=None, max_length=128, description="岗位")

    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "newstaff",
                "password": "mypassword",
                "display_name": "新员工",
                "phone": "13800138000",
                "department_id": "dept_mvp_core",
                "job_title": "销售专员",
            }
        }
    }


class OnboardingCompleteRequest(BaseModel):
    collected_info: dict = Field(default_factory=dict, description="墨智采集的员工信息")


@router.post("/register", summary="员工自助注册")
def register(payload: RegisterRequest, db: Session = Depends(get_db_session)):
    """新员工自助注册。初始状态为 pending_onboarding，等待墨智采集信息后激活。"""
    # 检查用户名是否已存在
    existing = db.query(UserModel).filter(
        UserModel.username == payload.username,
        UserModel.deleted_at.is_(None),
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="用户名已存在")

    # 查找组织
    org = db.execute(text("SELECT id FROM organizations LIMIT 1")).fetchone()
    if not org:
        raise HTTPException(status_code=500, detail="未找到组织")
    org_id = org[0]

    # 创建用户
    ph = bcrypt.hashpw(payload.password.encode(), bcrypt.gensalt()).decode()
    public_id = f"usr_{secrets.token_hex(8)}"

    meta = json.dumps({
        "role": "staff",
        "level": "l1_staff",
        "department_id": payload.department_id,
        "job_title": payload.job_title or "",
        "phone": payload.phone or "",
        "onboarding_status": "pending",
    })

    db.execute(text(
        "INSERT INTO users (public_id, org_id, username, display_name, password_hash, email, status, meta) "
        "VALUES (:pid, :oid, :u, :dn, :ph, :em, 1, CAST(:meta AS jsonb))"
    ), {
        "pid": public_id, "oid": org_id,
        "u": payload.username, "dn": payload.display_name,
        "ph": ph, "em": payload.email,
        "meta": meta,
    })
    db.commit()

    # 获取新用户 ID
    new_user = db.execute(text("SELECT id FROM users WHERE username = :u"), {"u": payload.username}).fetchone()

    return {
        "code": 200,
        "data": {
            "user_id": str(new_user[0]),
            "username": payload.username,
            "display_name": payload.display_name,
            "status": "pending_onboarding",
            "message": "注册成功！请等待墨智智能助手联系你完成入职信息采集。",
        },
        "msg": "注册成功",
    }


@router.get("/pending", summary="待入职员工列表")
def pending_onboarding(db: Session = Depends(get_db_session)):
    """Manager 查看待入职员工列表"""
    rows = db.execute(text(
        "SELECT id, username, display_name, meta "
        "FROM users WHERE deleted_at IS NULL AND meta->>'onboarding_status' = 'pending'"
    )).fetchall()

    items = []
    for r in rows:
        meta = r[3] or {}
        items.append({
            "user_id": str(r[0]),
            "username": r[1],
            "display_name": r[2],
            "phone": meta.get("phone", ""),
            "job_title": meta.get("job_title", ""),
            "department_id": meta.get("department_id", ""),
        })

    return {"code": 200, "data": {"items": items, "total": len(items)}, "msg": "ok"}


@router.post("/{user_id}/complete", summary="完成入职")
def complete_onboarding(
    user_id: int,
    payload: OnboardingCompleteRequest,
    db: Session = Depends(get_db_session),
):
    """墨智完成信息采集后调用，将员工状态改为 active"""
    user = db.query(UserModel).filter(UserModel.id == user_id, UserModel.deleted_at.is_(None)).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    current_meta = dict(user.meta or {})
    current_meta["onboarding_status"] = "completed"
    current_meta.update(payload.collected_info)
    new_meta = json.dumps(current_meta)

    db.execute(text(
        "UPDATE users SET meta = CAST(:meta AS jsonb) WHERE id = :uid"
    ), {"meta": new_meta, "uid": user_id})
    db.commit()

    return {"code": 200, "data": {"user_id": str(user_id), "status": "active"}, "msg": "入职完成"}


@router.get("/match", summary="根据信息匹配待入职员工")
def match_pending(
    keyword: str = Query(..., min_length=1, description="姓名或手机号"),
    db: Session = Depends(get_db_session),
):
    """墨智用此接口根据姓名或手机号查找 pending 员工"""
    rows = db.execute(text(
        "SELECT id, username, display_name, meta FROM users "
        "WHERE deleted_at IS NULL AND meta->>'onboarding_status' = 'pending' "
        "AND (display_name LIKE :kw OR username LIKE :kw OR meta->>'phone' LIKE :kw)"
    ), {"kw": f"%{keyword}%"}).fetchall()

    items = []
    for r in rows:
        meta = r[3] or {}
        items.append({
            "user_id": str(r[0]),
            "username": r[1],
            "display_name": r[2],
            "phone": meta.get("phone", ""),
            "job_title": meta.get("job_title", ""),
        })

    return {"code": 200, "data": {"items": items, "total": len(items)}, "msg": "ok"}


@router.get("/check-username", summary="检查用户名可用性")
def check_username(username: str = Query(..., min_length=2), db: Session = Depends(get_db_session)):
    """检查用户名是否已被注册"""
    exists = db.query(UserModel).filter(
        UserModel.username == username,
        UserModel.deleted_at.is_(None),
    ).first()
    return {"code": 200, "data": {"available": exists is None}, "msg": "ok"}
