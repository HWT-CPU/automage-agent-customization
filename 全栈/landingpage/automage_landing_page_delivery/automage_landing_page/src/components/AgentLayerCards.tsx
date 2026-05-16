interface AgentCard {
  name: string
  duty: string[]
  output: string[]
  tables: string[]
  apis: string[]
}

interface Props {
  cards: AgentCard[]
}

export function AgentLayerCards({ cards }: Props) {
  return (
    <section className="space-y-4">
      <h2 className="section-title">三层 Agent</h2>
      <p className="text-sm text-slate-600">Staff 产生一线事实，Manager 归并判断，Executive 确认关键选择。</p>
      <div className="grid gap-4 lg:grid-cols-3">
        {cards.map((card) => (
          <article
            key={card.name}
            className="group relative overflow-hidden rounded-2xl border border-slate-200 bg-white p-6 transition-all hover:border-indigo-300 hover:shadow-[0_22px_50px_rgba(30,64,175,0.15)]"
          >
            <div className="pointer-events-none absolute -right-20 -top-16 h-44 w-44 rounded-full bg-indigo-100 transition-colors group-hover:bg-indigo-200/70" />
            <h3 className="relative text-lg font-semibold text-slate-900">{card.name}</h3>
            <div className="relative mt-3 space-y-2 text-sm text-slate-600">
              <p className="text-slate-500">职责</p>
              <ul className="list-disc space-y-1 pl-5">
                {card.duty.map((d) => (
                  <li key={d}>{d}</li>
                ))}
              </ul>
              <p className="pt-2 text-slate-500">输出</p>
              <ul className="list-disc space-y-1 pl-5">
                {card.output.map((o) => (
                  <li key={o}>{o}</li>
                ))}
              </ul>
              <div className="max-h-0 overflow-hidden transition-all duration-300 group-hover:max-h-40">
                <p className="pt-2 text-slate-500">关键 API</p>
                <div className="flex flex-wrap gap-2">
                  {card.apis.map((api) => (
                    <span key={api} className="rounded bg-indigo-50 px-2 py-1 text-xs text-indigo-700">
                      {api}
                    </span>
                  ))}
                </div>
              </div>
              <p className="pt-2 text-slate-500">主要表</p>
              <div className="flex flex-wrap gap-2">
                {card.tables.map((t) => (
                  <span key={t} className="rounded bg-slate-100 px-2 py-1 text-xs text-slate-700">
                    {t}
                  </span>
                ))}
              </div>
            </div>
          </article>
        ))}
      </div>
    </section>
  )
}
