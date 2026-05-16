import { useQuery } from '@tanstack/react-query'
import { CheckCircle2, Clock } from 'lucide-react'
import { useAuth } from '../../contexts/AuthContext'
import { identityProfiles } from '../../config/identities'
import { PageHeader } from '../../components/common/PageHeader'
import { EmptyState } from '../../components/common/EmptyState'

export function StaffNotificationsPage() {
  const { user, token } = useAuth()
  const staffIdentity = { ...identityProfiles.staff, userId: user?.username ?? 'zhangsan' }

  const { data, isLoading } = useQuery({
    queryKey: ['notifications', user?.username],
    queryFn: async () => {
      const res = await fetch(`/api/v1/admin/audit?page=1&page_size=20&actor_user_id=${staffIdentity.userId}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) throw new Error('查询失败')
      return res.json()
    },
    refetchInterval: 60_000,
  })

  const items = data?.data?.items ?? []

  return (
    <div className="space-y-8">
      <PageHeader title="通知中心" description="与您相关的审计与系统事件摘要。" />

      {isLoading ? (
        <p className="text-sm text-slate-500">加载中…</p>
      ) : items.length === 0 ? (
        <EmptyState message="暂无与您相关的通知。" />
      ) : (
        <ul className="divide-y divide-slate-100 rounded-lg border border-slate-200 bg-white shadow-sm">
          {items.map((item: any, i: number) => (
            <li key={i} className="flex gap-4 px-4 py-4 transition-colors hover:bg-slate-50/80">
              <span className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-md border border-slate-200 bg-slate-50">
                {item.action?.includes('create') ? (
                  <CheckCircle2 className="h-4 w-4 text-emerald-600" strokeWidth={2} aria-hidden />
                ) : (
                  <Clock className="h-4 w-4 text-slate-500" strokeWidth={2} aria-hidden />
                )}
              </span>
              <div className="min-w-0 flex-1">
                <p className="text-sm font-medium text-slate-900">{item.summary}</p>
                <p className="mt-1 text-xs text-slate-500">
                  {item.event_at?.slice(0, 19)?.replace('T', ' ')} · {item.target_type}
                </p>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
