interface Props {
  staff: {
    todayDone: string[]
    issues: string[]
    triedSolutions: string[]
    needSupport: boolean
    tomorrowPlan: string[]
    relatedTasks: string[]
    taskProgress: string
    riskLevel: string
    artifacts: string[]
  }
}

export function StaffReportPanel({ staff }: Props) {
  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-5">
      <h3 className="text-xl font-semibold text-slate-900">Staff 日报与任务回流</h3>
      <p className="mt-2 text-sm text-slate-600">
        Staff 日报不是纯文本，而是进入 `schema_v1_staff` 后由后端拆分写入 `work_record_items`，任务结果回流下一轮日报。
      </p>
      <div className="mt-3 grid gap-4 md:grid-cols-2">
        <div>
          <p className="text-xs text-slate-500">今日完成事项</p>
          <ul className="list-disc pl-5 text-sm text-slate-700">
            {staff.todayDone.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
          <p className="mt-3 text-xs text-slate-500">遇到问题</p>
          <ul className="list-disc pl-5 text-sm text-slate-700">
            {staff.issues.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
        <div>
          <p className="text-xs text-slate-500">已尝试方案</p>
          <ul className="list-disc pl-5 text-sm text-slate-700">
            {staff.triedSolutions.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
          <p className="mt-3 text-xs text-slate-500">明日计划</p>
          <ul className="list-disc pl-5 text-sm text-slate-700">
            {staff.tomorrowPlan.map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      </div>
      <div className="mt-3 grid gap-2 text-sm text-slate-600 md:grid-cols-4">
        <p>是否需要支持：{staff.needSupport ? '是' : '否'}</p>
        <p>任务进展：{staff.taskProgress}</p>
        <p>风险等级：{staff.riskLevel}</p>
        <p>关联任务：{staff.relatedTasks.join(', ')}</p>
      </div>
      <p className="mt-2 text-sm text-slate-600">产出物：{staff.artifacts.join('、')}</p>
    </section>
  )
}
