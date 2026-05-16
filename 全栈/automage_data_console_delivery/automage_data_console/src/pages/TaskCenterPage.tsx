import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { TaskBoard } from '../components/tasks/TaskBoard'
import { TaskDetailDrawer } from '../components/tasks/TaskDetailDrawer'
import { TaskUpdateForm } from '../components/tasks/TaskUpdateForm'
import { PageHeader } from '../components/common/PageHeader'
import { apiClient } from '../lib/apiClient'
import { useAuth } from '../contexts/AuthContext'
import { normalizeApiTask } from '../lib/taskUtils'

export function TaskCenterPage() {
  const { user } = useAuth()
  const identity = {
    userId: user?.username ?? 'system',
    role: (user?.role ?? 'manager') as 'staff' | 'manager' | 'executive',
    nodeId: 'console',
    level: (user?.level ?? 'l2_manager') as 'l1_staff' | 'l2_manager' | 'l3_executive',
    managerNodeId: '',
    orgId: user?.org_id ?? 'org_automage_mvp',
    departmentId: user?.department_id ?? 'dept_mvp_core',
  }
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
    <div className="space-y-8">
      <PageHeader title="任务中心" description="按权限拉取的任务列表（含团队任务）。仅看指派给您本人的任务请用侧栏「我的任务」。" />

      <div className="grid gap-6 xl:grid-cols-2">
        <div className="space-y-4">
          {q.isLoading ? <p className="text-sm text-slate-500">加载任务…</p> : null}
          {q.isError ? <p className="text-sm text-rose-600">{(q.error as Error).message}</p> : null}
          <TaskBoard tasks={tasks} onSelect={setTaskId} />
          <TaskUpdateForm taskId={taskId} />
        </div>
        <TaskDetailDrawer taskId={taskId} tasks={tasks} />
      </div>
    </div>
  )
}
