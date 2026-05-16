import type { PropsWithChildren } from 'react'
import { Sidebar } from './Sidebar'
import { Topbar } from './Topbar'

export function AppShell({ children }: PropsWithChildren) {
  return (
    <div className="flex min-h-screen bg-slate-100">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col shadow-[inset_1px_0_0_0_rgb(226_232_240)]">
        <Topbar />
        <main className="flex-1 p-6">
          <div className="page-fade mx-auto max-w-[1600px] space-y-8">{children}</div>
        </main>
      </div>
    </div>
  )
}
