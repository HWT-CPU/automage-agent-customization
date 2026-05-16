import { useQuery } from '@tanstack/react-query'
import { useAuth } from '../../contexts/AuthContext'
import { useRunContextStore } from '../../store/useRunContextStore'
import { identityProfiles } from '../../config/identities'
import { label, translateValue } from '../../lib/fieldLabels'
import { PageHeader } from '../../components/common/PageHeader'
import { EmptyState } from '../../components/common/EmptyState'

export function DepartmentOverviewPage() {
  const { user, token } = useAuth()
  const { runDate } = useRunContextStore()
  const mgr = {
    ...identityProfiles.manager,
    userId: user?.username ?? 'lijingli',
    orgId: user?.org_id ?? 'org_automage_mvp',
    departmentId: user?.department_id ?? 'dept_mvp_core',
  }

  const { data: reports, isLoading } = useQuery({
    queryKey: ['staffReports', 'dept', runDate],
    queryFn: async () => {
      const res = await fetch(
        `/api/v1/report/staff?org_id=${mgr.orgId}&department_id=${mgr.departmentId}&record_date=${runDate}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'X-User-Id': mgr.userId,
            'X-Role': 'manager',
            'X-Node-Id': mgr.nodeId,
          },
        },
      )
      return await res.json()
    },
    refetchInterval: 30_000,
  })

  const reportList = (reports?.data?.reports ?? []) as any[]

  return (
    <div className="space-y-8">
      <PageHeader
        title="部门日报"
        description={`运行日 ${runDate} · ${label('department_id')} ${mgr.departmentId}`}
      />

      {isLoading ? (
        <p className="text-sm text-slate-500">加载中…</p>
      ) : reportList.length === 0 ? (
        <EmptyState message="本运行日尚无日报提交。可提醒员工在「写日报」中填报。" />
      ) : (
        <div className="console-panel overflow-hidden">
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
                    <td className="font-medium text-slate-900">{d.user_id ?? r.user_id}</td>
                    <td className="max-w-xs truncate text-slate-700">{d.work_progress ?? '—'}</td>
                    <td>
                      {Array.isArray(d.issues_faced) && d.issues_faced.length > 0 ? (
                        <span className="text-amber-800">{d.issues_faced[0]}</span>
                      ) : d.issues_faced ? (
                        <span className="text-amber-800">{d.issues_faced}</span>
                      ) : (
                        <span className="text-slate-400">—</span>
                      )}
                    </td>
                    <td className="max-w-xs truncate text-slate-700">{d.solution_attempt || '—'}</td>
                    <td className="max-w-xs truncate text-slate-700">{d.next_day_plan || '—'}</td>
                    <td>
                      <span
                        className={`badge ${
                          (d.risk_level ?? 'low') === 'high' || (d.risk_level ?? 'low') === 'critical'
                            ? 'badge-red'
                            : (d.risk_level ?? 'low') === 'medium'
                              ? 'badge-amber'
                              : 'badge-green'
                        }`}
                      >
                        {translateValue(d.risk_level ?? 'low')}
                      </span>
                    </td>
                    <td>
                      {d.need_support ? (
                        <span className="badge-amber">是</span>
                      ) : (
                        <span className="text-slate-400">否</span>
                      )}
                    </td>
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
