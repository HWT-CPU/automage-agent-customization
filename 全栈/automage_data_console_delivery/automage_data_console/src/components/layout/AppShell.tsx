import type { PropsWithChildren } from 'react'
import { Sidebar } from './Sidebar'
import { Topbar } from './Topbar'

export function AppShell({ children }: PropsWithChildren) {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="min-w-0 flex-1 p-4">
        <Topbar />
        <main className="space-y-4">{children}</main>
      </div>
    </div>
  )
}
