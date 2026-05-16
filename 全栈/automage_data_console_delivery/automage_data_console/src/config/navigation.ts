import type { LucideIcon } from 'lucide-react'
import {
  Activity,
  BarChart3,
  Bell,
  Brain,
  Bot,
  ClipboardList,
  FileBarChart,
  FileText,
  GitBranch,
  LayoutDashboard,
  ListTodo,
  Network,
  PieChart,
  Server,
  Settings,
  Shield,
  Target,
  Users,
} from 'lucide-react'

type IdentityRole = 'staff' | 'manager' | 'executive'

export interface NavItem {
  label: string
  path: string
  icon: LucideIcon
  roles?: IdentityRole[]
  /** 仅管理员可见（老板不可见） */
  adminOnly?: boolean
}

export function navLinkExactEnd(path: string): boolean {
  return ['/', '/staff', '/manager', '/executive'].includes(path)
}

export const navItems: NavItem[] = [
  // ═══════ 所有人 ═══════
  { label: '运行总览', path: '/', icon: PieChart, roles: ['staff', 'manager', 'executive'] },

  // ═══════ 员工端 ═══════
  { label: '我的首页', path: '/staff', icon: LayoutDashboard, roles: ['staff'] },
  { label: '写日报', path: '/staff/report', icon: FileText, roles: ['staff'] },
  { label: '我的任务', path: '/my-tasks', icon: ListTodo, roles: ['staff', 'executive'] },
  { label: '通知', path: '/staff/notifications', icon: Bell, roles: ['staff'] },

  // ═══════ 老板端（executive, 不含管理员）═══════
  { label: '战略视图', path: '/executive', icon: Target, roles: ['executive'] },
  { label: '决策中心', path: '/executive/decisions', icon: Brain, roles: ['executive'] },
  { label: '决策工作台', path: '/executive/workspace', icon: ClipboardList, roles: ['executive'] },

  // ═══════ 中控台（Manager 可见，管理员也可见）═══════
  { label: '部门全景', path: '/manager', icon: BarChart3, roles: ['manager', 'executive'] },
  { label: '员工管理', path: '/manager/staff', icon: Users, roles: ['manager', 'executive'] },
  { label: '汇总工作台', path: '/manager/reports', icon: FileBarChart, roles: ['manager', 'executive'] },
  { label: '任务中心', path: '/tasks', icon: ClipboardList, roles: ['manager', 'executive'] },
  { label: '异常中心', path: '/incidents', icon: Activity, roles: ['manager', 'executive'] },

  // ═══════ 管理员专属（admin only）═══════
  { label: '数据流转', path: '/data-flow', icon: GitBranch, adminOnly: true },
  { label: '审计中心', path: '/manager/audit', icon: Shield, adminOnly: true },
  { label: '系统监控', path: '/manager/monitor', icon: Network, adminOnly: true },
  { label: '接口与库监控', path: '/api-monitor', icon: Server, adminOnly: true },
  { label: 'Agent 控制台', path: '/agent-console', icon: Bot, adminOnly: true },
  { label: '设置', path: '/settings', icon: Settings, adminOnly: true },
]
