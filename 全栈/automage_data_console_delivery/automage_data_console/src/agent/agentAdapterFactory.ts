import { ExecutiveAgentClient } from './executiveAgentClient'
import { ManagerAgentClient } from './managerAgentClient'
import { StaffAgentClient } from './staffAgentClient'
import type { AgentAdapter, AgentType } from './agentAdapter'

export const getAgentAdapter = (type: AgentType): AgentAdapter => {
  if (type === 'staff') return new StaffAgentClient()
  if (type === 'manager') return new ManagerAgentClient()
  return new ExecutiveAgentClient()
}
