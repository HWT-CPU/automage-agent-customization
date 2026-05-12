import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useAuth } from '../../contexts/AuthContext'
import { label, translateValue } from '../../lib/fieldLabels'
import { ChevronDown, ChevronRight, Search, Filter } from 'lucide-react'

export function AuditCenterPage() {
  const { token } = useAuth()
  const [action, setAction] = useState('')
  const [targetType, setTargetType] = useState('')
  const [page, setPage] = useState(1)
  const [expandedId, setExpandedId] = useState<number | null>(null)

  const params = new URLSearchParams()
  if (action) params.set('action', action)
  if (targetType) params.set('target_type', targetType)
  params.set('page', String(page))
  params.set('page_size', '30')

  const { data, isLoading } = useQuery({
    queryKey: ['audit', action, targetType, page],
    queryFn: async () => {
      const res = await fetch(`/api/v1/admin/audit?${params}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      return (await res.json())
    },
    refetchInterval: 30_000,
  })

  const items = data?.data?.items ?? []

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-slate-800">审计中心</h2>
        <div className="flex items-center gap-3">
          <Filter size={14} className="text-slate-400" />
          <select value={action} onChange={e => { setAction(e.target.value); setPage(1) }}
            className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs text-slate-600">
            <option value="">全部操作</option>
            <option value="create">创建</option>
            <option value="update">更新</option>
            <option value="delete">删除</option>
            <option value="dream_run">Dream 运行</option>
          </select>
          <select value={targetType} onChange={e => { setTargetType(e.target.value); setPage(1) }}
            className="rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs text-slate-600">
            <option value="">全部类型</option>
            <option value="tasks">任务</option>
            <option value="work_records">日报</option>
            <option value="summaries">汇总</option>
            <option value="decision_records">决策</option>
            <option value="incidents">异常</option>
          </select>
          <Search size={14} className="text-slate-400" />
        </div>
      </div>

      {isLoading ? (
        <p className="text-sm text-slate-400 py-8 text-center">加载中…</p>
      ) : (
        <div className="rounded-xl border border-slate-100 bg-white overflow-hidden">
          <table className="w-full">
            <thead>
              <tr>
                <th className="table-header px-4 py-3 w-8"></th>
                <th className="table-header px-4 py-3">时间</th>
                <th className="table-header px-4 py-3">操作类型</th>
                <th className="table-header px-4 py-3">目标</th>
                <th className="table-header px-4 py-3">操作人</th>
                <th className="table-header px-4 py-3">描述</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item: any, i: number) => (
                <>
                  <tr key={i} className="audit-row" onClick={() => setExpandedId(expandedId === i ? null : i)}>
                    <td className="px-4 py-3">
                      {expandedId === i ? <ChevronDown size={14} className="text-indigo-500" /> : <ChevronRight size={14} className="text-slate-300" />}
                    </td>
                    <td className="table-cell px-4 text-xs">{item.event_at?.slice(0, 19) ?? '—'}</td>
                    <td className="table-cell px-4">
                      <span className="badge-blue">{label(item.action)}</span>
                    </td>
                    <td className="table-cell px-4 text-xs">{label(item.target_type)} #{item.target_id}</td>
                    <td className="table-cell px-4 text-xs">{item.actor_user_id ?? '系统'}</td>
                    <td className="table-cell px-4 text-xs max-w-xs truncate">{item.summary ?? '—'}</td>
                  </tr>
                  {expandedId === i && (
                    <tr>
                      <td colSpan={6} className="px-4 pb-4">
                        <div className="audit-detail">
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                            {Object.entries(item).filter(([k]) => !['payload'].includes(k)).map(([k, v]) => (
                              <div key={k}>
                                <span className="text-xs text-slate-400">{label(k)}</span>
                                <p className="text-sm text-slate-700 font-medium">{translateValue(v as any)}</p>
                              </div>
                            ))}
                          </div>
                          {item.payload && (
                            <div className="mt-2">
                              <span className="text-xs text-slate-400">{label('payload')}</span>
                              <pre className="mt-1 text-xs text-slate-600 bg-slate-100 rounded-lg p-3 overflow-x-auto max-h-48">
                                {JSON.stringify(item.payload, null, 2)}
                              </pre>
                            </div>
                          )}
                        </div>
                      </td>
                    </tr>
                  )}
                </>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="flex items-center justify-center gap-4 text-sm">
        <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}
          className="btn-secondary text-xs disabled:opacity-30">上一页</button>
        <span className="text-slate-500">第 {page} 页</span>
        <button onClick={() => setPage(p => p + 1)} disabled={items.length < 30}
          className="btn-secondary text-xs disabled:opacity-30">下一页</button>
      </div>
    </div>
  )
}
