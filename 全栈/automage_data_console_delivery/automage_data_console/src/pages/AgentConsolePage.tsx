import { useQuery } from '@tanstack/react-query'
import { useAuth } from '../contexts/AuthContext'
import { PageHeader } from '../components/common/PageHeader'
import { RefreshCw, CheckCircle2, AlertCircle } from 'lucide-react'

export function AgentConsolePage() {
  const { token } = useAuth()

  // Scheduler task status
  const { data: tasks } = useQuery({
    queryKey: ['scheduler', 'tasks'],
    queryFn: async () => {
      const res = await fetch('/internal/scheduler/pending', {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) throw new Error('查询失败')
      return res.json()
    },
    refetchInterval: 30_000,
  })

  // System state
  const { data: state } = useQuery({
    queryKey: ['scheduler', 'state'],
    queryFn: async () => {
      const res = await fetch('/internal/scheduler/tick', { method: 'POST', headers: { Authorization: `Bearer ${token}` }})
      if (!res.ok) throw new Error('查询失败')
      return res.json()
    },
    refetchInterval: 120_000,
  })

  const taskList = tasks?.data?.tasks ?? []
  const systemState = state?.data?.state ?? {}

  return (
    <div className="space-y-8">
      <PageHeader title="Agent 控制台" description="调度器任务队列状态 · 墨智执行监控" />

      {/* System State Summary */}
      <div className="grid gap-4 md:grid-cols-4">
        <StateCard label="今日日报" value={String(systemState?.reports ?? '—')} icon={<CheckCircle2 size={16} />} />
        <StateCard label="未提交" value={String(Array.isArray(systemState?.missing) ? systemState.missing.length : '—')} icon={<AlertCircle size={16} />} color="amber" />
        <StateCard label="待汇总" value={String(Array.isArray(systemState?.pending_summaries) ? systemState.pending_summaries.length : '—')} icon={<AlertCircle size={16} />} />
        <StateCard label="待办任务" value={String(taskList.length)} icon={<RefreshCw size={16} />} color={taskList.length > 0 ? 'blue' : 'emerald'} />
      </div>

      {/* Task Queue */}
      <div className="console-panel overflow-hidden">
        <div className="border-b border-slate-100 px-5 py-3">
          <h3 className="text-sm font-semibold text-slate-800">调度器任务队列</h3>
          <p className="text-xs text-slate-400 mt-0.5">墨智每 2 分钟轮询领取任务</p>
        </div>
        {taskList.length === 0 ? (
          <p className="px-5 py-8 text-center text-sm text-slate-400">所有任务已完成，队列为空</p>
        ) : (
          <table className="data-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>类型</th>
                <th>指令摘要</th>
                <th>创建时间</th>
              </tr>
            </thead>
            <tbody>
              {taskList.map((t: any) => (
                <tr key={t.task_id}>
                  <td className="border-b border-slate-100 px-4 py-2.5 text-xs text-slate-500">#{t.task_id}</td>
                  <td className="border-b border-slate-100 px-4 py-2.5 text-xs">
                    <span className="badge-blue">{t.type}</span>
                  </td>
                  <td className="border-b border-slate-100 px-4 py-2.5 text-xs text-slate-600 max-w-md truncate">{t.instruction}</td>
                  <td className="border-b border-slate-100 px-4 py-2.5 text-xs text-slate-400">{t.created_at?.slice(0, 19)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <p className="text-xs text-slate-400">
        墨智 (OpenClaw Agent) — 通过 /internal/scheduler/pending 轮询 · Auto01 — 飞书 App cli_aa8bbf4af4f8dbee · 老板微信 o9cq80
      </p>
    </div>
  )
}

function StateCard({ label, value, icon, color }: any) {
  const c = color === 'amber' ? 'border-l-amber-500' : color === 'rose' ? 'border-l-rose-500' : color === 'blue' ? 'border-l-blue-500' : 'border-l-emerald-500'
  return (
    <div className={`stat-card-accent ${c}`}>
      <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-slate-500">{icon}{label}</div>
      <p className="mt-2 text-xl font-semibold tabular-nums text-slate-900">{value}</p>
    </div>
  )
}

