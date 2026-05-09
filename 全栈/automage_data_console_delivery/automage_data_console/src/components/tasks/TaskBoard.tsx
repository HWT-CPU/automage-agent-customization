import type { NormalizedTask } from '../../lib/taskUtils'

export function TaskBoard({
  tasks,
  onSelect,
}: {
  tasks: NormalizedTask[]
  onSelect: (taskId: string) => void
}) {
  return (
    <div className="console-panel p-4">
      <div className="mb-3 flex items-center justify-between">
        <p className="console-title">任务看板</p>
        <p className="text-xs text-slate-500">{tasks.length} 条（GET /api/v1/tasks）</p>
      </div>
      <div className="space-y-2">
        {tasks.map((task) => (
          <button key={task.key} className="block w-full rounded-lg bg-slate-50 p-3 text-left text-sm hover:bg-blue-50" onClick={() => onSelect(task.task_id)}>
            <p className="font-semibold text-slate-900">{task.title}</p>
            <p className="mt-1 text-xs text-slate-600">
              {task.task_id} | {task.status} | {task.priority}
            </p>
          </button>
        ))}
        {tasks.length === 0 ? <p className="text-sm text-slate-500">无任务数据。</p> : null}
      </div>
    </div>
  )
}
