import { fmtJson } from '../../lib/format'

export function JsonViewer({ data, title }: { data: unknown; title?: string }) {
  return (
    <div className="console-panel p-4">
      {title ? <p className="mb-2 text-sm font-semibold text-slate-800">{title}</p> : null}
      <pre className="max-h-80 overflow-auto rounded-lg bg-slate-950 p-3 text-xs text-slate-200">{fmtJson(data)}</pre>
    </div>
  )
}
