interface Props {
  healthOk: boolean
  pytestPassed: number
  risk: string
}

const statusItems = (healthOk: boolean, pytestPassed: number, risk: string) => [
  { label: '后端启动成功', value: '通过', ok: true },
  { label: '/healthz', value: healthOk ? '正常' : '异常', ok: healthOk },
  { label: 'pytest', value: `${pytestPassed} passed`, ok: true },
  { label: '主链路状态', value: 'Staff -> Manager -> Dream -> Decision -> Task 已跑通', ok: true },
  { label: '数据库核查', value: 'SELECT 核查通过', ok: true },
  { label: '非阻塞风险', value: risk, ok: false },
]

export function IntegrationStatusMatrix({ healthOk, pytestPassed, risk }: Props) {
  return (
    <section id="integration-status" className="space-y-4 scroll-mt-24">
      <h2 className="section-title">真实联调状态</h2>
      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
        {statusItems(healthOk, pytestPassed, risk).map((item) => (
          <div
            key={item.label}
            className={`inset-card p-4 ${item.ok ? 'inset-card-ok' : 'inset-card-risk'}`}
          >
            <p className="text-sm font-semibold text-slate-900">{item.label}</p>
            <p className={`mt-2 text-sm ${item.ok ? 'text-emerald-700' : 'text-rose-700'}`}>{item.value}</p>
          </div>
        ))}
      </div>
      <p className="text-sm text-slate-600">非阻塞风险：manager_cross_dept 当前未拒绝，里程碑三前关闭。</p>
    </section>
  )
}
