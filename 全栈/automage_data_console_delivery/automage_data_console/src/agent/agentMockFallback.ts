import { createRequestId } from '../lib/idempotency'
import type { AgentRunRequest, AgentRunResponse } from './agentAdapter'

export const runAgentMock = async (req: AgentRunRequest, output_schema_id: string, output: unknown): Promise<AgentRunResponse> => {
  return {
    ok: true,
    agent_type: req.agent_type,
    node_id: req.node_id,
    output_schema_id,
    output,
    warnings: ['REAL_AGENT_NOT_CONNECTED_USING_MOCK_FALLBACK'],
    trace_id: createRequestId('agent_trace'),
    fallback: true,
  }
}
