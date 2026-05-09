import { useEffect, useMemo, useState } from 'react'
import { HeroSection } from './components/HeroSection'
import { SystemStatusBar } from './components/SystemStatusBar'
import {
  agentCards,
  auditTimelineDemo,
  dashboardCards,
  decisionCardDemo,
  heroStatusCards,
  incidentDemo,
  integrationStatus,
  landingMeta,
  managerSummaryDemo,
  staffReportDemo,
  taskBoardDemo,
  workflowSteps,
} from './data/demoData'
import { ExecutiveDashboard } from './components/ExecutiveDashboard'
import { DecisionCard } from './components/DecisionCard'
import { ManagerSummaryPanel } from './components/ManagerSummaryPanel'
import { StaffReportPanel } from './components/StaffReportPanel'
import { TaskBoard } from './components/TaskBoard'
import { RiskIncidentPanel } from './components/RiskIncidentPanel'
import { AuditTimeline } from './components/AuditTimeline'
import { apiProof, integrationProof, schemaProof, tableProof } from './data/apiMapping'
import { RoadmapSection } from './components/RoadmapSection'
import { fetchLandingData } from './lib/apiClient'
import { PositioningSection } from './components/PositioningSection'
import { IntegrationStatusMatrix } from './components/IntegrationStatusMatrix'
import { DataTrustPipeline } from './components/DataTrustPipeline'
import { FinalCTA } from './components/FinalCTA'
import { FilmStripGallery } from './components/FilmStripGallery'
import { WorkflowStory } from './components/WorkflowStory'
import { AgentNetworkSection } from './components/AgentNetworkSection'
import { VisualArchive } from './components/VisualArchive'
import { PremiumFooter } from './components/PremiumFooter'
import { ReportPressSection } from './components/ReportPressSection'

function App() {
  const [mode, setMode] = useState<'demo' | 'api'>('demo')
  const [apiBase, setApiBase] = useState('http://localhost:8000')
  const [healthOk, setHealthOk] = useState(integrationStatus.healthz)

  useEffect(() => {
    const bootstrap = async () => {
      const data = await fetchLandingData()
      setMode(data.mode)
      setApiBase(data.apiBase)
      setHealthOk(Boolean(data.healthz?.status))
    }
    void bootstrap()
  }, [])

  const taskStats = useMemo(() => {
    const counts = { pending: 0, in_progress: 0, blocked: 0, completed: 0 }
    taskBoardDemo.forEach((task) => {
      if (task.status === 'pending') counts.pending += 1
      if (task.status === 'in_progress') counts.in_progress += 1
      if (task.status === 'blocked') counts.blocked += 1
      if (task.status === 'completed') counts.completed += 1
    })
    return [
      { name: '待处理', value: counts.pending },
      { name: '进行中', value: counts.in_progress },
      { name: '阻塞', value: counts.blocked },
      { name: '已完成', value: counts.completed },
    ]
  }, [])

  return (
    <div className="scroll-smooth-page borderless-flow relative pb-16 pt-4">
      <div className="global-ocean-backdrop pointer-events-none fixed inset-0" aria-hidden="true">
        <div className="global-island-backdrop" />
      </div>
      <svg className="pointer-events-none absolute h-0 w-0" aria-hidden="true" focusable="false">
        <filter id="handDrawnNoise">
          <feTurbulence result="noise" numOctaves="5" baseFrequency="0.0065" type="fractalNoise" />
          <feDisplacementMap yChannelSelector="G" xChannelSelector="R" scale="900" in2="noise" in="SourceGraphic" />
        </filter>
      </svg>

      <div className="relative z-10">
        <header className="sticky top-4 z-30 mb-8 px-4 md:px-10">
          <div className="borderless-topbar flex flex-col gap-3 px-4 py-3 md:flex-row md:items-center md:justify-between">
            <div>
              <p className="text-base font-semibold text-slate-900">AutoMage-2</p>
              <p className="text-xs text-slate-500">MVP Landing Page P0 · v1.1 Visual Upgrade</p>
            </div>
            <nav className="flex flex-wrap items-center gap-3 text-xs text-slate-600">
              <a href="#workflow">闭环流程</a>
              <a href="#agents">三层 Agent</a>
              <a href="#dashboard">老板控制台</a>
              <a href="#decision">老板决策</a>
              <a href="#tasks">任务追踪</a>
              <a href="#integration-status">联调状态</a>
              <a href="#roadmap">Roadmap</a>
              <SystemStatusBar mode={mode} />
            </nav>
          </div>
        </header>

        <main className="space-y-14 px-4 md:px-10">
          <HeroSection title={landingMeta.title} subtitle={landingMeta.subtitle} cards={heroStatusCards} />
          <FilmStripGallery />
          <PositioningSection />
          <WorkflowStory steps={workflowSteps} />
          <AgentNetworkSection cards={agentCards} />
          <ExecutiveDashboard cards={dashboardCards} taskStats={taskStats} />
          <DecisionCard decision={decisionCardDemo} />
          <VisualArchive />
          <section className="space-y-4">
            <h2 className="section-title">执行层细节面板</h2>
            <p className="text-sm text-slate-600">
              Staff 记录事实，Manager 归并判断，Executive 确认关键选择，系统把结果转成可追踪任务。
            </p>
            <ManagerSummaryPanel summary={managerSummaryDemo} />
            <StaffReportPanel staff={staffReportDemo} />
            <TaskBoard tasks={taskBoardDemo} />
            <RiskIncidentPanel incidents={incidentDemo} />
            <AuditTimeline timeline={auditTimelineDemo} />
          </section>
          <ReportPressSection />
          <IntegrationStatusMatrix
            healthOk={healthOk}
            pytestPassed={integrationStatus.pytestPassed}
            risk={integrationStatus.uniqueRisk}
          />
          <DataTrustPipeline schemaProof={schemaProof} apiProof={apiProof} tableProof={tableProof} />

          <details className="rounded-2xl border border-slate-200 bg-white p-4 text-sm text-slate-600">
            <summary className="cursor-pointer text-slate-900">技术详情（统一联调身份）</summary>
            <div className="mt-3 grid gap-2 md:grid-cols-2">
              <p>org_id: {landingMeta.orgId}</p>
              <p>department_id: {landingMeta.departmentId}</p>
              <p>staff: {landingMeta.staffName}</p>
              <p>manager: {landingMeta.managerName}</p>
              <p>executive: {landingMeta.executiveName}</p>
              <p>staff node: {landingMeta.staffNode}</p>
              <p>manager node: {landingMeta.managerNode}</p>
              <p>executive node: {landingMeta.executiveNode}</p>
              <p>联调摘要: {integrationProof.join(' | ')}</p>
            </div>
          </details>
          <RoadmapSection />
          <FinalCTA />
        </main>

        <div className="px-4 md:px-10">
          <PremiumFooter apiBase={apiBase} />
        </div>
      </div>
    </div>
  )
}

export default App
