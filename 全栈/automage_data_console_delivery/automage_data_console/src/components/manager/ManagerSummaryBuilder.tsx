import { useMemo, useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { JsonViewer } from '../common/JsonViewer'
import { ConfirmDialog } from '../common/ConfirmDialog'
import { apiClient } from '../../lib/apiClient'
import { useIdentityStore } from '../../store/useIdentityStore'
import { useRunContextStore } from '../../store/useRunContextStore'
import { useExecutiveSessionStore } from '../../store/useExecutiveSessionStore'
import { buildManagerReportBody } from '../../lib/payloadBuilders'
import { normalizeStaffTableRow } from '../../lib/taskUtils'
import type { StaffReportRow } from '../../lib/payloadBuilders'

export function ManagerSummaryBuilder() {
  const { identity } = useIdentityStore()
  const { runDate } = useRunContextStore()
  const { setSummaryPublicId } = useExecutiveSessionStore()
  const queryClient = useQueryClient()
  const [confirmOpen, setConfirmOpen] = useState(false)
  const [lastResult, setLastResult] = useState<unknown>(null)

  const staffQuery = useQuery({
    queryKey: ['staffReports', 'manager', runDate, identity.orgId, identity.departmentId],
    queryFn: async () => {
      const res = await apiClient.getStaffReports(identity, {
        org_id: identity.orgId,
        department_id: identity.departmentId,
        record_date: runDate,
      })
      if (!res.ok) throw new Error(res.msg ?? '拉取 Staff 日报失败')
      const raw = (res.data as { reports?: unknown[] })?.reports ?? []
      return raw.map(normalizeStaffTableRow)
    },
    enabled: identity.role === 'manager',
  })

  const draft = useMemo(() => {
    const rows = (staffQuery.data ?? []) as StaffReportRow[]
    const wrList =
      rows
        .map((r) => r.work_record_public_id)
        .filter(Boolean)
        .join(', ') || '（无 work_record_public_id，提交可能被 422）'
    const summaryLine = `部门汇总（${runDate}）：基于 ${rows.length} 条 Staff 日报自动生成；来源 wr = ${wrList}。`
    return buildManagerReportBody(identity, runDate, rows, summaryLine)
  }, [staffQuery.data, identity, runDate])

  const sourceIds = useMemo(() => {
    const rows = (staffQuery.data ?? []) as StaffReportRow[]
    return rows.map((r) => r.work_record_public_id).filter(Boolean)
  }, [staffQuery.data])

  const submit = async () => {
    const res = await apiClient.postManagerReport(draft, identity)
    setLastResult(res)
    setConfirmOpen(false)
    if (res.ok) {
      const record = (res.data as { record?: { summary_public_id?: string } })?.record
      if (record?.summary_public_id) setSummaryPublicId(record.summary_public_id)
      void queryClient.invalidateQueries({ queryKey: ['managerReports', runDate] })
      void staffQuery.refetch()
    }
  }

  if (identity.role !== 'manager') {
    return (
      <div className="console-panel p-4">
        <p className="console-title mb-3">Manager 汇总</p>
        <p className="text-sm text-slate-600">请切换到 Manager 身份后加载本部门 Staff 日报并生成 POST /api/v1/report/manager 载荷。</p>
      </div>
    )
  }

  return (
    <div className="grid gap-3 lg:grid-cols-2">
      <div className="console-panel p-4">
        <p className="console-title mb-3">Manager 汇总生成</p>
        <p className="text-sm text-slate-600">
          先从 API 读取 Staff 日报，再生成与联调验收包一致的 `{'{'} identity, report {'}'}` 提交体。`source_record_ids` 来自列表中的
          `work_record_public_id`。
        </p>
        {staffQuery.isLoading ? <p className="mt-2 text-sm text-slate-500">正在加载 Staff 日报…</p> : null}
        {staffQuery.isError ? <p className="mt-2 text-sm text-rose-600">{(staffQuery.error as Error).message}</p> : null}
        {sourceIds.length === 0 && !staffQuery.isLoading ? (
          <p className="mt-2 text-sm text-amber-800">当前行项缺少 work_record_public_id，直接提交可能导致后端校验失败；请先确保 Staff 已提交且列表字段完整。</p>
        ) : null}
        <button
          type="button"
          className="mt-3 rounded-lg bg-blue-600 px-3 py-2 text-sm text-white"
          onClick={() => void staffQuery.refetch()}
        >
          重新加载 Staff 日报
        </button>
        <button type="button" className="mt-3 ml-2 rounded-lg bg-slate-900 px-3 py-2 text-sm text-white" onClick={() => setConfirmOpen(true)}>
          提交 Manager 汇总（真实写入需确认）
        </button>
        {lastResult ? (
          <p className={`mt-3 text-sm ${(lastResult as { ok?: boolean }).ok ? 'text-emerald-700' : 'text-rose-600'}`}>
            {(lastResult as { ok?: boolean; msg?: string }).ok ? '提交完成，见右侧 JSON。' : (lastResult as { msg?: string }).msg ?? '提交失败'}
          </p>
        ) : null}
      </div>
      <JsonViewer title="POST /api/v1/report/manager 预览" data={draft} />
      <ConfirmDialog
        open={confirmOpen}
        title="真实写入：Manager 汇总"
        description={`将调用 POST /api/v1/report/manager。请确认顶部已开启 Real Write。source_record_ids 数量：${sourceIds.length}。`}
        onCancel={() => setConfirmOpen(false)}
        onConfirm={() => void submit()}
      />
    </div>
  )
}
