interface Props {
  incidents: Array<{
    title: string
    source: string
    severity: string
    status: string
    relatedTask: string
    nextAction: string
  }>
}

export function RiskIncidentPanel({ incidents }: Props) {
  return (
    <section className="inset-shell p-5">
      <h3 className="text-xl font-semibold text-slate-900">风险与异常面板</h3>
      <p className="mt-2 text-sm text-slate-600">
        风险可来自 Staff 日报或 Manager 汇总，Dream 会将高风险转换为决策或任务，incident 与 task 可双向关联。
      </p>
      <div className="mt-3 space-y-2">
        {incidents.map((incident) => (
          <div key={incident.title} className="inset-card inset-card-risk p-3">
            <p className="text-sm font-semibold text-rose-700">{incident.title}</p>
            <div className="mt-1 grid gap-1 text-xs text-rose-700 md:grid-cols-3">
              <p>source: {incident.source}</p>
              <p>severity: {incident.severity}</p>
              <p>status: {incident.status}</p>
              <p>related_task: {incident.relatedTask}</p>
              <p className="md:col-span-2">next_action: {incident.nextAction}</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
