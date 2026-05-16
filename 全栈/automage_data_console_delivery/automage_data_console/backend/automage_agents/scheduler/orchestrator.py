"""调度编排引擎 — 检测系统状态，生成任务指令，推送给墨智执行。

职责：
1. 定时检查状态（新日报？待汇总？待决策？）
2. 将待办任务写入 scheduler_tasks 表
3. 墨智通过 /internal/scheduler/pending 轮询领取任务
4. 跟踪执行结果，超时重试，失败告警
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session

from automage_agents.config import load_runtime_settings
from automage_agents.db import create_session_factory
from automage_agents.db.models import (
    DecisionRecordModel,
    SummaryModel,
    WorkRecordModel,
    DepartmentModel,
    UserModel,
)


# Task types
TASK_MANAGER_SUMMARY = "generate_manager_summary"
TASK_DREAM_DECISION = "generate_dream_decision"
TASK_COMMIT_DECISION = "commit_decision"
TASK_PUSH_BOSS = "push_to_boss"


@dataclass
class OrchestratorState:
    """当前系统运行状态快照"""
    check_date: str
    total_staff: int
    submitted_reports: int
    missing_staff: list[str]
    pending_summaries: list[str]  # dept ids that need summaries
    pending_decisions: list[dict]  # summaries that need executive decision
    pending_commits: list[dict]  # decisions needing boss confirmation
    open_tasks: int  # tasks already in scheduler_tasks table


def get_orchestrator_state(db: Session, check_date: str | None = None) -> OrchestratorState:
    """获取当前系统状态快照"""
    if check_date is None:
        check_date = date.today().isoformat()

    # 员工总数
    total_staff = db.execute(
        text("SELECT COUNT(*) FROM users WHERE deleted_at IS NULL")
    ).scalar()

    # 已提交日报数
    submitted = db.execute(
        text(
            "SELECT count(*) FROM work_records "
            "WHERE deleted_at IS NULL AND record_date = :d"
        ),
        {"d": check_date},
    ).scalar() or 0

    # 未提交日报的员工
    all_users = db.execute(
        text("SELECT username FROM users WHERE deleted_at IS NULL")
    ).fetchall()
    submitted_users = {
        r[0]
        for r in db.execute(
            text(
                "SELECT u.username FROM users u "
                "JOIN work_records wr ON wr.user_id = u.id "
                "WHERE wr.record_date = :d AND wr.deleted_at IS NULL"
            ),
            {"d": check_date},
        ).fetchall()
    }
    missing = [r[0] for r in all_users if r[0] not in submitted_users]

    # 需要生成汇总的部门
    existing_summary_depts = {
        r[0]
        for r in db.execute(
            text(
                "SELECT department_id FROM summaries "
                "WHERE deleted_at IS NULL AND summary_date = :d"
            ),
            {"d": check_date},
        ).fetchall()
    }
    pending_summaries = []
    depts = db.query(DepartmentModel).filter(DepartmentModel.deleted_at.is_(None)).all()
    for dept in depts:
        if dept.id not in existing_summary_depts:
            records_today = db.query(WorkRecordModel).filter(
                WorkRecordModel.deleted_at.is_(None),
                WorkRecordModel.record_date == date.fromisoformat(check_date),
                WorkRecordModel.department_id == dept.id,
            ).count()
            if records_today > 0:
                pending_summaries.append({
                    "dept_id": dept.public_id,
                    "dept_name": dept.name,
                    "record_count": records_today,
                })

    # 需要老板决策的汇总
    pending_decisions = []
    summaries = db.execute(
        text(
            "SELECT s.id, s.public_id, s.title, s.meta, d.public_id as dept_pid, d.name as dept_name "
            "FROM summaries s JOIN departments d ON s.department_id = d.id "
            "WHERE s.deleted_at IS NULL AND s.summary_date = :d"
        ),
        {"d": check_date},
    ).fetchall()
    for s in summaries:
        meta = s[3] or {}
        need_exec = meta.get("need_executive_decision") or []
        escalation = meta.get("escalation_required")
        if need_exec or escalation:
            pending_decisions.append({
                "summary_id": s[0],
                "summary_public_id": s[1],
                "title": s[2],
                "dept_id": s[4],
                "dept_name": s[5],
                "overall_health": meta.get("overall_health", "green"),
                "top_3_risks": meta.get("top_3_risks", []),
            })

    # 待老板确认的决策
    pending_commits = []
    decisions = db.execute(
        text(
            "SELECT dr.id, dr.public_id, dr.title, dr.option_schema_json, dr.status "
            "FROM decision_records dr "
            "WHERE dr.deleted_at IS NULL AND dr.selected_option_key IS NULL "
            "ORDER BY dr.id DESC LIMIT 10"
        )
    ).fetchall()
    for d in decisions:
        options = d[3] or []
        if isinstance(options, str):
            try:
                options = json.loads(options)
            except Exception:
                options = []
        if options:
            pending_commits.append({
                "id": d[0],
                "public_id": d[1],
                "title": d[2],
                "options": options,
            })

    # 已存在的调度任务数
    open_tasks = db.execute(
        text("SELECT count(*) FROM scheduler_tasks WHERE status = 'pending'")
    ).scalar() or 0

    return OrchestratorState(
        check_date=check_date,
        total_staff=total_staff or 0,
        submitted_reports=submitted,
        missing_staff=missing,
        pending_summaries=pending_summaries,
        pending_decisions=pending_decisions,
        pending_commits=pending_commits,
        open_tasks=open_tasks,
    )


def ensure_scheduler_tasks_table(db: Session) -> None:
    """确保调度任务表存在"""
    db.execute(text("""
        CREATE TABLE IF NOT EXISTS scheduler_tasks (
            id SERIAL PRIMARY KEY,
            task_type VARCHAR(64) NOT NULL,
            task_data JSONB DEFAULT '{}',
            status VARCHAR(16) DEFAULT 'pending',
            created_at TIMESTAMPTZ DEFAULT NOW(),
            claimed_at TIMESTAMPTZ,
            completed_at TIMESTAMPTZ,
            retry_count INTEGER DEFAULT 0,
            max_retries INTEGER DEFAULT 3,
            result JSONB,
            error_message TEXT,
            instruction TEXT
        )
    """))
    db.commit()


def generate_and_push_tasks(db: Session) -> list[dict]:
    """检查状态并生成新任务，返回创建的任务列表"""
    ensure_scheduler_tasks_table(db)
    state = get_orchestrator_state(db)
    created = []

    # 1. 有未汇总的日报 → 创建 Manager 汇总任务
    if state.submitted_reports > 0 and state.pending_summaries:
        for dept_info in state.pending_summaries:
            # 检查是否已有同类 pending 任务
            existing = db.execute(
                text(
                    "SELECT id FROM scheduler_tasks "
                    "WHERE task_type = :t AND task_data->>'date' = :d "
                    "AND task_data->>'dept_id' = :did AND status IN ('pending','claimed')"
                ),
                {"t": TASK_MANAGER_SUMMARY, "d": state.check_date, "did": dept_info["dept_id"]},
            ).fetchone()
            if existing:
                continue

            instruction = (
                f"请分析 {state.check_date} 部门 {dept_info['dept_name']}({dept_info['dept_id']}) "
                f"的 {dept_info['record_count']} 条员工日报，生成 Manager 汇总。"
                f" | 步骤: 1. GET /api/v1/report/staff?department_id={dept_info['dept_id']}&record_date={state.check_date} "
                f"2. 分析日报提取 overall_health / aggregated_summary / top_3_risks "
                f"3. POST /api/v1/report/manager 提交汇总 "
                f"4. 需要老板决策时生成A/B方案推老板微信"
            )

            db.execute(
                text(
                    "INSERT INTO scheduler_tasks (task_type, task_data, instruction, status) "
                    "VALUES (:t, CAST(:d AS jsonb), :i, 'pending')"
                ),
                {
                    "t": TASK_MANAGER_SUMMARY,
                    "d": json.dumps({"date": state.check_date, "dept_id": dept_info["dept_id"], "record_count": dept_info["record_count"]}),
                    "i": instruction,
                },
            )
            db.commit()
            created.append({"type": TASK_MANAGER_SUMMARY, "dept": dept_info["dept_id"]})

    # 2. 有需要决策的汇总且无待确认决策 → 创建 Dream 决策任务
    if state.pending_decisions and not state.pending_commits:
        for dec in state.pending_decisions:
            existing = db.execute(
                text(
                    "SELECT id FROM scheduler_tasks "
                    "WHERE task_type = :t AND task_data->>'summary_public_id' = :sid AND status IN ('pending','claimed')"
                ),
                {"t": TASK_DREAM_DECISION, "sid": dec["summary_public_id"]},
            ).fetchone()
            if existing:
                continue

            risks_text = " | ".join(f"{r}" for r in dec.get("top_3_risks", [])[:3])
            instruction = (
                f"部门 {dec['dept_name']} 需要老板决策。"
                f"汇总: {dec.get('title', '')} | 健康度: {dec.get('overall_health', 'unknown')}"
                f" | 风险: {risks_text or '无'} | "
                f"生成A/B两个对比方案(方案标题/摘要/任务分解/推荐方案) | "
                f"推送到老板微信 o9cq80-4ZTet7x8h6pGOsyDexBik@im.wechat | "
                f"老板回复A或B后调用 POST /api/v1/decision/commit 落库"
            )

            db.execute(
                text(
                    "INSERT INTO scheduler_tasks (task_type, task_data, instruction, status) "
                    "VALUES (:t, CAST(:d AS jsonb), :i, 'pending')"
                ),
                {
                    "t": TASK_DREAM_DECISION,
                    "d": json.dumps({"summary_public_id": dec["summary_public_id"], "dept_id": dec["dept_id"]}),
                    "i": instruction,
                },
            )
            db.commit()
            created.append({"type": TASK_DREAM_DECISION, "summary": dec["summary_public_id"]})

    # 3. 有未提交日报的员工 → 创建提醒任务
    if state.missing_staff:
        existing = db.execute(
            text(
                "SELECT id FROM scheduler_tasks "
                "WHERE task_type = 'remind_missing_staff' AND task_data->>'date' = :d AND status = 'pending'"
            ),
            {"d": state.check_date},
        ).fetchone()
        if not existing:
            instruction = (
                f"{state.check_date} 以下员工未提交日报: "
                + ", ".join(u for u in state.missing_staff[:20])
                + "。请通过飞书提醒他们提交日报。"
            )
            db.execute(
                text(
                    "INSERT INTO scheduler_tasks (task_type, task_data, instruction, status) "
                    "VALUES (:t, CAST(:d AS jsonb), :i, 'pending')"
                ),
                {
                    "t": "remind_missing_staff",
                    "d": json.dumps({"date": state.check_date, "missing": state.missing_staff}),
                    "i": instruction,
                },
            )
            db.commit()
            created.append({"type": "remind_missing_staff", "count": len(state.missing_staff)})

    return created


# ── Scheduler job entry point ──


def orchestrator_tick(config_path: str = "configs/automage.docker.toml") -> dict:
    """每次 tick 执行：检查状态 → 生成任务。由 cron 线程调用。"""
    settings = load_runtime_settings(config_path)
    factory = create_session_factory(settings.postgres)
    db = factory()
    try:
        state = get_orchestrator_state(db)
        created = generate_and_push_tasks(db)
        return {
            "date": state.check_date,
            "reports": state.submitted_reports,
            "missing": len(state.missing_staff),
            "pending_summaries": len(state.pending_summaries),
            "pending_decisions": len(state.pending_decisions),
            "open_tasks": state.open_tasks + len(created),
            "new_tasks": created,
        }
    finally:
        db.close()
