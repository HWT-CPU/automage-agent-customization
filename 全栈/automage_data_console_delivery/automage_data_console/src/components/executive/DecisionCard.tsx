import type { ReactNode } from 'react'

export function DecisionCard({ title, content, actions }: { title: string; content: ReactNode; actions: ReactNode }) {
  return (
    <div className="console-panel p-4">
      <p className="text-base font-semibold text-slate-900">{title}</p>
      <div className="mt-2 text-sm text-slate-700">{content}</div>
      <div className="mt-3 flex flex-wrap gap-2">{actions}</div>
    </div>
  )
}
