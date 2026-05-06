from __future__ import annotations

import base64
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from automage_agents.server.deps import get_db_session
from automage_agents.server.service import import_staff_daily_report_from_markdown, read_staff_daily_report


HTTP_404_RECORD_RESPONSE = {
    404: {
        "description": "指定日报记录不存在",
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
                            "loc": ["body", "org_id"],
                            "msg": "Field required",
                            "input": {
                                "user_id": 3,
                            },
                        }
                    ]
                }
            }
        },
    }
}

IMPORT_MARKDOWN_RESPONSE = {
    200: {
        "description": "Markdown 日报导入成功",
        "content": {
            "application/json": {
                "example": {
                    "code": 200,
                    "data": {
                        "record": {
                            "template_id": 1,
                            "work_record_id": 3,
                            "work_record_public_id": "WRK0000000000000000000003",
                            "item_count": 5,
                            "staff_report_id": 3,
                        }
                    },
                    "msg": "staff daily report imported",
                }
            }
        },
    }
}

GET_STAFF_REPORT_RESPONSE = {
    200: {
        "description": "员工日报读取成功",
        "content": {
            "application/json": {
                "example": {
                    "code": 200,
                    "data": {
                        "work_record_id": 1,
                        "work_record_public_id": "WRK0000000000000000000001",
                        "format": "json",
                        "meta": {
                            "customer_calls": 6,
                            "quotes": 2,
                        },
                        "report": {
                            "title": "张三 5月6日日报",
                            "record_date": "2026-05-06",
                            "items": [
                                {
                                    "field_key": "completed_work",
                                    "field_label": "今日完成",
                                    "value_text": "今日完成3位重点客户跟进，整理2份报价方案。",
                                },
                                {
                                    "field_key": "issues",
                                    "field_label": "遇到问题",
                                    "value_text": "客户关注交付周期，需要确认排期。",
                                },
                            ],
                        },
                    },
                    "msg": "staff daily report loaded",
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


router = APIRouter()


class StaffDailyReportImportRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "markdown": "# 员工日报\n\n- 姓名：张三\n- 日期：2026-05-06\n\n## 今日完成\n- 回访 2 位重点客户\n- 整理 1 份报价说明\n\n## 遇到问题\n- 客户对交付周期还不太放心\n\n## 需要支持\n- 需要经理协助统一交付话术\n\n## 明日计划\n- 继续推进报价确认",
                "org_id": 1,
                "user_id": 3,
                "department_id": 1,
                "created_by": 3,
                "include_staff_report_snapshot": True,
                "snapshot_identity": {
                    "node_id": "staff-node-import-001",
                    "user_id": "3",
                    "role": "staff",
                    "level": "l1_staff",
                    "department_id": "1",
                    "manager_node_id": "manager-node-swagger-001",
                },
                "include_source_markdown": True,
            }
        }
    )

    markdown: str | None = Field(default=None, description="原始 Markdown 日报内容")
    markdown_base64: str | None = Field(default=None, description="Base64 编码的原始 Markdown 字节流")
    org_id: int = Field(description="正式业务表 work_records.org_id")
    user_id: int = Field(description="正式业务表 work_records.user_id")
    department_id: int | None = Field(default=None, description="正式业务表 work_records.department_id")
    created_by: int | None = Field(default=None, description="操作人 ID")
    include_staff_report_snapshot: bool = Field(default=True, description="是否同步写入 staff_reports 快照")
    snapshot_identity: dict[str, str] | None = Field(default=None, description="快照身份信息")
    include_source_markdown: bool = Field(default=True, description="是否保留原始 Markdown 快照")


@router.post(
    "/api/v1/report/staff/import-markdown",
    summary="导入 Markdown 员工日报",
    description="解析 Markdown 员工日报并写入 form_templates、work_records、work_record_items，可选同步 staff_reports。",
    responses=merge_responses(IMPORT_MARKDOWN_RESPONSE, HTTP_422_RESPONSE),
)
def import_staff_daily_report(
    payload: StaffDailyReportImportRequest,
    request: Request,
    db: Session = Depends(get_db_session),
) -> dict[str, Any]:
    if not payload.markdown and not payload.markdown_base64:
        raise HTTPException(status_code=422, detail="markdown or markdown_base64 is required")
    if payload.markdown_base64:
        try:
            base64.b64decode(payload.markdown_base64)
        except Exception as exc:
            raise HTTPException(status_code=422, detail="markdown_base64 is not valid base64") from exc
    data = import_staff_daily_report_from_markdown(
        db,
        markdown=payload.markdown,
        markdown_base64=payload.markdown_base64,
        org_id=payload.org_id,
        user_id=payload.user_id,
        department_id=payload.department_id,
        created_by=payload.created_by,
        include_staff_report_snapshot=payload.include_staff_report_snapshot,
        snapshot_identity=payload.snapshot_identity,
        include_source_markdown=payload.include_source_markdown,
        request_id=getattr(request.state, "request_id", None),
    )
    return {"code": 200, "data": {"record": data}, "msg": "staff daily report imported"}


@router.get(
    "/api/v1/report/staff/{work_record_id}",
    summary="读取并还原员工日报",
    description="按 work_record_id 读取日报，并还原为完整 JSON 或 Markdown。",
    responses=merge_responses(GET_STAFF_REPORT_RESPONSE, HTTP_404_RECORD_RESPONSE, HTTP_422_RESPONSE),
)
def get_staff_daily_report(
    work_record_id: int,
    format: Literal["json", "markdown"] = Query(default="json"),
    db: Session = Depends(get_db_session),
) -> dict[str, Any]:
    data = read_staff_daily_report(db, work_record_id=work_record_id, output_format=format)
    if data is None:
        raise HTTPException(status_code=404, detail="record not found")
    return {"code": 200, "data": data, "msg": "staff daily report loaded"}
