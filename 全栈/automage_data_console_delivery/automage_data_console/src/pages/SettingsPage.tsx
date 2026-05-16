import { appEnv } from '../config/env'
import { PageHeader } from '../components/common/PageHeader'

export function SettingsPage() {
  return (
    <div className="space-y-8">
      <PageHeader title="系统设置" description="前端环境变量与运行模式（不含密钥）。" />
      <div className="console-panel p-6">
        <dl className="grid gap-3 text-sm text-slate-700 sm:grid-cols-1">
          <div className="flex flex-col gap-0.5 border-b border-slate-100 py-2 last:border-0 sm:flex-row sm:justify-between">
            <dt className="text-slate-500">VITE_AUTOMAGE_API_BASE</dt>
            <dd className="font-mono text-xs text-slate-900 sm:text-right">{appEnv.apiBase}</dd>
          </div>
          <div className="flex flex-col gap-0.5 border-b border-slate-100 py-2 last:border-0 sm:flex-row sm:justify-between">
            <dt className="text-slate-500">VITE_AUTOMAGE_DEMO_MODE</dt>
            <dd className="font-medium text-slate-900">{String(appEnv.demoMode)}</dd>
          </div>
          <div className="flex flex-col gap-0.5 border-b border-slate-100 py-2 last:border-0 sm:flex-row sm:justify-between">
            <dt className="text-slate-500">VITE_AUTOMAGE_ENABLE_REAL_WRITE</dt>
            <dd className="font-medium text-slate-900">{String(appEnv.enableRealWrite)}</dd>
          </div>
          <div className="flex flex-col gap-0.5 border-b border-slate-100 py-2 last:border-0 sm:flex-row sm:justify-between">
            <dt className="text-slate-500">VITE_AUTOMAGE_DEFAULT_ORG_ID</dt>
            <dd className="font-mono text-xs text-slate-900 sm:text-right">{appEnv.defaultOrgId}</dd>
          </div>
          <div className="flex flex-col gap-0.5 py-2 sm:flex-row sm:justify-between">
            <dt className="text-slate-500">VITE_AUTOMAGE_DEFAULT_DEPARTMENT_ID</dt>
            <dd className="font-mono text-xs text-slate-900 sm:text-right">{appEnv.defaultDepartmentId}</dd>
          </div>
        </dl>
        <p className="callout mt-6 text-xs leading-relaxed text-slate-600">
          Token 仅从环境变量读取，不在页面持久化明文展示。生产环境请配合网关与密钥管理策略使用。
        </p>
      </div>
    </div>
  )
}
