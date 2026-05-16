interface Props {
  schemaProof: string[]
  apiProof: string[]
  tableProof: string[]
  integrationProof: string[]
}

export function ApiDatabaseProof({ schemaProof, apiProof, tableProof, integrationProof }: Props) {
  return (
    <section id="integration" className="space-y-4">
      <h2 className="section-title">API / DB / Schema 可信证明</h2>
      <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
        <div className="glass-card rounded-2xl p-4">
          <p className="text-sm text-slate-200">Schema 文件</p>
          <ul className="mt-2 space-y-1 text-xs text-slate-400">
            {schemaProof.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
        <div className="glass-card rounded-2xl p-4">
          <p className="text-sm text-slate-200">核心 API</p>
          <ul className="mt-2 space-y-1 text-xs text-slate-400">
            {apiProof.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
        <div className="glass-card rounded-2xl p-4">
          <p className="text-sm text-slate-200">核心表</p>
          <ul className="mt-2 space-y-1 text-xs text-slate-400">
            {tableProof.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
        <div className="glass-card rounded-2xl p-4">
          <p className="text-sm text-slate-200">联调结论</p>
          <ul className="mt-2 space-y-1 text-xs text-slate-400">
            {integrationProof.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  )
}
