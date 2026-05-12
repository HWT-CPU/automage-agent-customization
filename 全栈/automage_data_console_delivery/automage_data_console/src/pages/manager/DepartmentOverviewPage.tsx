import { useQuery } from '@tanstack/react-query'
import { useAuth } from '../../contexts/AuthContext'
import { useRunContextStore } from '../../store/useRunContextStore'
import { identityProfiles } from '../../config/identities'
import { label, translateValue } from '../../lib/fieldLabels'

export function DepartmentOverviewPage() {
  const { user, token } = useAuth()
  const { runDate } = useRunContextStore()
  const mgr = { ...identityProfiles.manager, userId: user?.username ?? 'lijingli', orgId: user?.org_id ?? 'org_automage_mvp', departmentId: user?.department_id ?? 'dept_mvp_core' }

  const { data: reports, isLoading } = useQuery({
    queryKey: ['staffReports', 'dept', runDate],
    queryFn: async () => {
      const res = await fetch(`/api/v1/report/staff?org_id=${mgr.orgId}&department_id=${mgr.departmentId}&record_date=${runDate}`, {
        headers: { Authorization: `Bearer ${token}`, 'X-User-Id': mgr.userId, 'X-Role': 'manager', 'X-Node-Id': mgr.nodeId },
      })
      return (await res.json())
    },
    refetchInterval: 30_000,
  })

  const reportList = (reports?.data?.reports ?? []) as any[]

  return (
    <div className="space-y-6">
      <div>
        <h2 className="section-title">部门日报</h2>
        <p className="text-sm text-gray-500">日期：{runDate} · {label('department_id')}：{mgr.departmentId}</p>
      </div>

      {isLoading ? <p className="text-sm text-gray-400">加载中…</p> : reportList.length === 0 ? (
        <div className="panel p-8 text-center text-sm text-gray-400">今日暂无日报提交</div>
      ) : (
        <div className="panel overflow-hidden">
          <table className="data-table">
            <thead>
              <tr>
                <th>{label('user_id')}</th>
                <th>{label('work_progress')}</th>
                <th>{label('issues_faced')}</th>
                <th>{label('solution_attempt')}</th>
                <th>{label('next_day_plan')}</th>
                <th>{label('risk_level')}</th>
                <th>{label('need_support')}</th>
              </tr>
            </thead>
            <tbody>
              {reportList.map((r: any, i: number) => {
                const d = r.report ?? r
                return (
                  <tr key={i}>
                    <td className="border-b border-gray-100 px-4 py-2.5 text-sm text-gray-900 font-medium">{d.user_id ?? r.user_id}</td>
                    <td className="border-b border-gray-100 px-4 py-2.5 text-sm text-gray-700 max-w-xs truncate">{d.work_progress ?? '—'}</td>
                    <td className="border-b border-gray-100 px-4 py-2.5 text-sm">
                      {Array.isArray(d.issues_faced) && d.issues_faced.length > 0
                        ? <span className="text-amber-700">{d.issues_faced[0]}</span>
                        : d.issues_faced ? <span className="text-amber-700">{d.issues_faced}</span> : <span className="text-gray-300">—</span>}
                    </td>
                    <td className="border-b border-gray-100 px-4 py-2.5 text-sm text-gray-700 max-w-xs truncate">{d.solution_attempt || '—'}</td>
                    <td className="border-b border-gray-100 px-4 py-2.5 text-sm text-gray-700 max-w-xs truncate">{d.next_day_plan || '—'}</td>
                    <td className="border-b border-gray-100 px-4 py-2.5 text-sm">
                      <span className={`badge ${(d.risk_level ?? 'low') === 'high' || (d.risk_level ?? 'low') === 'critical' ? 'badge-red' : (d.risk_level ?? 'low') === 'medium' ? 'badge-amber' : 'badge-green'}`}>
                        {translateValue(d.risk_level ?? 'low')}
                      </span>
                    </td>
                    <td className="border-b border-gray-100 px-4 py-2.5 text-sm">{d.need_support ? <span className="badge-amber">是</span> : <span className="text-gray-300">否</span>}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
