import { useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { AlertTriangle, CheckCircle2 } from 'lucide-react'
import { PageHeader } from '../../components/common/PageHeader'
import { useAuth } from '../../contexts/AuthContext'
import { useRunContextStore } from '../../store/useRunContextStore'
import { identityProfiles } from '../../config/identities'

export function StaffReportPage() {
  const { user, token } = useAuth()
  const { runDate } = useRunContextStore()
  const queryClient = useQueryClient()
  const [text, setText] = useState('')
  const [lastResult, setLastResult] = useState<any>(null)
  const [errors, setErrors] = useState<string[]>([])

  const identity = {
    ...identityProfiles.staff,
    userId: user?.username ?? 'zhangsan',
    departmentId: user?.department_id ?? 'dept_mvp_core',
    orgId: user?.org_id ?? 'org_automage_mvp',
  }

  const submit = useMutation({
    mutationFn: async () => {
      const payload = {
        identity: {
          node_id: identity.nodeId,
          user_id: identity.userId,
          role: 'staff',
          level: 'l1_staff',
          department_id: identity.departmentId,
          manager_node_id: identity.managerNodeId,
        },
        report: {
          schema_id: 'schema_v1_staff',
          org_id: identity.orgId,
          department_id: identity.departmentId,
          user_id: identity.userId,
          record_date: runDate,
          work_progress: text,
          issues_faced: [],
          solution_attempt: '',
          need_support: false,
          next_day_plan: '',
          risk_level: 'low',
        },
      }

      const res = await fetch('/api/v1/report/staff', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}`, 'X-User-Id': identity.userId, 'X-Role': 'staff', 'X-Node-Id': identity.nodeId, 'X-Level': 'l1_staff', 'X-Department-Id': identity.departmentId },
        body: JSON.stringify(payload),
      })
      return res.json()
    },
    onSuccess: (data) => {
      setLastResult(data)
      if (data.code === 200) {
        setErrors([])
        queryClient.invalidateQueries({ queryKey: ['staffReports'] })
      } else {
        setErrors([data.msg ?? '提交失败'])
      }
    },
    onError: (err: any) => setErrors([err.message]),
  })

  return (
    <div className="space-y-8">
      <PageHeader title="写日报" description={`运行日 ${runDate} · 用户 ${identity.userId}`} />
      <textarea
        className="input h-36 resize-y"
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="今天完成了什么工作？遇到了什么问题？明天的计划是什么？"
      />
      <button
        type="button"
        onClick={() => submit.mutate()}
        disabled={submit.isPending || !text.trim()}
        className="btn-primary disabled:opacity-40"
      >
        {submit.isPending ? '提交中…' : '提交日报'}
      </button>
      {errors.length > 0 && <p className="text-sm text-rose-600">{errors.join('；')}</p>}
      {lastResult?.code === 200 && (
        <p className="flex items-center gap-2 text-sm text-emerald-700">
          <CheckCircle2 className="h-4 w-4 shrink-0" strokeWidth={2} aria-hidden />
          {lastResult.msg}
        </p>
      )}
      {lastResult?.code === 409 && (
        <p className="flex items-center gap-2 text-sm text-amber-800">
          <AlertTriangle className="h-4 w-4 shrink-0" strokeWidth={2} aria-hidden />
          {lastResult.msg}（今日已提交过）
        </p>
      )}
    </div>
  )
}
