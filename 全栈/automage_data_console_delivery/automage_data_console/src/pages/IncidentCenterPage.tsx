import { IncidentBoard } from '../components/incidents/IncidentBoard'
import { IncidentDetailDrawer } from '../components/incidents/IncidentDetailDrawer'

export function IncidentCenterPage() {
  return (
    <div className="grid gap-4 xl:grid-cols-2">
      <IncidentBoard />
      <IncidentDetailDrawer />
    </div>
  )
}
