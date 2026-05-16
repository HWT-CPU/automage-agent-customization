import type { WorkflowStep } from './demoData'

export const mainLoopNarrative: WorkflowStep[] = [
  { step: 'Staff 日报提交', role: 'Staff Agent', table: 'staff_reports + work_records', api: 'POST /api/v1/report/staff', status: '真实 API 已通' },
  { step: 'Manager 读取并汇总', role: 'Manager Agent', table: 'summaries + summary_source_links', api: 'POST /api/v1/report/manager', status: '真实 API 已通' },
  { step: 'Dream 生成决策卡', role: 'Executive / Dream', table: 'decision_records', api: 'POST /internal/dream/run', status: 'Mock 已通' },
  { step: '老板确认并生成任务', role: 'Executive', table: 'tasks + task_assignments', api: 'POST /api/v1/decision/commit', status: '真实 API 已通' },
  { step: '任务回流日报', role: 'Staff Agent', table: 'task_updates + work_record_items', api: 'GET /api/v1/tasks -> POST /api/v1/report/staff', status: '真实 API 已通' },
]
