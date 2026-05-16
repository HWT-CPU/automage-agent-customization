export const schemaProof = [
  'schema_v1_staff',
  'schema_v1_manager',
  'schema_v1_executive',
  'schema_v1_task',
  'schema_v1_incident',
]

export const apiProof = [
  'POST /api/v1/report/staff',
  'GET /api/v1/report/staff',
  'POST /api/v1/report/manager',
  'GET /api/v1/report/manager',
  'POST /api/v1/decision/commit',
  'GET /api/v1/tasks',
  'POST /internal/dream/run',
  'GET /healthz',
]

export const tableProof = [
  'work_records',
  'work_record_items',
  'summaries',
  'summary_source_links',
  'decision_records',
  'decision_logs',
  'tasks',
  'task_assignments',
  'task_updates',
  'audit_logs',
]

export const integrationProof = [
  'pytest 30 passed',
  '主链路真实 API 通过',
  '数据库 SELECT 核查通过',
  '唯一风险：manager_cross_dept 未拒绝（非阻塞）',
]
