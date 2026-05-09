import { AuditTimeline } from '../components/monitor/AuditTimeline'
import { JsonViewer } from '../components/common/JsonViewer'

export function AuditPage() {
  return (
    <div className="space-y-4">
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
