import { Inbox } from 'lucide-react'

export function EmptyState({ message }: { message: string }) {
  return (
    <div className="console-panel flex flex-col items-center justify-center gap-3 p-10 text-center">
      <Inbox className="h-10 w-10 text-slate-300" strokeWidth={1.25} aria-hidden />
      <p className="max-w-sm text-sm text-slate-600">{message}</p>
    </div>
  )
}
