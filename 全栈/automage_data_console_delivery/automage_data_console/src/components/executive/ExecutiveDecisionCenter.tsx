import { useMemo, useState } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { identityProfiles } from '../../config/identities'
import { apiClient } from '../../lib/apiClient'
import { buildDecisionCommitBody } from '../../lib/payloadBuilders'
import { useExecutiveSessionStore } from '../../store/useExecutiveSessionStore'
import { ConfirmDialog } from '../common/ConfirmDialog'
import { DecisionCard } from './DecisionCard'

export function ExecutiveDecisionCenter() {
  const exec = identityProfiles.executive
  const { summaryPublicId, lastDreamResult } = useExecutiveSessionStore()
  const queryClient = useQueryClient()
  const [open, setOpen] = useState(false)
  const [pendingOption, setPendingOption] = useState<'A' | 'B' | null>(null)

  const dream = lastDreamResult as Record<string, unknown> | null
  const options = (dream?.decision_options as Array<{ option_id?: string; title?: string; summary?: string }>) ?? []

  const optionSummary = useMemo(
    () =>
      options
        .map((o) => `${o.option_id}: ${o.title ?? ''} — ${o.summary ?? ''}`)
        .join('\n') || '暂无 Dream 输出，请先成功运行 Dream 或切到 Demo 模式查看样例。',
    [options],
  )

  const commit = useMutation({
    mutationFn: async (opt: 'A' | 'B') => {
      if (!summaryPublicId) throw new Error('缺少 summary_public_id：请先完成 Manager 汇总提交或手动在 Dream 面板填写 summary_id。')
      const payload = buildDecisionCommitBody(
        exec,
        summaryPublicId,
        opt,
        'Data Console 决策确认（选项 ' + opt + '）',
        dream,
      )
      return apiClient.commitDecision(payload, exec)
    },
    onSuccess: (res) => {
      setOpen(false)
      setPendingOption(null)
      if (res.ok) void queryClient.invalidateQueries({ queryKey: ['tasks'] })
    },
  })

  return (
    <>
      <DecisionCard
        title="老板决策台（POST /api/v1/decision/commit）"
        content={
          <>
            <p className="text-sm text-slate-600">当前 summary_public_id（来自 Manager 提交或手工维护）：</p>
            <p className="mt-1 font-mono text-sm">{summaryPublicId || '—'}</p>
            <pre className="mt-3 max-h-48 overflow-auto whitespace-pre-wrap rounded-lg bg-slate-50 p-3 text-xs text-slate-700">{optionSummary}</pre>
            {commit.isError ? <p className="mt-2 text-sm text-rose-600">{(commit.error as Error).message}</p> : null}
            {commit.data && !commit.data.ok ? <p className="mt-2 text-sm text-rose-600">{commit.data.msg ?? '提交失败'}</p> : null}
          </>
        }
        actions={
          <>
            <button
              type="button"
              className="rounded-lg bg-emerald-600 px-3 py-2 text-sm text-white"
              onClick={() => {
                setPendingOption('A')
                setOpen(true)
              }}
            >
              确认方案 A
            </button>
            <button
              type="button"
              className="rounded-lg bg-slate-800 px-3 py-2 text-sm text-white"
              onClick={() => {
                setPendingOption('B')
                setOpen(true)
              }}
            >
              确认方案 B
            </button>
          </>
        }
      />
      {commit.data?.ok ? <p className="text-sm text-emerald-700">决策已提交，任务列表已触发刷新。</p> : null}
      <ConfirmDialog
        open={open}
        title="真实写入：决策确认"
        description={`将调用 POST /api/v1/decision/commit，选项 ${pendingOption ?? ''}。载荷结构与验收包一致（identity + decision）。请确认 Real Write 已开启。`}
        onCancel={() => {
          setOpen(false)
          setPendingOption(null)
        }}
        onConfirm={() => pendingOption && commit.mutate(pendingOption)}
      />
    </>
  )
}
