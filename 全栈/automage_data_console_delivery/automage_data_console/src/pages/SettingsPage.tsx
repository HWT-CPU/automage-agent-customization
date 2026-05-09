import { appEnv } from '../config/env'

export function SettingsPage() {
  return (
    <div className="console-panel p-4">
      <p className="console-title mb-3">设置 / 环境配置</p>
      <div className="grid gap-2 text-sm text-slate-700">
        <p>VITE_AUTOMAGE_API_BASE: {appEnv.apiBase}</p>
        <p>VITE_AUTOMAGE_DEMO_MODE: {String(appEnv.demoMode)}</p>
        <p>VITE_AUTOMAGE_ENABLE_REAL_WRITE: {String(appEnv.enableRealWrite)}</p>
        <p>VITE_AUTOMAGE_DEFAULT_ORG_ID: {appEnv.defaultOrgId}</p>
        <p>VITE_AUTOMAGE_DEFAULT_DEPARTMENT_ID: {appEnv.defaultDepartmentId}</p>
      </div>
      <p className="mt-3 text-xs text-slate-500">Token 仅从环境变量读取，不在页面存储、不在日志明文显示。</p>
    </div>
  )
}
