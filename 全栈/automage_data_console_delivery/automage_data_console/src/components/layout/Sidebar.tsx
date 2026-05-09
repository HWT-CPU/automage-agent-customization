import { NavLink } from 'react-router-dom'
import { navItems } from '../../config/constants'

export function Sidebar() {
  return (
    <aside className="w-64 shrink-0 border-r border-slate-200/70 bg-white/60 p-4 backdrop-blur">
      <p className="mb-4 text-sm font-semibold text-slate-900">AutoMage-2 Data Console</p>
      <nav className="space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `block rounded-lg px-3 py-2 text-sm ${isActive ? 'bg-blue-100 text-blue-700' : 'text-slate-600 hover:bg-slate-100'}`
            }
            end={item.path === '/'}
          >
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
