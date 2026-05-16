import { useQuery } from '@tanstack/react-query'
import { useAuth } from '../../contexts/AuthContext'
import { Server, Database, Activity, HardDrive } from 'lucide-react'

export function SystemMonitorPage() {
  const { token } = useAuth()

  const stats = useQuery({
    queryKey: ['admin', 'system'],
    queryFn: async () => {
      const res = await fetch('/api/v1/admin/stats/system', {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) throw new Error('查询失败')
      return res.json()
    },
    refetchInterval: 15_000,
  })

  const dept = useQuery({
    queryKey: ['admin', 'department'],
    queryFn: async () => {
      const res = await fetch('/api/v1/admin/stats/department', {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) throw new Error('查询失败')
      return res.json()
    },
    refetchInterval: 30_000,
  })

  const sys = stats.data?.data ?? {}
  const dpt = dept.data?.data ?? {}

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-slate-900">系统监控</h2>

      <div className="grid gap-3 md:grid-cols-4">
        <MonitorCard icon={<Activity size={18} />} label="审计日志" value={String(sys.audit_logs ?? '—')} color="blue" />
        <MonitorCard icon={<Server size={18} />} label="Agent 会话" value={String(sys.agent_sessions ?? '—')} color="emerald" />
        <MonitorCard icon={<HardDrive size={18} />} label="任务队列" value={String(sys.task_queue ?? '—')} color="amber" />
        <MonitorCard icon={<Database size={18} />} label="运行模式" value={sys.mode ?? 'production'} color="slate" />
      </div>

      <h3 className="text-md font-semibold text-slate-800 mt-4">部门全景</h3>
      <div className="grid gap-3 md:grid-cols-3">
        <MonitorCard icon={<Database size={18} />} label="员工总数" value={String(dpt.total_users ?? '—')} color="blue" />
        <MonitorCard icon={<Activity size={18} />} label="今日日报" value={String(dpt.reports_today ?? '—')} color="emerald" />
        <MonitorCard icon={<Server size={18} />} label="未关闭异常" value={String(dpt.open_incidents ?? '—')} color={Number(dpt.open_incidents) > 0 ? 'rose' : 'emerald'} />
      </div>

      <h3 className="text-md font-semibold text-slate-800 mt-2">部门分布</h3>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead><tr className="border-b text-left text-slate-500"><th className="pb-2">部门</th><th className="pb-2">人数</th></tr></thead>
          <tbody>
            {(dpt.departments ?? []).map((d: any, i: number) => (
              <tr key={i} className="border-b border-slate-50"><td className="py-2">{d.name}</td><td className="py-2">{d.user_count}</td></tr>
            ))}
          </tbody>
        </table>
      </div>

      <p className="text-xs text-slate-400">后端: {sys.backend ?? 'FastAPI + PostgreSQL + Redis'} | 实时刷新中</p>
    </div>
  )
}

function MonitorCard({ icon, label, value, color }: any) {
  const borders: Record<string, string> = { blue: 'border-l-blue-500', emerald: 'border-l-emerald-500', amber: 'border-l-amber-500', rose: 'border-l-rose-500', slate: 'border-l-slate-400' }
  return (
    <div className={`console-panel rounded-lg border-l-4 p-3 ${borders[color] ?? borders.slate}`}>
      <div className="flex items-center gap-2 text-slate-500">{icon}<span className="text-xs">{label}</span></div>
      <p className="mt-1 text-xl font-semibold text-slate-900">{value}</p>
    </div>
  )
}
