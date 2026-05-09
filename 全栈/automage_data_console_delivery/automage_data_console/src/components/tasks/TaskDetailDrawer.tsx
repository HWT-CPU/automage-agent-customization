import { JsonViewer } from '../common/JsonViewer'
import type { NormalizedTask } from '../../lib/taskUtils'

export function TaskDetailDrawer({ taskId, tasks }: { taskId?: string; tasks: NormalizedTask[] }) {
  const task = tasks.find((item) => item.task_id === taskId)
  if (!taskId || !task) return null
  return <JsonViewer title={`任务详情 ${task.task_id}`} data={task.raw} />
}
