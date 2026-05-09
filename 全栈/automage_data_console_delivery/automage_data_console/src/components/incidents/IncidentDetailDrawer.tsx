import { JsonViewer } from '../common/JsonViewer'

export function IncidentDetailDrawer() {
  return (
    <JsonViewer
      title="异常详情"
      data={{
        incident_id: 'INC-20260506-API-SKILL-001',
        related_task: 'TASK-20260507-BACKEND-001',
        updates: ['2026-05-09 10:40 manager 记录风险', '2026-05-09 11:20 executive 标记为需决策'],
      }}
    />
  )
}
