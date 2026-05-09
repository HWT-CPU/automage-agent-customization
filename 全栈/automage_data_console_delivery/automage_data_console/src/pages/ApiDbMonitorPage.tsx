import { ApiHealthPanel } from '../components/monitor/ApiHealthPanel'
import { ApiLogViewer } from '../components/monitor/ApiLogViewer'
import { IntegrationStatusMatrix } from '../components/monitor/IntegrationStatusMatrix'

export function ApiDbMonitorPage() {
  return (
    <div className="space-y-4">
      <ApiHealthPanel />
      <IntegrationStatusMatrix />
      <ApiLogViewer />
    </div>
  )
}
