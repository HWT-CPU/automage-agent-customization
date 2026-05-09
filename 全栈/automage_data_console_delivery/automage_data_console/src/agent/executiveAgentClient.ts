import type { AgentAdapter, AgentRunRequest } from './agentAdapter'
import { runAgentMock } from './agentMockFallback'
import { mockDecisions } from '../data/mockDecisions'

export class ExecutiveAgentClient implements AgentAdapter {
  async run(req: AgentRunRequest) {
    return runAgentMock(req, 'schema_v1_executive', mockDecisions[0])
  }
}
