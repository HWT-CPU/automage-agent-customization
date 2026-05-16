interface Props {
  summary: {
    summaryDate: string
    department: string
    staffReportCount: number
    missingReportCount: number
    overallHealth: string
    aggregatedSummary: string
    top3Risks: string[]
    blockedItems: string[]
    needExecutiveDecision: string
    nextDayAdjustment: string
  }
}

export function ManagerSummaryPanel({ summary }: Props) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5">
      <h3 className="text-xl font-semibold text-slate-900">Manager 汇总面板</h3>
      <div className="mt-3 grid gap-2 text-sm text-slate-600 md:grid-cols-3">
        <p>汇总日期：{summary.summaryDate}</p>
        <p>部门：{summary.department}</p>
        <p>整体健康度：{summary.overallHealth}</p>
        <p>Staff 日报数：{summary.staffReportCount}</p>
        <p>缺失日报数：{summary.missingReportCount}</p>
        <p>上推状态：已生成老板候选决策</p>
      </div>
      <p className="mt-3 text-sm text-slate-600">{summary.aggregatedSummary}</p>
      <div className="mt-3 grid gap-4 md:grid-cols-3">
        <div>
          <p className="text-xs text-slate-500">Top 3 Risks</p>
          <ul className="list-disc pl-5 text-sm text-slate-700">
            {summary.top3Risks.map((risk) => (
              <li key={risk}>{risk}</li>
            ))}
          </ul>
        </div>
        <div>
          <p className="text-xs text-slate-500">Blocked Items</p>
          <ul className="list-disc pl-5 text-sm text-slate-700">
            {summary.blockedItems.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
        <div>
          <p className="text-xs text-slate-500">Need Executive Decision</p>
          <p className="text-sm text-slate-700">{summary.needExecutiveDecision}</p>
          <p className="mt-2 text-xs text-slate-500">Next Day Adjustment</p>
          <p className="text-sm text-slate-700">{summary.nextDayAdjustment}</p>
        </div>
      </div>
    </section>
  )
}
