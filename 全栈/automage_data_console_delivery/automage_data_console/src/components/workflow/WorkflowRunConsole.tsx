import { useWorkflowStore } from '../../store/useWorkflowStore'

export function WorkflowRunConsole() {
  const { setNodeStatus, resetRun } = useWorkflowStore()

  return (
    <div className="console-panel p-4">
      <p className="console-title mb-3">Workflow Run Console</p>
      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          className="rounded-lg bg-blue-600 px-3 py-2 text-sm text-white"
          onClick={() => {
            setNodeStatus('R0', 'Passed')
            setNodeStatus('S4', 'Running')
            setTimeout(() => setNodeStatus('S4', 'Passed'), 600)
          }}
        >
          一键运行 Demo Workflow
        </button>
        <button
          type="button"
          className="rounded-lg bg-slate-800 px-3 py-2 text-sm text-white"
          onClick={() => {
            setNodeStatus('V0', 'Running')
            setTimeout(() => setNodeStatus('V0', 'Passed'), 500)
          }}
        >
          一键真实 API 冒烟（占位）
        </button>
        <button type="button" className="rounded-lg bg-slate-100 px-3 py-2 text-sm text-slate-700" onClick={resetRun}>
          重置运行状态
        </button>
      </div>
    </div>
  )
}
