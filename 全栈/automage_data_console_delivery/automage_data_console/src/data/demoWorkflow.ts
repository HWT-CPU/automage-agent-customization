export interface WorkflowNode {
  id: string
  title: string
  role: string
  api: string
  readTables?: string[]
  writeTables?: string[]
  outputSchema?: string
  status: 'Not started' | 'Ready' | 'Running' | 'Passed' | 'Failed' | 'Skipped' | 'Fallback' | 'Needs human confirmation'
}

export const workflowNodes: WorkflowNode[] = [
  { id: 'R0', title: '运行上下文', role: 'System', api: 'N/A', status: 'Passed' },
  { id: 'B1', title: 'Agent 初始化', role: 'System', api: 'POST /api/v1/agent/init', status: 'Ready' },
  { id: 'S0', title: 'Staff 日报录入', role: 'Staff', api: 'UI Input', status: 'Ready' },
  { id: 'S1', title: 'Staff Schema 整理', role: 'Staff Agent', api: 'Adapter Run', outputSchema: 'schema_v1_staff', status: 'Ready' },
  { id: 'S4', title: '提交日报', role: 'Staff', api: 'POST /api/v1/report/staff', writeTables: ['work_records', 'work_record_items'], status: 'Ready' },
  { id: 'V0', title: '后端校验', role: 'Backend', api: 'Schema Validation', status: 'Ready' },
  { id: 'D0', title: '日报事实落库', role: 'Backend', api: 'DB Write', writeTables: ['work_records', 'work_record_items', 'audit_logs'], status: 'Ready' },
  { id: 'I1', title: '高风险异常', role: 'Backend', api: 'POST /api/v1/incidents', writeTables: ['incidents', 'incident_updates'], status: 'Ready' },
  { id: 'M1', title: 'Manager 读取日报', role: 'Manager', api: 'GET /api/v1/report/staff', readTables: ['work_records'], status: 'Ready' },
  { id: 'M3', title: 'Manager Schema', role: 'Manager Agent', api: 'Adapter Run', outputSchema: 'schema_v1_manager', status: 'Ready' },
  { id: 'M5', title: '提交汇总', role: 'Manager', api: 'POST /api/v1/report/manager', writeTables: ['summaries', 'summary_source_links'], status: 'Ready' },
  { id: 'D1', title: '汇总入库', role: 'Backend', api: 'DB Write', writeTables: ['summaries'], status: 'Ready' },
  { id: 'X2', title: 'Dream 归并', role: 'Executive Agent', api: 'POST /internal/dream/run', outputSchema: 'schema_v1_executive', status: 'Ready' },
  { id: 'X5', title: '决策卡片', role: 'Executive', api: 'Decision Preview', status: 'Needs human confirmation' },
  { id: 'H1', title: '老板确认', role: 'Executive', api: 'POST /api/v1/decision/commit', status: 'Needs human confirmation' },
  { id: 'D3', title: '决策落库', role: 'Backend', api: 'DB Write', writeTables: ['decision_records', 'decision_logs'], status: 'Ready' },
  { id: 'T1', title: '生成任务', role: 'Backend', api: 'POST /api/v1/tasks', writeTables: ['tasks', 'task_assignments', 'task_updates'], status: 'Ready' },
  { id: 'T2', title: '分配任务', role: 'Backend', api: 'POST /api/v1/tasks', writeTables: ['task_assignments'], status: 'Ready' },
  { id: 'T3', title: '任务事件', role: 'Staff', api: 'PATCH /api/v1/tasks/{task_id}', writeTables: ['task_updates', 'audit_logs'], status: 'Ready' },
  { id: 'P2', title: '结果进入下一轮日报', role: 'Staff', api: 'GET /api/v1/tasks -> POST /api/v1/report/staff', readTables: ['task_updates'], writeTables: ['work_records'], status: 'Ready' },
]
