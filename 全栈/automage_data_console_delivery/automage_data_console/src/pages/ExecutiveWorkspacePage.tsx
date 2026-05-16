import { DreamRunPanel } from '../components/executive/DreamRunPanel'
import { ExecutiveDecisionCenter } from '../components/executive/ExecutiveDecisionCenter'

export function ExecutiveWorkspacePage() {
  return (
    <div className="space-y-4">
      <DreamRunPanel />
      <ExecutiveDecisionCenter />
    </div>
  )
}
