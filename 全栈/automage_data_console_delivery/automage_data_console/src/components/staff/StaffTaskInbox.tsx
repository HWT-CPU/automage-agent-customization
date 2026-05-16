import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../../lib/apiClient'
import { useIdentityStore } from '../../store/useIdentityStore'
import { normalizeApiTask } from '../../lib/taskUtils'

export function StaffTaskInbox() {
  const { identity } = useIdentityStore()
  const q = useQuery({
    queryKey: ['tasks', 'inbox', identity.userId, identity.role],
    queryFn: async () => {
      const res = await apiClient.getTasks(identity)
      if (!res.ok) throw new Error(res.msg ?? '任务列表加载失败')
      const list = (res.data as { tasks?: unknown[] })?.tasks ?? []
      return list.map(normalizeApiTask).filter(Boolean) as NonNullable<ReturnType<typeof normalizeApiTask>>[]
    },
    enabled: identity.role === 'staff',
  })

  if (identity.role !== 'staff') {
    return (
      <div className="console-panel p-4">
        <p className="console-title mb-3">我的任务 Inbox</p>
        <p className="text-sm text-slate-600">切换到 Staff 身份后可查看本人任务列表（GET /api/v1/tasks）。</p>
      </div>
    )
  }

  return (
    <div className="console-panel p-4">
      <p className="console-title mb-3">我的任务 Inbox</p>
      {q.isLoading ? <p className="text-sm text-slate-500">加载中…</p> : null}
      {q.isError ? <p className="text-sm text-rose-600">{(q.error as Error).message}</p> : null}
      <div className="space-y-2">
        {(q.data ?? []).map((task) => (
          <div key={task.key} className="rounded-lg bg-slate-50 p-3 text-sm">
            <p className="font-semibold text-slate-900">{task.title}</p>
            <p className="mt-1 text-xs text-slate-600">
              {task.task_id} | {task.status} | {task.priority}
              {task.assignee_user_id ? ` | 执行人 ${task.assignee_user_id}` : ''}
            </p>
          </div>
        ))}
        {!q.isLoading && !q.isError && (q.data?.length ?? 0) === 0 ? (
          <p className="text-sm text-slate-500">暂无任务或列表为空。</p>
        ) : null}
      </div>
    </div>
  )
}
