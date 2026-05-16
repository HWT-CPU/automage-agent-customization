import { ApiHealthPanel } from '../components/monitor/ApiHealthPanel'
import { ApiLogViewer } from '../components/monitor/ApiLogViewer'
import { IntegrationStatusMatrix } from '../components/monitor/IntegrationStatusMatrix'
import { PageHeader } from '../components/common/PageHeader'

export function ApiDbMonitorPage() {
  return (
    <div className="space-y-8">
      <PageHeader
        title="接口与库监控"
        description="健康检查、集成矩阵与请求日志；用于联调与运维观察。"
      />
      <ApiHealthPanel />
      <IntegrationStatusMatrix />
      <ApiLogViewer />
    </div>
  )
}
