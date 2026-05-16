import heroMock from '../assets/hero-product-mockup.svg'
import agentVisual from '../assets/agent-network-visual.svg'
import workflowVisual from '../assets/workflow-loop-visual.svg'
import dashboardVisual from '../assets/dashboard-preview-dark.svg'
import decisionExhibit from '../assets/decision-exhibit.svg'
import riskBoard from '../assets/risk-incident-board.svg'
import taskStrip from '../assets/task-kanban-strip.svg'
import schemaRail from '../assets/schema-api-rail.svg'

const frames = [
  { title: 'Staff Facts Intake', image: heroMock },
  { title: 'Manager Summary Merge', image: agentVisual },
  { title: 'Workflow Loop', image: workflowVisual },
  { title: 'Executive Console', image: dashboardVisual },
  { title: 'Decision Exhibit', image: decisionExhibit },
  { title: 'Risk Board', image: riskBoard },
  { title: 'Task Strip', image: taskStrip },
  { title: 'Schema Rail', image: schemaRail },
]

export function FilmStripGallery() {
  const renderRow = (reverse = false) => (
    <div className={`film-row ${reverse ? 'film-row-reverse' : ''}`}>
      {[...frames, ...frames].map((frame, idx) => (
        <article key={`${frame.title}-${idx}`} className="film-card">
          <img src={frame.image} alt={frame.title} className="film-image" />
          <div className="film-caption">
            <span>{frame.title}</span>
          </div>
        </article>
      ))}
    </div>
  )

  return (
    <section className="relative overflow-hidden rounded-[30px] border border-slate-200 bg-slate-950 px-3 py-10">
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_30%,rgba(56,189,248,0.18),transparent_40%),radial-gradient(circle_at_80%_60%,rgba(168,85,247,0.18),transparent_38%)]" />
      <div className="relative space-y-5">
        <p className="px-3 text-xs uppercase tracking-[0.18em] text-slate-300">Visual Transition / Product Montage</p>
        <div className="film-mask">{renderRow(false)}</div>
        <div className="film-mask -rotate-[1.2deg]">{renderRow(true)}</div>
        <div className="film-mask rotate-[0.6deg]">{renderRow(false)}</div>
      </div>
    </section>
  )
}
