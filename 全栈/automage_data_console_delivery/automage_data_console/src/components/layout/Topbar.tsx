import { useQuery } from '@tanstack/react-query'
import { AlertTriangle, Database, ShieldCheck } from 'lucide-react'
import { knownRisk } from '../../config/constants'
import { apiClient } from '../../lib/apiClient'
import { useIdentityStore } from '../../store/useIdentityStore'
import { useRuntimeStore } from '../../store/useRuntimeStore'
import { useRunContextStore } from '../../store/useRunContextStore'
import { RoleSwitcher } from './RoleSwitcher'

export function Topbar() {
  const { identity } = useIdentityStore()
  const { demoMode, enableRealWrite, setDemoMode, setEnableRealWrite } = useRuntimeStore()
  const { runDate, setRunDate } = useRunContextStore()

  const health = useQuery({
    queryKey: ['healthz', 'top'],
    queryFn: () => apiClient.healthz(identity),
    refetchInterval: 45_000,
  })

  const healthLabel = demoMode
    ? 'Demo（未请求真实 /healthz）'
    : health.isLoading
      ? '检查中…'
      : health.data?.ok
        ? '真实 /healthz：正常'
        : `异常：${health.data?.msg ?? (health.error instanceof Error ? health.error.message : String(health.error ?? '未知'))}`

  return (
    <header className="console-panel mb-4 p-4">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="space-y-1">
          <p className="text-lg font-semibold text-slate-900">AutoMage-2 数据中台 / 组织运行控制台</p>
          <p className="text-xs text-slate-600">
            org={identity.orgId} | dept={identity.departmentId} | user={identity.userId}
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <label className="flex items-center gap-2 text-xs text-slate-600">
            运行日
            <input type="date" className="rounded border border-slate-200 px-2 py-1 text-sm" value={runDate} onChange={(e) => setRunDate(e.target.value)} />
          </label>
          <RoleSwitcher />
          <button
            type="button"
            onClick={() => setDemoMode(!demoMode)}
            className={`status-pill ${demoMode ? 'bg-amber-100 text-amber-800' : 'bg-emerald-100 text-emerald-700'}`}
          >
            {demoMode ? 'Demo Mode' : 'Real API Mode'}
          </button>
          <button
            type="button"
            onClick={() => setEnableRealWrite(!enableRealWrite)}
            className={`status-pill ${enableRealWrite ? 'bg-rose-100 text-rose-700' : 'bg-slate-100 text-slate-700'}`}
          >
            Real Write {enableRealWrite ? 'ON' : 'OFF'}
          </button>
        </div>
      </div>
      <div className="mt-3 grid gap-2 md:grid-cols-3">
        <p className="status-pill bg-emerald-100 text-emerald-700 inline-flex items-center gap-1">
          <ShieldCheck size={14} /> {healthLabel}
        </p>
        <p className="status-pill bg-blue-100 text-blue-700 inline-flex items-center gap-1">
          <Database size={14} /> pytest: 30 passed（联调报告）
        </p>
        <p className="status-pill bg-amber-100 text-amber-800 inline-flex items-center gap-1">
          <AlertTriangle size={14} /> {knownRisk}
        </p>
      </div>
    </header>
  )
}
