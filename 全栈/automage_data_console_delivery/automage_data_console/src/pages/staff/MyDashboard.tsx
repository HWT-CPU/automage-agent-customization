import { useQuery } from '@tanstack/react-query'
import type { ReactNode } from 'react'
import { AlertCircle, CheckCircle2, ClipboardList, ListTodo } from 'lucide-react'
import { PageHeader } from '../../components/common/PageHeader'
import { useAuth } from '../../contexts/AuthContext'
import { apiClient } from '../../lib/apiClient'
import { useRunContextStore } from '../../store/useRunContextStore'
import { identityProfiles } from '../../config/identities'

export function StaffMyDashboard() {
  const { user } = useAuth()
  const { runDate } = useRunContextStore()

  const staffIdentity = {
    ...identityProfiles.staff,
    userId: user?.username ?? 'zhangsan',
    departmentId: user?.department_id ?? 'dept_mvp_core',
    orgId: user?.org_id ?? 'org_automage_mvp',
  }

  const myReports = useQuery({
    queryKey: ['staffReports', 'my', runDate, user?.username],
    queryFn: async () => {
      const res = await apiClient.getStaffReports(staffIdentity, {
        org_id: staffIdentity.orgId,
        department_id: staffIdentity.departmentId,
        record_date: runDate,
        user_id: staffIdentity.userId,
      })
      if (!res.ok) throw new Error(res.msg ?? '查询日报失败')
      return (res.data as { reports?: unknown[] })?.reports ?? []
    },
  })

  const myTasks = useQuery({
    queryKey: ['tasks', 'my', user?.username],
    queryFn: async () => {
      const res = await apiClient.getTasks(staffIdentity)
      if (!res.ok) throw new Error(res.msg ?? '查询任务失败')
      return (res.data as { tasks?: unknown[] })?.tasks ?? []
    },
  })

  const todayReport = Array.isArray(myReports.data) ? myReports.data[0] : null
  const tasks = Array.isArray(myTasks.data) ? myTasks.data : []
  const pendingTasks = tasks.filter((t: any) => t.status === 'pending' || t.status === 'in_progress')

  return (
    <div className="space-y-8">
      <PageHeader title="我的首页" description="今日日报与任务处理情况一览。" />
      <div className="grid gap-4 md:grid-cols-3">
        <MetricCard
          title="今日日报"
          value={
            todayReport ? (
              <span className="inline-flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-emerald-600" strokeWidth={2} aria-hidden />
                已提交
              </span>
            ) : (
              <span className="inline-flex items-center gap-2">
                <AlertCircle className="h-5 w-5 text-amber-600" strokeWidth={2} aria-hidden />
                未提交
              </span>
            )
          }
          hint={todayReport ? `运行日 ${runDate}` : `请在「写日报」中提交（${runDate}）`}
          accent={todayReport ? 'emerald' : 'amber'}
        />
        <MetricCard
          title="待处理任务"
          value={
            <span className="inline-flex items-center gap-2">
              <ListTodo className="h-5 w-5 text-slate-500" strokeWidth={2} aria-hidden />
              {String(pendingTasks.length)}
            </span>
          }
          hint={pendingTasks.length > 0 ? `${pendingTasks.length} 项待处理` : '暂无待处理'}
          accent={pendingTasks.length > 3 ? 'rose' : 'slate'}
        />
        <MetricCard
          title="任务总量"
          value={
            <span className="inline-flex items-center gap-2">
              <ClipboardList className="h-5 w-5 text-slate-500" strokeWidth={2} aria-hidden />
              {String(tasks.length)}
            </span>
          }
          hint="当前分配给我的全部任务"
          accent="slate"
        />
      </div>
    </div>
  )
}

function MetricCard({
  title,
  value,
  hint,
  accent,
}: {
  title: string
  value: ReactNode
  hint: string
  accent: 'emerald' | 'amber' | 'rose' | 'slate'
}) {
  const bar: Record<string, string> = {
    emerald: 'border-l-emerald-600',
    amber: 'border-l-amber-500',
    rose: 'border-l-rose-600',
    slate: 'border-l-slate-400',
  }
  return (
    <div className={`console-panel border-l-[3px] p-5 ${bar[accent]}`}>
      <p className="text-xs font-medium uppercase tracking-wide text-slate-500">{title}</p>
      <div className="mt-2 text-2xl font-semibold text-slate-900">{value}</div>
      <p className="mt-2 text-xs leading-relaxed text-slate-500">{hint}</p>
    </div>
  )
}
