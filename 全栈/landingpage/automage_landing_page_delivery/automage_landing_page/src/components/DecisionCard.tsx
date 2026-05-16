import { useMemo, useState } from 'react'

interface Props {
  decision: {
    decisionTitle: string
    background: string
    sourceSummary: string
    riskLevel: string
    optionA: string
    optionB: string
    recommendedOption: string
    reasoningSummary: string
    expectedImpact: string
    generatedTasks: string[]
    humanConfirmStatus: string
    confirmedBy: string
    confirmedAt: string
  }
}

export function DecisionCard({ decision }: Props) {
  const [status, setStatus] = useState(decision.humanConfirmStatus)
  const [feedback, setFeedback] = useState('等待老板操作。')

  const actions = useMemo(
    () => [
      { id: 'A', label: '确认方案 A' },
      { id: 'B', label: '确认方案 B' },
      { id: 'MORE', label: '要求补充信息' },
      { id: 'PAUSE', label: '暂不处理' },
    ],
    [],
  )

  const onAction = (action: string) => {
    if (action === 'A' || action === 'B') {
      setStatus('confirmed')
      setFeedback(`已确认方案 ${action}（Demo 状态已更新，可替换为 POST /api/v1/decision/commit）。`)
      return
    }
    setStatus(action === 'MORE' ? 'need_more_info' : 'on_hold')
    setFeedback(action === 'MORE' ? '已标记补充信息请求。' : '已标记暂不处理。')
  }

  return (
    <section id="decision" className="space-y-4 scroll-mt-24">
      <h2 className="section-title">Executive 决策卡片</h2>
      <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-[0_22px_40px_rgba(15,23,42,0.08)]">
        <p className="text-xs text-slate-500">来源 summary：{decision.sourceSummary} ｜ 来源部门：MVP 核心组</p>
        <h3 className="mt-2 text-2xl font-semibold text-slate-900">{decision.decisionTitle}</h3>
        <p className="mt-3 text-sm text-slate-600">{decision.background}</p>

        <div className="mt-4 grid gap-3 md:grid-cols-2">
          <div className="rounded-xl border border-cyan-200 bg-cyan-50 p-3">
            <p className="text-xs text-cyan-700">Option A</p>
            <p className="text-sm text-slate-800">{decision.optionA}</p>
          </div>
          <div className="rounded-xl border border-violet-200 bg-violet-50 p-3">
            <p className="text-xs text-violet-700">Option B</p>
            <p className="text-sm text-slate-800">{decision.optionB}</p>
          </div>
        </div>

        <div className="mt-4 grid gap-2 text-sm text-slate-600 md:grid-cols-2">
          <p>风险等级：{decision.riskLevel}</p>
          <p>推荐方案：{decision.recommendedOption}</p>
          <p>推理摘要：{decision.reasoningSummary}</p>
          <p>预期影响：{decision.expectedImpact}</p>
          <p>确认人：{decision.confirmedBy}</p>
          <p>确认时间：{decision.confirmedAt}</p>
        </div>

        <div className="mt-4">
          <p className="text-xs text-slate-500">生成任务</p>
          <div className="mt-2 flex flex-wrap gap-2">
            {decision.generatedTasks.map((task) => (
              <span key={task} className="rounded bg-emerald-50 px-2 py-1 text-xs text-emerald-700">
                {task}
              </span>
            ))}
          </div>
        </div>

        <div className="mt-5 flex flex-wrap gap-2">
          {actions.map((action) => (
            <button
              key={action.id}
              type="button"
              onClick={() => onAction(action.id)}
              className="rounded-lg border border-slate-300 bg-slate-900 px-3 py-2 text-sm text-white hover:border-slate-900"
            >
              {action.label}
            </button>
          ))}
        </div>

        <p className="mt-3 text-sm text-cyan-700">当前状态：{status} ｜ {feedback}</p>
      </div>
    </section>
  )
}
