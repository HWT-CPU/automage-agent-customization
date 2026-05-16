import type { AgentAdapter, AgentRunRequest } from './agentAdapter'
import { runAgentMock } from './agentMockFallback'
import { mockStaffReports } from '../data/mockStaffReports'

export class StaffAgentClient implements AgentAdapter {
  async run(req: AgentRunRequest) {
    return runAgentMock(req, 'schema_v1_staff', mockStaffReports[0])
  }
}
