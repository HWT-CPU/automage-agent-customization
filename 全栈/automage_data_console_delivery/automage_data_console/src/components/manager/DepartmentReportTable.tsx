import { useQuery } from '@tanstack/react-query'
import { apiClient } from '../../lib/apiClient'
import { useIdentityStore } from '../../store/useIdentityStore'
import { useRunContextStore } from '../../store/useRunContextStore'
import { knownRisk } from '../../config/constants'
import { normalizeStaffTableRow } from '../../lib/taskUtils'

export function DepartmentReportTable() {
  const { identity } = useIdentityStore()
  const { runDate } = useRunContextStore()

  const q = useQuery({
    queryKey: ['staffReports', 'manager', runDate, identity.orgId, identity.departmentId],
    queryFn: async () => {
      const res = await apiClient.getStaffReports(identity, {
        org_id: identity.orgId,
        department_id: identity.departmentId,
        record_date: runDate,
      })
      if (!res.ok) throw new Error(res.msg ?? '本部门 Staff 日报加载失败')
      const raw = (res.data as { reports?: unknown[] })?.reports ?? []
      return raw.map(normalizeStaffTableRow)
    },
    enabled: identity.role === 'manager',
  })

  if (identity.role !== 'manager') {
    return (
      <div className="console-panel p-4">
        <p className="console-title mb-3">本部门日报池</p>
        <p className="text-sm text-slate-600">切换到 Manager 角色后，将使用 GET /api/v1/report/staff 拉取本部门数据（查询参数与联调包一致）。</p>
      </div>
    )
  }

  const rows = q.data ?? []

  return (
    <div className="console-panel p-4">
      <p className="console-title mb-3">本部门日报池</p>
      <p className="mb-2 text-xs text-amber-800">已知风险：{knownRisk}</p>
      {q.isLoading ? <p className="text-sm text-slate-500">加载中…</p> : null}
      {q.isError ? <p className="text-sm text-rose-600">{(q.error as Error).message}</p> : null}
      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="text-xs text-slate-500">
            <tr>
              <th className="pb-2">业务日期</th>
              <th className="pb-2">员工</th>
              <th className="pb-2">work_record_public_id</th>
              <th className="pb-2">进展摘要</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={`${row.user_id}-${row.work_record_public_id ?? row.report?.record_date}`} className="border-t border-slate-200/70">
                <td className="py-2">{row.report?.record_date ?? runDate}</td>
                <td className="py-2">{row.user_id ?? '—'}</td>
                <td className="py-2 font-mono text-xs">{row.work_record_public_id ?? '—'}</td>
                <td className="py-2 max-w-md truncate">{row.report?.work_progress ?? '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {!q.isLoading && !q.isError && rows.length === 0 ? (
        <p className="mt-2 text-sm text-slate-500">当前查询条件下无日报。请确认 record_date、org_id、department_id 与后端数据一致。</p>
      ) : null}
    </div>
  )
}
