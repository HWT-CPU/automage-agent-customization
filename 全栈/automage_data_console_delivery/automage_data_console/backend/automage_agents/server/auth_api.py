"""Authentication API — JWT-based login / refresh / logout / me."""

from __future__ import annotations

import hashlib
import os
import time
from datetime import datetime, timezone
from typing import Any

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request
import bcrypt
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from automage_agents.config import load_runtime_settings
from automage_agents.db.models import UserModel
from automage_agents.server.deps import get_db_session

_settings = load_runtime_settings("configs/automage.local.toml")

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

# JWT config
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 24 * 3600  # 24 hours
REFRESH_TOKEN_EXPIRE_SECONDS = 7 * 86400  # 7 days


def _jwt_secret() -> str:
    """Derive JWT signing key from auth_token or generate one."""
    token = (_settings.auth_token or "").strip()
    if token:
        return f"automage-jwt-{token}"
    return os.getenv("AUTOMAGE_JWT_SECRET", "automage-jwt-dev-secret-change-me")


def _create_access_token(user: UserModel, role: str, level: str) -> str:
    now = int(time.time())
    payload = {
        "sub": str(user.id),
        "username": user.username,
        "display_name": user.display_name,
        "role": role,
        "level": level,
        "department_id": str(user.meta.get("department_id", "")) if user.meta else "",
        "iat": now,
        "exp": now + ACCESS_TOKEN_EXPIRE_SECONDS,
        "type": "access",
    }
    return jwt.encode(payload, _jwt_secret(), algorithm=JWT_ALGORITHM)


def _create_refresh_token(user_id: int) -> str:
    now = int(time.time())
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + REFRESH_TOKEN_EXPIRE_SECONDS,
        "type": "refresh",
        "jti": hashlib.sha256(os.urandom(32)).hexdigest()[:16],
    }
    return jwt.encode(payload, _jwt_secret(), algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict[str, Any]:
    """Decode and verify a JWT token. Raises on invalid/expired."""
    return jwt.decode(token, _jwt_secret(), algorithms=[JWT_ALGORITHM])


def _resolve_user_role_level(db: Session, user: UserModel) -> tuple[str, str]:
    """Resolve user's role and level from meta or database."""
    meta = user.meta or {}
    role = str(meta.get("role") or "staff")
    level = str(meta.get("level") or "l1_staff")
    return role, level


# --- Pydantic Models ---

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=64)
    password: str = Field(..., min_length=1)

    model_config = {
        "json_schema_extra": {"example": {"username": "zhangsan", "password": "password123"}}
    }


class RefreshRequest(BaseModel):
    refresh_token: str = Field(..., min_length=1)


class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int = ACCESS_TOKEN_EXPIRE_SECONDS
    token_type: str = "bearer"
    user: dict[str, Any]


# --- Endpoints ---

@router.post("/login", response_model=dict, summary="用户登录")
def login(payload: LoginRequest, db: Session = Depends(get_db_session)):
    """Authenticate user and return JWT tokens."""
    user = db.query(UserModel).filter(
        UserModel.username == payload.username,
        UserModel.deleted_at.is_(None),
    ).first()

    if user is None:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    if user.password_hash is None:
        # No password set — check if seed default matches
        if payload.password != "password123":
            raise HTTPException(status_code=401, detail="用户名或密码错误")

    if user.password_hash and not bcrypt.checkpw(payload.password.encode('utf-8'), user.password_hash.encode('utf-8')):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    if user.status != 1:
        raise HTTPException(status_code=403, detail="账户已被禁用")

    role, level = _resolve_user_role_level(db, user)
    access_token = _create_access_token(user, role, level)
    refresh_token = _create_refresh_token(user.id)

    # Update last login
    user.last_login_at = datetime.now(timezone.utc)
    db.commit()

    return {
        "code": 200,
        "data": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": ACCESS_TOKEN_EXPIRE_SECONDS,
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "username": user.username,
                "display_name": user.display_name,
                "role": role,
                "level": level,
                "department_id": str(user.meta.get("department_id", "")) if user.meta else "",
                "org_id": str(user.org_id),
                "meta": dict(user.meta) if user.meta else {},
            },
        },
        "msg": "登录成功",
    }


@router.post("/refresh", response_model=dict, summary="刷新令牌")
def refresh_token(payload: RefreshRequest):
    """Exchange a refresh token for a new access token."""
    try:
        data = decode_token(payload.refresh_token)
        if data.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="无效的刷新令牌")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="刷新令牌已过期")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="无效的刷新令牌")

    return {
        "code": 200,
        "data": {
            "access_token": _create_access_token_from_sub(data["sub"]),
            "expires_in": ACCESS_TOKEN_EXPIRE_SECONDS,
            "token_type": "bearer",
        },
        "msg": "令牌刷新成功",
    }


@router.post("/logout", response_model=dict, summary="退出登录")
def logout():
    """Client-side logout. Refresh tokens are stateless JWT; client should discard."""
    return {"code": 200, "data": None, "msg": "已退出登录"}


# --- Password Reset ---

class ForgotPasswordRequest(BaseModel):
    username: str = Field(..., min_length=1)


class ResetPasswordRequest(BaseModel):
    username: str = Field(..., min_length=1)
    reset_token: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=4)


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=4)


# Simple in-memory reset token store (TTL 15 min)
_reset_tokens: dict[str, tuple[str, float]] = {}


@router.post("/forgot-password", summary="忘记密码")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db_session)):
    """生成密码重置令牌。生产环境中应通过邮件/短信发送。"""
    user = db.query(UserModel).filter(
        UserModel.username == payload.username,
        UserModel.deleted_at.is_(None),
    ).first()
    if user is None:
        # 不暴露用户是否存在
        return {"code": 200, "data": None, "msg": "如果该用户存在，重置令牌已生成"}

    import secrets
    token = secrets.token_urlsafe(32)
    _reset_tokens[payload.username] = (token, time.time() + 900)  # 15 min TTL

    # 同时更新用户 meta 中的 reset_token
    meta = dict(user.meta or {})
    meta["reset_token"] = token
    meta["reset_token_expires"] = time.time() + 900
    user.meta = meta
    db.commit()

    return {
        "code": 200,
        "data": {"reset_token": token},
        "msg": f"重置令牌: {token}（15 分钟有效。生产环境会通过邮件/短信发送）",
    }


@router.post("/reset-password", summary="重置密码")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db_session)):
    """使用重置令牌修改密码"""
    user = db.query(UserModel).filter(
        UserModel.username == payload.username,
        UserModel.deleted_at.is_(None),
    ).first()
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")

    meta = dict(user.meta or {})
    stored_token = meta.get("reset_token", "")
    expires = meta.get("reset_token_expires", 0)

    if not stored_token or stored_token != payload.reset_token:
        raise HTTPException(status_code=403, detail="重置令牌无效")
    if time.time() > expires:
        raise HTTPException(status_code=403, detail="重置令牌已过期")

    user.password_hash = bcrypt.hashpw(payload.new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    meta.pop("reset_token", None)
    meta.pop("reset_token_expires", None)
    user.meta = meta
    db.commit()

    return {"code": 200, "data": None, "msg": "密码已重置，请用新密码登录"}


@router.post("/change-password", summary="修改密码")
def change_password(
    payload: ChangePasswordRequest,
    request: Request,
    db: Session = Depends(get_db_session),
):
    """已登录用户修改密码"""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未提供认证令牌")

    try:
        data = decode_token(auth_header[7:])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        raise HTTPException(status_code=401, detail="令牌无效或已过期")

    user = db.query(UserModel).filter(UserModel.id == int(data["sub"]), UserModel.deleted_at.is_(None)).first()
    if user is None:
        raise HTTPException(status_code=401, detail="用户不存在")

    if user.password_hash and not bcrypt.checkpw(payload.old_password.encode('utf-8'), user.password_hash.encode('utf-8')):
        raise HTTPException(status_code=403, detail="旧密码错误")

    user.password_hash = bcrypt.hashpw(payload.new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    db.commit()

    return {"code": 200, "data": None, "msg": "密码已修改"}


# ---


@router.get("/me", response_model=dict, summary="获取当前用户信息")
def get_me(request: Request, db: Session = Depends(get_db_session)):
    """Return the current authenticated user's profile."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未提供认证令牌")

    try:
        data = decode_token(auth_header[7:])
        if data.get("type") != "access":
            raise HTTPException(status_code=401, detail="无效的访问令牌")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="令牌已过期")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="无效的令牌")

    user = db.query(UserModel).filter(UserModel.id == int(data["sub"])).first()
    if user is None:
        raise HTTPException(status_code=401, detail="用户不存在")

    role, level = _resolve_user_role_level(db, user)
    return {
        "code": 200,
        "data": {
            "id": str(user.id),
            "username": user.username,
            "display_name": user.display_name,
            "role": role,
            "level": level,
            "department_id": data.get("department_id", ""),
            "org_id": str(user.org_id),
        },
        "msg": "ok",
    }


def _create_access_token_from_sub(sub: str) -> str:
    """Create access token from user ID string. User context is minimal."""
    now = int(time.time())
    payload = {
        "sub": sub,
        "iat": now,
        "exp": now + ACCESS_TOKEN_EXPIRE_SECONDS,
        "type": "access",
    }
    return jwt.encode(payload, _jwt_secret(), algorithm=JWT_ALGORITHM)
