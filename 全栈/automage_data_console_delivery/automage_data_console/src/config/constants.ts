export const knownRisk = 'manager_cross_dept 当前未拒绝，返回 200，里程碑三前需要关闭'

export const integrationFacts = {
  backendStarted: true,
  healthzOk: true,
  pytestPassed: 30,
  mainChainPassed: true,
  dbSelectCheckPassed: true,
  nonBlockingRiskCount: 1,
}

export const navItems = [
  { label: '总览 Dashboard', path: '/' },
  { label: '数据流转 Data Flow', path: '/data-flow' },
  { label: 'Staff 工作台', path: '/staff' },
  { label: 'Manager 工作台', path: '/manager' },
  { label: 'Executive 决策台', path: '/executive' },
  { label: '任务中心', path: '/tasks' },
  { label: '异常中心', path: '/incidents' },
  { label: 'Agent 控制台', path: '/agent-console' },
  { label: 'API / DB 监控', path: '/api-monitor' },
  { label: '审计日志', path: '/audit' },
  { label: '设置', path: '/settings' },
]
