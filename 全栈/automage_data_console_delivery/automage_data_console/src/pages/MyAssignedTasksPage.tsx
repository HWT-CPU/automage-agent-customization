import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { CheckCircle2, CircleDashed, ListTodo } from 'lucide-react'
import { PageHeader } from '../components/common/PageHeader'
import { useAuth } from '../contexts/AuthContext'
import { identityProfiles, type IdentityRole } from '../config/identities'

const COLUMN_META = {
  pending: { label: '待处理', Icon: ListTodo },
  in_progress: { label: '进行中', Icon: CircleDashed },
  done: { label: '已完成', Icon: CheckCircle2 },
} as const

/**
 * 当前登录用户作为 assignee 的任务看板（与「任务中心」全量看板区分）。
 * 员工 / 经理 / 高管均可被指派任务，故统一用登录身份请求 API，不再写死 staff。
 */
export function MyAssignedTasksPage() {
  const { user, token } = useAuth()
  const queryClient = useQueryClient()
  const [updatingId, setUpdatingId] = useState<string | null>(null)

  const role: IdentityRole = user?.role ?? 'staff'
  const profile = identityProfiles[role]
  const userId = user?.username ?? profile.userId
  const nodeId = profile.nodeId

  const { data, isLoading } = useQuery({
    queryKey: ['tasks', 'mine', userId, role],
    queryFn: async () => {
      const res = await fetch(`/api/v1/tasks?assignee_user_id=${encodeURIComponent(userId)}`, {
        headers: {
          Authorization: `Bearer ${token}`,
          'X-User-Id': userId,
          'X-Role': role,
          'X-Node-Id': nodeId,
        },
      })
      if (!res.ok) throw new Error('查询失败')
      return res.json()
    },
    refetchInterval: 30_000,
  })

  const updateTask = useMutation({
    mutationFn: async ({ taskId, status }: { taskId: string; status: string }) => {
      const res = await fetch(`/api/v1/tasks/${encodeURIComponent(taskId)}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
          'X-User-Id': userId,
          'X-Role': role,
          'X-Node-Id': nodeId,
        },
        body: JSON.stringify({ status }),
      })
      if (!res.ok) throw new Error('更新失败')
      return res.json()
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['tasks', 'mine'] }),
  })

  const tasks = (data?.data?.tasks ?? []) as any[]
  const grouped = {
    pending: tasks.filter((t: any) => t.status === 'pending' || t.status === 'not_started'),
    in_progress: tasks.filter((t: any) => t.status === 'in_progress' || t.status === 'doing'),
    done: tasks.filter((t: any) => t.status === 'done' || t.status === 'completed'),
  }

  return (
    <div className="space-y-8">
      <PageHeader
        title="我的任务"
        description="仅展示指派给您本人的任务；部门/全局任务请在「任务中心」查看。"
      />
      {isLoading ? (
        <p className="text-sm text-slate-500">加载中…</p>
      ) : (
        <div className="grid gap-4 lg:grid-cols-3">
          {(['pending', 'in_progress', 'done'] as const).map((col) => {
            const { label, Icon } = COLUMN_META[col]
            return (
              <div key={col} className="flex flex-col rounded-md border border-slate-200 bg-white shadow-sm">
                <div className="flex items-center gap-2 border-b border-slate-100 px-4 py-3">
                  <Icon className="h-4 w-4 text-slate-500" strokeWidth={1.75} aria-hidden />
                  <p className="text-sm font-semibold text-slate-800">
                    {label}
                    <span className="ml-2 font-normal text-slate-500">({grouped[col].length})</span>
                  </p>
                </div>
                <div className="space-y-2 p-3">
                  {grouped[col].map((task: any) => (
                    <div
                      key={task.task_id ?? task.public_id}
                      className="rounded-md border border-slate-100 bg-slate-50/80 p-3"
                    >
                      <p className="text-sm font-medium text-slate-900">{task.title ?? task.task_title}</p>
                      <p className="mt-1 text-xs leading-relaxed text-slate-600">{task.description ?? task.task_description}</p>
                      <p className="mt-2 text-xs">
                        <span
                          className={`status-pill ${
                            task.priority === 'high' || task.priority === 'critical'
                              ? 'border border-rose-200 bg-rose-50 text-rose-800'
                              : 'border border-slate-200 bg-white text-slate-700'
                          }`}
                        >
                          {task.priority ?? 'medium'}
                        </span>
                      </p>
                      {col !== 'done' && (
                        <button
                          type="button"
                          onClick={() => {
                            setUpdatingId(task.task_id ?? task.public_id)
                            updateTask.mutate(
                              {
                                taskId: task.task_id ?? task.public_id,
                                status: col === 'pending' ? 'in_progress' : 'done',
                              },
                              { onSettled: () => setUpdatingId(null) },
                            )
                          }}
                          disabled={updatingId === (task.task_id ?? task.public_id)}
                          className="btn-primary mt-3 px-3 py-1.5 text-xs"
                        >
                          {col === 'pending' ? '开始' : '完成'}
                        </button>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
