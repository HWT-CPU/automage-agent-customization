import { useWorkflowStore } from '../../store/useWorkflowStore'
import { StatusBadge } from '../common/StatusBadge'

export function WorkflowGraph() {
  const { nodes, setSelectedNode } = useWorkflowStore()
  return (
    <div className="console-panel p-4">
      <p className="console-title mb-3">DAG 节点轨道</p>
      <div className="grid gap-2 md:grid-cols-2 xl:grid-cols-3">
        {nodes.map((node) => (
          <button
            key={node.id}
            type="button"
            onClick={() => setSelectedNode(node.id)}
            className="rounded-xl bg-slate-50 p-3 text-left hover:bg-blue-50"
          >
            <div className="mb-1 flex items-center justify-between">
              <p className="text-sm font-semibold text-slate-900">
                {node.id} {node.title}
              </p>
              <StatusBadge status={node.status} />
            </div>
            <p className="text-xs text-slate-500">{node.api}</p>
          </button>
        ))}
      </div>
    </div>
  )
}
