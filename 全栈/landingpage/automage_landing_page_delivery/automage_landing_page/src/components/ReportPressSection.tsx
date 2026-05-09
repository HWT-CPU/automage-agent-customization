const pieces = ['sheet', 'roll', 'sheet', 'roll', 'sheet', 'roll', 'sheet', 'sheet', 'sheet', 'sheet', 'sheet', 'roll'] as const

export function ReportPressSection() {
  return (
    <section className="space-y-4">
      <div className="flex items-end justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Narrative Transition</p>
          <h2 className="text-2xl font-semibold tracking-tight text-slate-900 md:text-3xl">事件压印为可交付凭证</h2>
        </div>
        <p className="max-w-lg text-sm text-slate-600">这段动画用于承接 Audit Timeline 和联调状态：事件不是停在日志，而是变成可验证的交付证据。</p>
      </div>

      <div className="report-press">
        {pieces.map((piece, index) => (
          <div key={`${piece}-${index}`} className={piece} />
        ))}
      </div>
    </section>
  )
}
