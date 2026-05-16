export function RiskAggregationPanel() {
  const risks = [
    'API / 数据库 Skill 端到端读写未验证（high）',
    '真实库新增表与契约主落点待冻结（medium）',
    'manager_cross_dept 当前未拒绝（non-blocking）',
  ]

  return (
    <div className="console-panel p-4">
      <p className="console-title mb-2">风险归并面板</p>
      <ul className="space-y-2 text-sm text-slate-700">
        {risks.map((risk) => (
          <li key={risk} className="rounded-lg bg-rose-50 px-3 py-2 text-rose-700">
            {risk}
          </li>
        ))}
      </ul>
    </div>
  )
}
