interface Props {
  schemaProof: string[]
  apiProof: string[]
  tableProof: string[]
}

export function DataTrustPipeline({ schemaProof, apiProof, tableProof }: Props) {
  return (
    <section id="integration" className="space-y-4 scroll-mt-24">
      <h2 className="section-title">数据可信链路</h2>
      <div className="inset-shell p-6">
        <div className="grid items-start gap-3 md:grid-cols-7">
          <PipelineColumn title="Schema" items={schemaProof} />
          <Arrow />
          <PipelineColumn title="API" items={apiProof} />
          <Arrow />
          <PipelineColumn title="Database" items={tableProof} />
          <Arrow />
          <PipelineColumn title="Audit" items={['audit_logs', 'payload hash', '确认时间', 'actor trace']} />
        </div>
      </div>
    </section>
  )
}

function PipelineColumn({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="inset-card p-4">
      <p className="text-sm font-semibold text-slate-900">{title}</p>
      <ul className="mt-3 space-y-1 text-xs text-slate-600">
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  )
}

function Arrow() {
  return (
    <div className="hidden items-center justify-center text-slate-400 md:flex">
      <span className="text-xl">→</span>
    </div>
  )
}
