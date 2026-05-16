import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useAuth } from '../../contexts/AuthContext'
import { Search, CheckCircle, Clock } from 'lucide-react'

export function StaffManagementPage() {
  const { token } = useAuth()
  const [search, setSearch] = useState('')
  const [page, setPage] = useState(1)

  const { data, isLoading } = useQuery({
    queryKey: ['admin', 'users', search, page],
    queryFn: async () => {
      const params = new URLSearchParams({ page: String(page), page_size: '20' })
      if (search) params.set('search', search)
      const res = await fetch(`/api/v1/admin/users?${params}`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) throw new Error('查询失败')
      return res.json()
    },
  })

  const items = data?.data?.items ?? []
  const total = data?.data?.total ?? 0

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-slate-900">员工管理</h2>

      <div className="flex items-center gap-3">
        <div className="flex flex-1 items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-2">
          <Search size={16} className="text-slate-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1) }}
            placeholder="搜索用户名或姓名..."
            className="flex-1 text-sm outline-none"
          />
        </div>
      </div>

      {isLoading ? (
        <p className="text-sm text-slate-400">加载中…</p>
      ) : (
        <>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-slate-500">
                  <th className="pb-2">用户名</th>
                  <th className="pb-2">姓名</th>
                  <th className="pb-2">角色</th>
                  <th className="pb-2">部门</th>
                  <th className="pb-2">状态</th>
                </tr>
              </thead>
              <tbody>
                {items.map((u: any) => (
                  <tr key={u.id} className="border-b border-slate-100">
                    <td className="py-2 font-medium">{u.username}</td>
                    <td className="py-2">{u.display_name}</td>
                    <td className="py-2">
                      <span className={`status-pill text-xs ${u.role === 'executive' ? 'bg-purple-100 text-purple-700' : u.role === 'manager' ? 'bg-blue-100 text-blue-700' : 'bg-slate-100 text-slate-700'}`}>
                        {u.role}
                      </span>
                    </td>
                    <td className="py-2 text-slate-500">{u.department_id}</td>
                    <td className="py-2">
                      {u.status === 1 ? (
                        <span className="inline-flex items-center gap-1 text-emerald-600"><CheckCircle size={14} /> 正常</span>
                      ) : (
                        <span className="inline-flex items-center gap-1 text-amber-600"><Clock size={14} /> 停用</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="flex items-center justify-between text-sm text-slate-500">
            <span>共 {total} 人</span>
            <div className="flex gap-2">
              <button disabled={page <= 1} onClick={() => setPage(page - 1)} className="rounded px-2 py-1 hover:bg-slate-100 disabled:opacity-30">上一页</button>
              <button disabled={page * 20 >= total} onClick={() => setPage(page + 1)} className="rounded px-2 py-1 hover:bg-slate-100 disabled:opacity-30">下一页</button>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
