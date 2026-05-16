import { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { JsonViewer } from '../common/JsonViewer'
import { ConfirmDialog } from '../common/ConfirmDialog'
import { apiClient } from '../../lib/apiClient'
import { identityProfiles } from '../../config/identities'
import { useExecutiveSessionStore } from '../../store/useExecutiveSessionStore'
import { useIdentityStore } from '../../store/useIdentityStore'
import { useRunContextStore } from '../../store/useRunContextStore'
import type { ApiResult } from '../../lib/apiClient'

export function DreamRunPanel() {
  const exec = identityProfiles.executive
  const { role } = useIdentityStore((s) => s.identity)
  const { summaryPublicId, lastDreamResult, setLastDreamResult } = useExecutiveSessionStore()
  const { runDate } = useRunContextStore()
  const [inputId, setInputId] = useState(summaryPublicId)
  const [confirmOpen, setConfirmOpen] = useState(false)
  const [lastCall, setLastCall] = useState<ApiResult | null>(null)

  useEffect(() => {
    if (summaryPublicId) setInputId(summaryPublicId)
  }, [summaryPublicId])

  const loadManager = useQuery({
    queryKey: ['managerReports', runDate, identityProfiles.manager.orgId],
    queryFn: async () => {
      const res = await apiClient.getManagerReports(identityProfiles.manager, {
        org_id: identityProfiles.manager.orgId,
        dept_id: identityProfiles.manager.departmentId,
        summary_date: runDate,
        manager_user_id: identityProfiles.manager.userId,
      })
      if (!res.ok) throw new Error(res.msg ?? '读取 Manager 列表失败')
      return (res.data as { reports?: Array<{ summary_public_id?: string }> })?.reports ?? []
    },
    enabled: role === 'executive' || role === 'manager',
  })

  const run = async () => {
    const res = await apiClient.runDream({ summary_id: inputId }, exec)
    setLastCall(res)
    setConfirmOpen(false)
    if (res.ok) setLastDreamResult(res.data)
  }

  const hintFirst = loadManager.data?.find((r) => r.summary_public_id)?.summary_public_id ?? ''
  const displayData = lastCall?.ok ? lastCall.data : lastDreamResult

  return (
    <div className="grid gap-3 lg:grid-cols-2">
      <div className="console-panel p-4">
        <p className="console-title mb-2">沙箱预演</p>
        <p className="text-sm text-slate-600">
          调用 <code className="text-xs">POST /internal/dream/run</code>，请求体字段 <code className="text-xs">summary_id</code> 与联调验收包一致。请求头使用 Executive 身份（chenzong）。
        </p>
        <label className="mt-3 block text-xs text-slate-600">summary_id（public id）</label>
        <input
          className="mt-1 w-full rounded-lg border border-slate-200 p-2 font-mono text-sm"
          value={inputId}
          onChange={(e) => setInputId(e.target.value)}
          placeholder={hintFirst || 'SUM…'}
        />
        {hintFirst ? (
          <button type="button" className="mt-2 text-xs text-blue-700 underline" onClick={() => setInputId(hintFirst)}>
            填入当日列表首个 summary_public_id：{hintFirst}
          </button>
        ) : null}
        {loadManager.isError ? <p className="mt-2 text-xs text-rose-600">{(loadManager.error as Error).message}</p> : null}
        <button type="button" className="mt-3 rounded-lg bg-blue-600 px-3 py-2 text-sm text-white" onClick={() => setConfirmOpen(true)}>
          触发 Dream（真实写入需确认）
        </button>
        {lastCall && !lastCall.ok ? <p className="mt-2 text-sm text-rose-600">{lastCall.msg ?? 'Dream 调用失败'}</p> : null}
      </div>
      <JsonViewer title="Dream 输出（data 字段）" data={displayData} />
      <ConfirmDialog
        open={confirmOpen}
        title="真实写入：沙箱预演"
        description={`将调用 POST /internal/dream/run，summary_id=${inputId || '（空）'}。请确认顶部已开启 Real Write，且已配置 Token。`}
        onCancel={() => setConfirmOpen(false)}
        onConfirm={() => void run()}
      />
    </div>
  )
}
