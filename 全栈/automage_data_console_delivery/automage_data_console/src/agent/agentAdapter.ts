export type AgentType = 'staff' | 'manager' | 'executive'

export type AgentRunRequest = {
  agent_type: AgentType
  org_id: string
  department_id?: string
  user_id: string
  node_id: string
  run_date: string
  input: unknown
  context?: unknown
}

export type AgentRunResponse = {
  ok: boolean
  agent_type: string
  node_id: string
  output_schema_id: string
  output: unknown
  warnings: string[]
  trace_id: string
  fallback: boolean
}

export interface AgentAdapter {
  run(req: AgentRunRequest): Promise<AgentRunResponse>
}
