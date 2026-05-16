export type IdentityRole = 'staff' | 'manager' | 'executive'

export interface IdentityProfile {
  userId: string
  role: IdentityRole
  nodeId: string
  level: 'l1_staff' | 'l2_manager' | 'l3_executive'
  managerNodeId: string
  orgId: string
  departmentId: string
}

export const identityProfiles: Record<IdentityRole, IdentityProfile> = {
  staff: {
    userId: 'zhangsan',
    role: 'staff',
    nodeId: 'staff_agent_mvp_001',
    level: 'l1_staff',
    managerNodeId: 'manager_agent_mvp_001',
    orgId: 'org_automage_mvp',
    departmentId: 'dept_mvp_core',
  },
  manager: {
    userId: 'lijingli',
    role: 'manager',
    nodeId: 'manager_agent_mvp_001',
    level: 'l2_manager',
    managerNodeId: 'executive_agent_boss_001',
    orgId: 'org_automage_mvp',
    departmentId: 'dept_mvp_core',
  },
  executive: {
    userId: 'chenzong',
    role: 'executive',
    nodeId: 'executive_agent_boss_001',
    level: 'l3_executive',
    managerNodeId: 'executive_agent_boss_001',
    orgId: 'org_automage_mvp',
    departmentId: 'dept_mvp_core',
  },
}
