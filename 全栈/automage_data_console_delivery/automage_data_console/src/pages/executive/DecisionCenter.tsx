import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { useAuth } from '../../contexts/AuthContext'
import { identityProfiles } from '../../config/identities'
import { useRunContextStore } from '../../store/useRunContextStore'
import { Check, ChevronDown, ChevronRight } from 'lucide-react'
import { PageHeader } from '../../components/common/PageHeader'

export function DecisionCenter() {
  const { user, token } = useAuth()
  const { runDate } = useRunContextStore()
  const execIdentity = { ...identityProfiles.executive, userId: user?.username ?? 'chenzong', orgId: user?.org_id ?? 'org_automage_mvp' }
  const [expandedOption, setExpandedOption] = useState<string | null>(null)
  const [dreamResult, setDreamResult] = useState<any>(null)
  const [dreamLoading, setDreamLoading] = useState(false)

  const { data: summaries, isLoading } = useQuery({
    queryKey: ['managerReports', 'decision', runDate],
    queryFn: async () => {
      const res = await fetch(`/api/v1/report/manager?summary_date=${runDate}`, {
        headers: { Authorization: `Bearer ${token}`, 'X-User-Id': execIdentity.userId, 'X-Role': 'executive', 'X-Node-Id': execIdentity.nodeId },
      })
      if (!res.ok) throw new Error('查询失败')
      return res.json()
    },
    refetchInterval: 60_000,
  })

  const runDream = async (summaryId: string) => {
    setDreamLoading(true)
    try {
      const res = await fetch('/internal/dream/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}`, 'X-User-Id': execIdentity.userId, 'X-Role': 'executive', 'X-Node-Id': execIdentity.nodeId },
        body: JSON.stringify({ summary_id: summaryId }),
      })
      setDreamResult((await res.json()).data ?? null)
    } finally { setDreamLoading(false) }
  }

  const commitDecision = useMutation({
    mutationFn: async (decision: any) => {
      const res = await fetch('/api/v1/decision/commit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}`, 'X-User-Id': execIdentity.userId, 'X-Role': 'executive', 'X-Node-Id': execIdentity.nodeId },
        body: JSON.stringify({ identity: { node_id: execIdentity.nodeId, user_id: execIdentity.userId, role: 'executive', level: 'l3_executive' }, decision }),
      })
      return res.json()
    },
  })

  const reports = (summaries?.data?.reports ?? []) as any[]

  const healthColor = (h: string) => h === 'red' ? 'text-rose-600' : h === 'yellow' ? 'text-amber-600' : 'text-emerald-600'

  return (
    <div className="space-y-8">
      <PageHeader title="决策中心" description={`基于运行日 ${runDate} 的 Manager 汇总，生成与确认决策方案。`} />
      {isLoading ? (
        <p className="text-sm text-slate-500">加载汇总中…</p>
      ) : reports.length === 0 ? (
        <p className="callout text-sm text-slate-600">暂无汇总数据（{runDate}）</p>
      ) : (
        <div className="space-y-4">
          {reports.map((r: any, i: number) => (
            <div key={i} className="console-panel p-5">
              <p className="font-medium text-slate-900">
                健康度:{' '}
                <span className={healthColor(r.overall_health ?? r.report?.overall_health ?? 'green')}>
                  {r.overall_health ?? r.report?.overall_health ?? '—'}
                </span>
              </p>
              <p className="mt-2 text-sm leading-relaxed text-slate-600">{r.aggregated_summary ?? r.report?.aggregated_summary}</p>
              <button
                type="button"
                onClick={() => runDream(r.summary_public_id ?? r.public_id)}
                disabled={dreamLoading}
                className="btn-secondary mt-4 px-3 py-1.5 text-xs"
              >
                {dreamLoading ? '生成中…' : '生成 A/B 方案'}
              </button>
            </div>
          ))}
        </div>
      )}
      {dreamResult && (
        <div className="console-panel space-y-4 p-5">
          <h3 className="console-title">决策方案</h3>
          {(dreamResult.decision_options ?? []).map((opt: any, i: number) => (
            <div key={i} className="console-panel border-slate-200 p-4">
              <div
                className="flex cursor-pointer items-center justify-between"
                onClick={() => setExpandedOption(expandedOption === opt.option_id ? null : opt.option_id)}
              >
                <p className="font-medium text-slate-900">
                  方案 {opt.option_id}: {opt.title}
                </p>
                {expandedOption === opt.option_id ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
              </div>
              {expandedOption === opt.option_id && (
                <div className="mt-3 space-y-2">
                  <p className="text-sm text-slate-600">{opt.summary}</p>
                  {(opt.task_candidates ?? []).map((t: any, j: number) => (
                    <p key={j} className="text-xs text-slate-500">
                      · {t.title} [优先级: {t.priority}]
                    </p>
                  ))}
                  <button
                    type="button"
                    onClick={() =>
                      commitDecision.mutate({
                        selected_option_id: opt.option_id,
                        decision_summary: opt.summary,
                        task_candidates: opt.task_candidates ?? [],
                      })
                    }
                    className="btn-primary px-3 py-1.5 text-xs"
                  >
                    <Check size={14} className="mr-1 inline" /> 确认方案 {opt.option_id}
                  </button>
                </div>
              )}
            </div>
          ))}
          {commitDecision.isSuccess && <p className="text-sm font-medium text-emerald-700">决策已提交，任务已下发</p>}
        </div>
      )}
    </div>
  )
}
