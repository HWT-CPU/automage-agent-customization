import { useState } from 'react'
import { useQueryClient, useMutation } from '@tanstack/react-query'
import { StaffReportComposer } from '../components/staff/StaffReportComposer'
import { StaffReportPreview } from '../components/staff/StaffReportPreview'
import { StaffTaskInbox } from '../components/staff/StaffTaskInbox'
import { ConfirmDialog } from '../components/common/ConfirmDialog'
import { apiClient } from '../lib/apiClient'
import { useIdentityStore } from '../store/useIdentityStore'
import { useRunContextStore } from '../store/useRunContextStore'

export function StaffWorkspacePage() {
  const { identity } = useIdentityStore()
  const { runDate } = useRunContextStore()
  const queryClient = useQueryClient()
  const [snapshot, setSnapshot] = useState<unknown>({})
  const [pendingPayload, setPendingPayload] = useState<Record<string, unknown> | null>(null)
  const [confirmOpen, setConfirmOpen] = useState(false)

  const submitMutation = useMutation({
    mutationFn: (payload: Record<string, unknown>) => apiClient.postStaffReport(payload, identity),
    onSuccess: (res) => {
      setSnapshot(res)
      setConfirmOpen(false)
      setPendingPayload(null)
      void queryClient.invalidateQueries({ queryKey: ['tasks', identity.userId] })
      void queryClient.invalidateQueries({ queryKey: ['staffReports', 'self', runDate] })
      void queryClient.invalidateQueries({ queryKey: ['staffReports', 'manager', runDate] })
    },
  })

  return (
    <div className="space-y-4">
      <StaffReportComposer
        onSubmit={(payload) => {
          setPendingPayload(payload)
          setConfirmOpen(true)
        }}
      />
      <ConfirmDialog
        open={confirmOpen}
        title="真实写入：Staff 日报"
        description="将调用 POST /api/v1/report/staff（载荷含 identity + report）。请确认顶部已开启 Real Write，并已配置有效 Token。"
        onCancel={() => {
          setConfirmOpen(false)
          setPendingPayload(null)
        }}
        onConfirm={() => pendingPayload && submitMutation.mutate(pendingPayload)}
      />
      {submitMutation.isError ? (
        <p className="text-sm text-rose-600">{(submitMutation.error as Error).message}</p>
      ) : null}
      {submitMutation.data && !submitMutation.data.ok ? (
        <p className="text-sm text-rose-600">{submitMutation.data.msg ?? '请求失败'}</p>
      ) : null}
      <div className="grid gap-4 xl:grid-cols-2">
        <StaffTaskInbox />
        <StaffReportPreview payload={snapshot} />
      </div>
    </div>
  )
}
