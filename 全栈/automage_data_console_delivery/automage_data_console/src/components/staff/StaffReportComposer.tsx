import { useState } from 'react'
import { useIdentityStore } from '../../store/useIdentityStore'
import { useRunContextStore } from '../../store/useRunContextStore'
import { buildStaffReportBody, type StaffComposerInput } from '../../lib/payloadBuilders'
import { validateStaffSubmitEnvelope } from '../../lib/schemaValidator'
import { JsonViewer } from '../common/JsonViewer'

interface Props {
  onSubmit: (payload: Record<string, unknown>) => void
}

export function StaffReportComposer({ onSubmit }: Props) {
  const { identity } = useIdentityStore()
  const { runDate } = useRunContextStore()
  const [text, setText] = useState(
    '今日完成 Data Console 与真实 API 载荷对齐；关注 manager_cross_dept 仍未拒绝，里程碑三前需关闭。',
  )
  const [draft, setDraft] = useState<Record<string, unknown>>({})
  const [errors, setErrors] = useState<string[]>([])

  const buildDraft = () => {
    const input: StaffComposerInput = {
      work_progress: text,
      issues_faced: ['manager_cross_dept 当前未拒绝（非阻塞风险，里程碑三前关闭）'],
      solution_attempt: '按 automage_m2_real_api_integration_acceptance 请求体重构前端载荷',
      need_support: false,
      support_detail: '',
      next_day_plan: '继续联调 Staff / Manager / Dream / Decision / Task 全链路',
      risk_level: 'medium',
      employee_comment: '内容由 Data Console 录入，提交体结构与联调验收包一致。',
      related_task_ids: [],
      task_progress: [],
    }
    const body = buildStaffReportBody(identity, runDate, input)
    const result = validateStaffSubmitEnvelope(body as Record<string, unknown>)
    setErrors(result.errors)
    setDraft(body as Record<string, unknown>)
  }

  return (
    <div className="grid gap-3 lg:grid-cols-2">
      <div className="console-panel p-4">
        <p className="console-title mb-2">Staff 日报录入</p>
        <p className="mb-2 text-xs text-slate-500">运行日 {runDate}（与 GET 查询参数 record_date 一致）</p>
        <textarea className="h-40 w-full rounded-lg border border-slate-200 p-3 text-sm" value={text} onChange={(e) => setText(e.target.value)} />
        <div className="mt-3 flex flex-wrap gap-2">
          <button type="button" onClick={buildDraft} className="rounded-lg bg-blue-600 px-3 py-2 text-sm text-white">
            生成 Staff 提交体（identity + report）
          </button>
          <button
            type="button"
            onClick={() => onSubmit(draft)}
            disabled={Object.keys(draft).length === 0}
            className="rounded-lg bg-slate-900 px-3 py-2 text-sm text-white disabled:opacity-40"
          >
            提交 Staff 日报
          </button>
        </div>
        {errors.length > 0 ? <p className="mt-2 text-xs text-rose-600">{errors.join('；')}</p> : null}
      </div>
      <JsonViewer title="POST /api/v1/report/staff 预览（联调结构）" data={draft} />
    </div>
  )
}
