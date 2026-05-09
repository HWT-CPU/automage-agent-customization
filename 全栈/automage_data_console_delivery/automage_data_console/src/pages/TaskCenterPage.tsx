import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { TaskBoard } from '../components/tasks/TaskBoard'
import { TaskDetailDrawer } from '../components/tasks/TaskDetailDrawer'
import { TaskUpdateForm } from '../components/tasks/TaskUpdateForm'
import { apiClient } from '../lib/apiClient'
import { useIdentityStore } from '../store/useIdentityStore'
import { normalizeApiTask } from '../lib/taskUtils'

export function TaskCenterPage() {
  const { identity } = useIdentityStore()
  const [taskId, setTaskId] = useState<string>()

  const q = useQuery({
    queryKey: ['tasks', 'center', identity.userId, identity.role],
    queryFn: async () => {
      const res = await apiClient.getTasks(identity)
      if (!res.ok) throw new Error(res.msg ?? '任务列表加载失败')
      const list = (res.data as { tasks?: unknown[] })?.tasks ?? []
      return list.map(normalizeApiTask).filter((t): t is NonNullable<typeof t> => Boolean(t))
    },
  })

  const tasks = q.data ?? []

  return (
    <div className="grid gap-4 xl:grid-cols-2">
      <div className="space-y-4">
        {q.isLoading ? <p className="text-sm text-slate-500">加载任务…</p> : null}
        {q.isError ? <p className="text-sm text-rose-600">{(q.error as Error).message}</p> : null}
        <TaskBoard tasks={tasks} onSelect={setTaskId} />
        <TaskUpdateForm taskId={taskId} />
      </div>
      <TaskDetailDrawer taskId={taskId} tasks={tasks} />
    </div>
  )
}
