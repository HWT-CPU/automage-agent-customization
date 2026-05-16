interface Props {
  timeline: string[]
}

export function AuditTimeline({ timeline }: Props) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5">
      <h3 className="text-xl font-semibold text-slate-900">审计时间线</h3>
      <div className="mt-3 space-y-3">
        {timeline.map((item) => (
          <div key={item} className="flex items-start gap-3">
            <span className="mt-1 h-2.5 w-2.5 rounded-full bg-cyan-300" />
            <p className="text-sm text-slate-600">{item}</p>
          </div>
        ))}
      </div>
    </section>
  )
}
