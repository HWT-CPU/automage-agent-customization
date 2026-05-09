import type { StaffReportRow } from './payloadBuilders'

export type NormalizedTask = {
  key: string
  task_id: string
  title: string
  description: string
  status: string
  priority: string
  assignee_user_id?: string
  raw: unknown
}

export function normalizeApiTask(row: unknown): NormalizedTask | null {
  if (!row || typeof row !== 'object') return null
  const r = row as Record<string, unknown>
  const task_id = String(r.task_id ?? r.id ?? '')
  if (!task_id) return null
  const title = String(r.title ?? r.task_title ?? '（无标题）')
  const description = String(r.description ?? r.task_description ?? '')
  const status = String(r.status ?? 'unknown')
  const priority = String(r.priority ?? 'medium')
  const assignee_user_id = r.assignee_user_id !== undefined ? String(r.assignee_user_id) : undefined
  return {
    key: `${task_id}-${title}`,
    task_id,
    title,
    description,
    status,
    priority,
    assignee_user_id,
    raw: row,
  }
}

export function normalizeStaffTableRow(row: unknown): StaffReportRow {
  if (!row || typeof row !== 'object') return {}
  const r = row as Record<string, unknown>
  const report = (r.report as Record<string, unknown>) ?? {}
  return {
    user_id: r.user_id as string | undefined,
    work_record_public_id: r.work_record_public_id as string | undefined,
    report: {
      record_date: report.record_date as string | undefined,
      work_progress: report.work_progress as string | undefined,
      risk_level: report.risk_level as string | undefined,
      related_task_ids: report.related_task_ids as string[] | undefined,
    },
  }
}
