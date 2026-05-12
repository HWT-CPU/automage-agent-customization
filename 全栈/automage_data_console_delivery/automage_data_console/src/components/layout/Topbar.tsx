import { useAuth } from '../../contexts/AuthContext'
import { useRunContextStore } from '../../store/useRunContextStore'

export function Topbar() {
  const { user, logout } = useAuth()
  const { runDate, setRunDate } = useRunContextStore()

  return (
    <header className="topbar flex items-center justify-between px-6 py-3">
      <div className="flex items-center gap-4">
        <span className="text-sm font-semibold text-gray-900">AutoMage</span>
        <span className="text-xs text-gray-400">|</span>
        <span className="text-xs text-gray-500">{user?.display_name ?? user?.username}</span>
        <span className="badge-blue">{user?.role === 'executive' ? '管理员' : user?.role === 'manager' ? '经理' : '员工'}</span>
      </div>

      <div className="flex items-center gap-3">
        <label className="flex items-center gap-2 text-xs text-gray-500">
          运行日
          <input type="date" className="rounded-md border border-gray-300 px-2 py-1 text-xs" value={runDate} onChange={e => setRunDate(e.target.value)} />
        </label>
        <button onClick={logout} className="btn-ghost text-xs">退出</button>
      </div>
    </header>
  )
}
