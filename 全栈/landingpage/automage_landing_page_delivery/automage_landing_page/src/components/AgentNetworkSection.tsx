import agentVisual from '../assets/agent-network-visual.svg'

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

export function AgentNetworkSection({ cards }: Props) {
  return (
    <section id="agents" className="scroll-mt-24 space-y-7">
      <div className="grid gap-8 lg:grid-cols-[1.1fr_1fr]">
        <div>
          <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Agent Network</p>
          <h2 className="mt-3 text-3xl font-semibold tracking-tight text-slate-900">三层 Agent，不同边界，同一闭环</h2>
          <p className="mt-3 text-sm leading-7 text-slate-600">
            Staff 产生一线事实，Manager 归并与判断，Executive 保留关键确认权。<br />
            每一层只处理其权限内的信息，再将结果传给下一层。
          </p>
          <div className="mt-6 space-y-2 text-sm text-slate-700">
            <p>Staff / Facts Intake</p>
            <p>Manager / Summary Merge</p>
            <p>Executive / Decision &amp; Task Issue</p>
          </div>
        </div>
        <div className="rounded-3xl border border-slate-200 bg-white p-4 shadow-[0_22px_45px_rgba(15,23,42,0.1)]">
          <img src={agentVisual} alt="Agent 网络图" className="w-full rounded-2xl" />
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        {cards.map((card) => (
          <article key={card.name} className="group rounded-3xl border border-slate-200 bg-white p-6 transition hover:border-indigo-300">
            <h3 className="text-lg font-semibold text-slate-900">{card.name}</h3>
            <p className="mt-2 text-sm text-slate-600">{card.duty.slice(0, 3).join(' / ')}</p>
            <p className="mt-4 text-xs text-slate-500">主要输出</p>
            <p className="mt-1 text-sm text-slate-700">{card.output.slice(0, 2).join('、')}</p>
            <div className="mt-4 max-h-0 overflow-hidden transition-all duration-300 group-hover:max-h-40">
              <p className="text-xs text-slate-500">关键 API</p>
              <div className="mt-1 flex flex-wrap gap-2">
                {card.apis.map((api) => (
                  <span key={api} className="rounded bg-indigo-50 px-2 py-1 text-xs text-indigo-700">
                    {api}
                  </span>
                ))}
              </div>
              <p className="mt-3 text-xs text-slate-500">关键表</p>
              <div className="mt-1 flex flex-wrap gap-2">
                {card.tables.slice(0, 3).map((table) => (
                  <span key={table} className="rounded bg-slate-100 px-2 py-1 text-xs text-slate-700">
                    {table}
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
