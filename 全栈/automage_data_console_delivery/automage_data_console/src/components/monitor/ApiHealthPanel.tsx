import { useQuery } from '@tanstack/react-query'
import { integrationFacts, knownRisk } from '../../config/constants'
import { apiClient } from '../../lib/apiClient'
import { useIdentityStore } from '../../store/useIdentityStore'
import { useRuntimeStore } from '../../store/useRuntimeStore'

export function ApiHealthPanel() {
  const { identity } = useIdentityStore()
  const demoMode = useRuntimeStore((s) => s.demoMode)

  const health = useQuery({
    queryKey: ['healthz', 'monitor'],
    queryFn: () => apiClient.healthz(identity),
    enabled: !demoMode,
    refetchInterval: 30_000,
  })

  return (
    <div className="console-panel p-4">
      <p className="console-title mb-3">后端健康检查</p>
      <div className="grid gap-2 text-sm md:grid-cols-2">
        <p>后端启动（项目事实）：{String(integrationFacts.backendStarted)}</p>
        <p>pytest：{integrationFacts.pytestPassed} passed（联调报告）</p>
        <p>
          /healthz 实时探测：
          {demoMode
            ? ' Demo 模式下未请求'
            : health.isLoading
              ? ' 探测中…'
              : health.data?.ok
                ? ` OK（HTTP ${health.data.status}）`
                : ` 失败：${health.data?.msg ?? (health.error instanceof Error ? health.error.message : '未知')}`}
        </p>
        <p>数据库 SELECT 核查：通过（联调报告，前端不直连库）</p>
      </div>
      <p className="mt-3 rounded-lg bg-amber-50 px-3 py-2 text-xs text-amber-800">当前唯一非阻塞风险：{knownRisk}</p>
    </div>
  )
}
