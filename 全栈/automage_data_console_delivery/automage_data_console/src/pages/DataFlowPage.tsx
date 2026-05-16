import { DataTraceDrawer } from '../components/workflow/DataTraceDrawer'
import { WorkflowGraph } from '../components/workflow/WorkflowGraph'
import { WorkflowRunConsole } from '../components/workflow/WorkflowRunConsole'
import { WorkflowStepPanel } from '../components/workflow/WorkflowStepPanel'
import { PageHeader } from '../components/common/PageHeader'

export function DataFlowPage() {
  return (
    <div className="space-y-8">
      <PageHeader title="数据流转" description="工作流运行轨迹、DAG 与步骤执行视图。" />
      <div className="grid gap-6 xl:grid-cols-[2fr_1fr]">
        <div className="space-y-6">
          <WorkflowRunConsole />
          <WorkflowGraph />
          <WorkflowStepPanel />
        </div>
        <DataTraceDrawer />
      </div>
    </div>
  )
}
