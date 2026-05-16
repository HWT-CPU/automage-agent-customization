import { useWorkflowStore } from '../../store/useWorkflowStore'

export function WorkflowStepPanel() {
  const { nodes } = useWorkflowStore()
  return (
    <div className="console-panel p-4">
      <p className="console-title mb-3">执行步骤列表</p>
      <div className="space-y-2 text-sm">
        {nodes.map((node) => (
          <div key={node.id} className="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-2">
            <p className="text-slate-700">{node.id} · {node.title}</p>
            <span className="text-xs text-slate-500">{node.status}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
