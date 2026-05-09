import agentVisual from '../assets/agent-network-visual.svg'
import dashboardVisual from '../assets/dashboard-preview-dark.svg'
import heroVisual from '../assets/hero-product-mockup.svg'
import workflowVisual from '../assets/workflow-loop-visual.svg'
import decisionExhibit from '../assets/decision-exhibit.svg'
import riskBoard from '../assets/risk-incident-board.svg'
import taskStrip from '../assets/task-kanban-strip.svg'
import schemaRail from '../assets/schema-api-rail.svg'
import auditTimeline from '../assets/audit-timeline-visual.svg'
import managerSheet from '../assets/manager-summary-sheet.svg'

const items = [
  { title: 'Agent Network Snapshot', image: agentVisual, size: 'lg:col-span-2' },
  { title: 'Executive Dashboard', image: dashboardVisual, size: '' },
  { title: 'Workflow Ribbon', image: workflowVisual, size: '' },
  { title: 'Decision Exhibit', image: decisionExhibit, size: '' },
  { title: 'Risk Incident Board', image: riskBoard, size: '' },
  { title: 'Task Kanban Strip', image: taskStrip, size: '' },
  { title: 'Schema API Rail', image: schemaRail, size: '' },
  { title: 'Audit Timeline', image: auditTimeline, size: '' },
  { title: 'Manager Summary Sheet', image: managerSheet, size: '' },
  { title: 'Hero Product Mockup', image: heroVisual, size: 'lg:col-span-2' },
]

export function VisualArchive() {
  return (
    <section className="uiverse-mosaic-bg relative space-y-4 overflow-hidden rounded-[28px] border border-slate-200/70 bg-white/75 p-5 md:p-6">
      <div className="flex items-end justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Visual Archive</p>
          <h2 className="mt-2 text-3xl font-semibold tracking-tight text-slate-900">产品视觉资料库</h2>
        </div>
        <p className="max-w-md text-sm text-slate-600">不是装饰图集，而是闭环运行中的界面切片：风险、决策、任务、回流与审计。</p>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        {items.map((item) => (
          <article key={item.title} className={`overflow-hidden rounded-3xl border border-slate-200 bg-white ${item.size}`}>
            <img src={item.image} alt={item.title} className="h-full w-full object-cover" />
            <div className="border-t border-slate-200 px-4 py-3 text-sm text-slate-700">{item.title}</div>
          </article>
        ))}
      </div>
    </section>
  )
}
