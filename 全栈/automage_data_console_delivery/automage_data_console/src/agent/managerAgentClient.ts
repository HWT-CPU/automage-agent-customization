import type { AgentAdapter, AgentRunRequest } from './agentAdapter'
import { runAgentMock } from './agentMockFallback'
import { mockManagerSummaries } from '../data/mockManagerSummaries'

export class ManagerAgentClient implements AgentAdapter {
  async run(req: AgentRunRequest) {
    return runAgentMock(req, 'schema_v1_manager', mockManagerSummaries[1])
  }
}
