import { NavLink } from 'react-router-dom'
import { LayoutGrid, LogOut } from 'lucide-react'
import { useAuth } from '../../contexts/AuthContext'
import { navItems, navLinkExactEnd } from '../../config/navigation'

export function Sidebar() {
  const { user, logout } = useAuth()
  const role = user?.role ?? 'staff'
  const isAdmin = (user?.meta as any)?.is_admin === true
  const isBoss = role === 'executive' && !isAdmin

  const roleLabel = isAdmin ? '系统管理员' : isBoss ? '老板驾驶舱' : role === 'manager' ? '运营中控台' : '员工工作台'

  const visibleItems = navItems.filter((item) => {
    // 管理员看全部
    if (isAdmin) return true
    // 非管理员排除 adminOnly 项
    if (item.adminOnly) return false
    if (!item.roles || item.roles.length === 0) return true
    // 老板看 executive 标记的项
    if (isBoss) return item.roles.includes('executive')
    return item.roles.includes(role)
  })

  return (
    <aside className="flex w-60 shrink-0 flex-col border-r border-slate-200 bg-white">
      <div className="flex h-14 items-center gap-2 border-b border-slate-200 px-4">
        <NavLink
          to="/"
          className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-slate-900 text-white transition-opacity hover:opacity-90"
          title="运行总览"
          end
        >
          <LayoutGrid className="h-4 w-4" strokeWidth={2} aria-hidden />
        </NavLink>
        <div className="min-w-0">
          <p className="truncate text-sm font-semibold tracking-tight text-slate-900">AutoMage</p>
          <p className="truncate text-xs text-slate-500">{roleLabel}</p>
        </div>
      </div>

      <nav className="flex-1 space-y-0.5 overflow-y-auto p-3">
        {visibleItems.map((item) => {
          const Icon = item.icon
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                [
                  'group flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors',
                  isActive
                    ? 'bg-slate-100 font-medium text-slate-900'
                    : 'font-normal text-slate-600 hover:bg-slate-50 hover:text-slate-900',
                ].join(' ')
              }
              end={navLinkExactEnd(item.path)}
            >
              <Icon
                className="h-4 w-4 shrink-0 text-slate-400 [[aria-current=page]_&]:text-slate-700"
                strokeWidth={1.75}
                aria-hidden
              />
              <span className="truncate">{item.label}</span>
            </NavLink>
          )
        })}
      </nav>

      <div className="border-t border-slate-200 p-3">
        <p className="truncate px-3 pb-2 text-xs text-slate-500">{user?.display_name ?? user?.username}</p>
        <button
          type="button"
          onClick={logout}
          className="flex w-full items-center gap-3 rounded-md px-3 py-2 text-left text-sm text-slate-600 transition-colors hover:bg-slate-50 hover:text-slate-900"
        >
          <LogOut className="h-4 w-4 shrink-0 text-slate-400" strokeWidth={1.75} aria-hidden />
          退出登录
        </button>
      </div>
    </aside>
  )
}
