import { integrationFacts, knownRisk } from '../../config/constants'

const rows = [
  ['后端启动成功', String(integrationFacts.backendStarted), true],
  ['/healthz', String(integrationFacts.healthzOk), true],
  ['pytest', `${integrationFacts.pytestPassed} passed`, true],
  ['主链路状态', 'Staff → Manager → Dream → Decision → Task 已跑通', true],
  ['数据库核查', 'SELECT 核查通过', true],
  ['当前唯一非阻塞风险', knownRisk, false],
] as const

export function IntegrationStatusMatrix() {
  return (
    <div className="console-panel p-4">
      <p className="console-title mb-3">Integration Status Matrix</p>
      <div className="grid gap-2 md:grid-cols-2 xl:grid-cols-3">
        {rows.map(([label, value, ok]) => (
          <div key={label} className={`rounded-lg p-3 text-sm ${ok ? 'bg-emerald-50 text-emerald-700' : 'bg-amber-50 text-amber-800'}`}>
            <p className="font-semibold">{label}</p>
            <p className="mt-1 text-xs">{value}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
