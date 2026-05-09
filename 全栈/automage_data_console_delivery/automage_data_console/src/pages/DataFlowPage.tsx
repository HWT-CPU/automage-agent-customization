import { DataTraceDrawer } from '../components/workflow/DataTraceDrawer'
import { WorkflowGraph } from '../components/workflow/WorkflowGraph'
import { WorkflowRunConsole } from '../components/workflow/WorkflowRunConsole'
import { WorkflowStepPanel } from '../components/workflow/WorkflowStepPanel'

export function DataFlowPage() {
  return (
    <div className="grid gap-4 xl:grid-cols-[2fr_1fr]">
      <div className="space-y-4">
        <WorkflowRunConsole />
        <WorkflowGraph />
        <WorkflowStepPanel />
      </div>
      <DataTraceDrawer />
    </div>
  )
}
