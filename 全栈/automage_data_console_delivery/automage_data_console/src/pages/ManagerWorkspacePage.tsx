import { DepartmentReportTable } from '../components/manager/DepartmentReportTable'
import { ManagerSummaryBuilder } from '../components/manager/ManagerSummaryBuilder'
import { RiskAggregationPanel } from '../components/manager/RiskAggregationPanel'

export function ManagerWorkspacePage() {
  return (
    <div className="space-y-4">
      <DepartmentReportTable />
      <ManagerSummaryBuilder />
      <RiskAggregationPanel />
    </div>
  )
}
