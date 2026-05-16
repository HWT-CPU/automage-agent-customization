import { useWorkflowStore } from '../../store/useWorkflowStore'
import { JsonViewer } from '../common/JsonViewer'

export function DataTraceDrawer() {
  const { selectedNode } = useWorkflowStore()
  if (!selectedNode) return null

  return (
    <aside className="console-panel p-4">
      <p className="console-title">{selectedNode.id} - {selectedNode.title}</p>
      <div className="mt-2 space-y-1 text-sm text-slate-700">
        <p>角色: {selectedNode.role}</p>
        <p>API: {selectedNode.api}</p>
        <p>输出 Schema: {selectedNode.outputSchema ?? 'N/A'}</p>
        <p>读表: {(selectedNode.readTables ?? []).join(', ') || 'N/A'}</p>
        <p>写表: {(selectedNode.writeTables ?? []).join(', ') || 'N/A'}</p>
      </div>
      <div className="mt-3">
        <JsonViewer
          title="最近一次 Trace 占位（M3 接后端后替换）"
          data={{
            request_id: 'generated-in-runtime',
            idempotency_key: 'generated-in-runtime',
            node_status: selectedNode.status,
          }}
        />
      </div>
    </aside>
  )
}
