import type { WorkflowStep } from '../data/demoData'
import loopVisual from '../assets/workflow-loop-visual.svg'

interface Props {
  steps: WorkflowStep[]
}

export function WorkflowSection({ steps }: Props) {
  return (
    <section id="workflow" className="space-y-6 scroll-mt-24">
      <div className="space-y-2">
        <h2 className="section-title">Workflow 闭环</h2>
        <p className="text-sm text-slate-600">
          Staff 日报 -&gt; Schema 校验 -&gt; Manager 汇总 -&gt; Dream 归并 -&gt; 老板决策 -&gt; 任务下发 -&gt; 结果回流
        </p>
      </div>
      <img src={loopVisual} alt="Workflow 闭环视觉图" className="w-full rounded-2xl border border-slate-200" />
      <div className="grid gap-3 lg:grid-cols-2">
        {steps.map((item, index) => (
          <div
            key={item.step}
            className="group rounded-2xl border border-slate-200 bg-white p-4 transition-all hover:-translate-y-0.5 hover:border-sky-300 hover:shadow-[0_16px_30px_rgba(14,116,144,0.14)]"
          >
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="text-xs text-slate-400">Step {index + 1}</p>
                <p className="text-base font-semibold text-slate-900">{item.step}</p>
              </div>
              <span className="rounded-full border border-slate-300 px-2 py-1 text-xs text-slate-600 group-hover:border-sky-300 group-hover:text-sky-700">
                {item.status}
              </span>
            </div>
            <div className="mt-3 grid gap-2 text-sm text-slate-600 md:grid-cols-3">
              <p>角色：{item.role}</p>
              <p>数据表：{item.table}</p>
              <p>API：{item.api}</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
