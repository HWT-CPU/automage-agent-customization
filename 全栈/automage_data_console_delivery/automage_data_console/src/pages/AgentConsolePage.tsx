import { useState } from 'react'
import { getAgentAdapter } from '../agent/agentAdapterFactory'
import type { AgentType, AgentRunResponse } from '../agent/agentAdapter'
import { useIdentityStore } from '../store/useIdentityStore'
import { JsonViewer } from '../components/common/JsonViewer'

export function AgentConsolePage() {
  const { identity } = useIdentityStore()
  const [type, setType] = useState<AgentType>('staff')
  const [result, setResult] = useState<AgentRunResponse>()

  const run = async () => {
    const adapter = getAgentAdapter(type)
    const res = await adapter.run({
      agent_type: type,
      org_id: identity.orgId,
      department_id: identity.departmentId,
      user_id: identity.userId,
      node_id: identity.nodeId,
      run_date: '2026-05-09',
      input: { message: 'Run adapter in console' },
    })
    setResult(res)
  }

  return (
    <div className="grid gap-4 xl:grid-cols-2">
      <div className="console-panel p-4">
        <p className="console-title mb-3">Agent Adapter Console</p>
        <div className="flex items-center gap-2">
          <select className="rounded-lg border border-slate-200 p-2 text-sm" value={type} onChange={(e) => setType(e.target.value as AgentType)}>
            <option value="staff">staff</option>
            <option value="manager">manager</option>
            <option value="executive">executive</option>
          </select>
          <button type="button" className="rounded-lg bg-blue-600 px-3 py-2 text-sm text-white" onClick={run}>
            运行 Agent Adapter
          </button>
        </div>
        <p className="mt-3 text-sm text-slate-600">当前默认 fallback 到本地 mock；后续可替换为真实 HTTP / WebSocket / Skill 网关。</p>
      </div>
      <JsonViewer title="AgentRunResponse" data={result ?? { hint: '尚未运行' }} />
    </div>
  )
}
