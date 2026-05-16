import { AuditTimeline } from '../components/monitor/AuditTimeline'
import { JsonViewer } from '../components/common/JsonViewer'
import { PageHeader } from '../components/common/PageHeader'

export function AuditPage() {
  return (
    <div className="space-y-8">
      <PageHeader
        title="审计流水"
        description="全局审计时间线与接口占位说明；与「审计中心」合规视图互补。"
      />
      <AuditTimeline />
      <JsonViewer
        title="Audit API 状态"
        data={{
          note: 'Audit API not available yet, using integration logs / demo fallback.',
          source: ['api_logs', 'mock workflow runtime'],
        }}
      />
    </div>
  )
}
