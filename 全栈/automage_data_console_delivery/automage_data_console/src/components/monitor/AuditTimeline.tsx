const timeline = [
  '09:10 Staff 提交日报 -> audit_logs',
  '09:16 Manager 提交汇总 -> audit_logs',
  '09:24 Dream 归并 -> agent_decision_logs',
  '09:33 Executive 确认方案 A -> decision_logs',
  '09:42 Task 更新回流 -> task_updates / audit_logs',
]

export function AuditTimeline() {
  return (
    <div className="console-panel p-4">
      <p className="console-title mb-3">审计时间线</p>
      <ol className="space-y-2 text-sm text-slate-700">
        {timeline.map((item) => (
          <li key={item} className="rounded-lg bg-slate-50 px-3 py-2">
            {item}
          </li>
        ))}
      </ol>
    </div>
  )
}
