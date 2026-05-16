import { CalendarDays } from 'lucide-react'
import { useAuth } from '../../contexts/AuthContext'
import { useRunContextStore } from '../../store/useRunContextStore'

export function Topbar() {
  const { user } = useAuth()
  const { runDate, setRunDate } = useRunContextStore()
  const isAdmin = (user?.meta as any)?.is_admin === true
  const roleLabel = isAdmin ? '系统管理员' : user?.role === 'executive' ? '老板' : user?.role === 'manager' ? '部门经理' : '员工'

  return (
    <header className="sticky top-0 z-10 flex h-14 shrink-0 items-center justify-between border-b border-slate-200 bg-white px-6 shadow-sm">
      <div className="min-w-0">
        <p className="truncate text-sm font-medium text-slate-900">{user?.display_name ?? user?.username}</p>
        <p className="text-xs text-slate-500">{roleLabel}</p>
      </div>

      <div className="flex items-center gap-2">
        <span className="hidden h-6 w-px bg-slate-200 sm:block" aria-hidden />
        <label className="flex items-center gap-2 text-xs text-slate-600">
          <CalendarDays className="h-3.5 w-3.5 text-slate-400" strokeWidth={1.75} aria-hidden />
          <span className="whitespace-nowrap">运行日</span>
          <input
            type="date"
            className="rounded border border-slate-300 bg-white px-2 py-1 text-xs text-slate-800 shadow-sm focus:border-slate-500 focus:outline-none focus:ring-1 focus:ring-slate-300"
            value={runDate}
            onChange={(e) => setRunDate(e.target.value)}
          />
        </label>
      </div>
    </header>
  )
}
