import { IncidentBoard } from '../components/incidents/IncidentBoard'
import { IncidentDetailDrawer } from '../components/incidents/IncidentDetailDrawer'
import { PageHeader } from '../components/common/PageHeader'

export function IncidentCenterPage() {
  return (
    <div className="space-y-8">
      <PageHeader title="异常中心" description="跟踪未闭环事件与处理进度。" />
      <div className="grid gap-6 xl:grid-cols-2">
        <IncidentBoard />
        <IncidentDetailDrawer />
      </div>
    </div>
  )
}
