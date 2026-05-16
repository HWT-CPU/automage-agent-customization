export type HealthTone = 'green' | 'yellow' | 'red'

export type WorkflowStepStatus = 'Mock 已通' | '真实 API 已通' | 'P1 扩展'

export interface WorkflowStep {
  step: string
  role: string
  table: string
  api: string
  status: WorkflowStepStatus
}

export const landingMeta = {
  title: 'AutoMage-2｜Agent 时代组织运行中枢',
  subtitle: '把一线事实、部门汇总、老板决策与任务回流，压缩成一条可校验、可追溯、可执行的数据闭环。',
  orgId: 'org_automage_mvp',
  departmentId: 'dept_mvp_core',
  staffName: 'zhangsan',
  managerName: 'lijingli',
  executiveName: 'chenzong',
  staffNode: 'staff_agent_mvp_001',
  managerNode: 'manager_agent_mvp_001',
  executiveNode: 'executive_agent_boss_001',
}

export const heroStatusCards = [
  { label: '主链路', value: 'Staff -> Manager -> Dream -> Decision -> Task 已跑通' },
  { label: '后端健康', value: '/healthz 正常' },
  { label: '测试状态', value: 'pytest 30 passed' },
  { label: '风险状态', value: '1 个非阻塞 RBAC 风险待关闭' },
]

export const workflowSteps: WorkflowStep[] = [
  { step: 'Staff 日报提交', role: 'Staff', table: 'work_records / work_record_items', api: 'POST /api/v1/report/staff', status: '真实 API 已通' },
  { step: '后端 Schema 校验', role: 'Backend', table: 'audit_logs', api: 'POST /api/v1/report/staff', status: '真实 API 已通' },
  { step: 'Manager 汇总', role: 'Manager', table: 'summaries / summary_source_links', api: 'POST /api/v1/report/manager', status: '真实 API 已通' },
  { step: 'Dream 风险归并', role: 'Executive/Dream', table: 'decision_records / decision_logs', api: 'POST /internal/dream/run', status: 'Mock 已通' },
  { step: '老板确认决策', role: 'Executive', table: 'decision_records', api: 'POST /api/v1/decision/commit', status: '真实 API 已通' },
  { step: '任务生成与分配', role: 'Task System', table: 'tasks / task_assignments / task_updates', api: 'POST /api/v1/tasks', status: '真实 API 已通' },
  { step: 'Staff 查询任务并回流日报', role: 'Staff', table: 'task_updates / work_record_items', api: 'GET /api/v1/tasks', status: '真实 API 已通' },
]

export const agentCards = [
  {
    name: 'Staff Agent',
    duty: ['引导员工填写日报', '提交结构化 Staff Schema', '查询自己的任务', '更新任务进展', '只能访问自己的数据'],
    output: ['Staff 日报', '任务进展', '风险/阻塞', '产出物'],
    tables: ['work_records', 'work_record_items', 'artifacts', 'incidents', 'task_updates'],
    apis: ['POST /api/v1/report/staff', 'GET /api/v1/tasks'],
  },
  {
    name: 'Manager Agent',
    duty: ['读取本部门 Staff 日报', '汇总部门情况', '识别风险', '处理权限内事项', '上推老板决策项'],
    output: ['Manager 汇总', 'top risks', 'blocked items', 'need executive decision', '部门调整建议'],
    tables: ['summaries', 'summary_source_links', 'incidents', 'tasks', 'audit_logs'],
    apis: ['POST /api/v1/report/manager', 'GET /api/v1/report/staff'],
  },
  {
    name: 'Executive Agent / Dream',
    duty: ['读取部门汇总', '归并同类事项', '生成老板决策卡片', '给出 A/B 方案', '老板确认后生成任务'],
    output: ['Executive Decision Card', 'decision_records', 'decision_logs', 'generated_tasks'],
    tables: ['decision_records', 'decision_logs', 'tasks', 'task_assignments', 'audit_logs'],
    apis: ['POST /internal/dream/run', 'POST /api/v1/decision/commit', 'POST /api/v1/tasks'],
  },
]

export const managerSummaryDemo = {
  summaryDate: '2026-05-06',
  department: 'MVP 核心组',
  staffReportCount: 2,
  missingReportCount: 0,
  overallHealth: 'yellow',
  aggregatedSummary:
    '本地 Mock 闭环可交付；真实数据库已可连接，主链路 API 已联调通过，存在 1 项 manager_cross_dept 权限校验未拒绝风险。',
  top3Risks: [
    '数据库 Skill / API 端到端读写验证需要持续回归',
    '新增表与里程碑一契约关系仍需冻结',
    'manager_cross_dept RBAC 风险尚未关闭',
  ],
  blockedItems: ['跨部门提交应拒绝但当前未拒绝（非阻塞）'],
  needExecutiveDecision: '是否在里程碑三前将 RBAC 风险关闭为上线门槛',
  nextDayAdjustment: '优先维持主链路稳定，补齐跨部门权限拒绝与审计告警。',
}

export const staffReportDemo = {
  todayDone: [
    '完成 Staff 日报字段映射与 schema_v1_staff 对齐',
    '完成 mock workflow 全链路脚本验证',
  ],
  issues: ['真实库新增表与旧契约映射存在差异', '跨部门 manager 提交拒绝规则待补齐'],
  triedSolutions: ['先保留 Mock fallback，确保演示稳定', '将关键字段绑定到 API 契约与 DDL'],
  needSupport: true,
  tomorrowPlan: ['联调 decision/commit 与 tasks 读取', '验证 RBAC 拒绝逻辑并落审计'],
  relatedTasks: ['TASK-20260507-BACKEND-001', 'TASK-20260507-AGENT-001'],
  taskProgress: 'in_progress',
  riskLevel: 'high',
  artifacts: ['run_mock_workflow.py', 'Mock 字段与 API 对照表'],
}

export const decisionCardDemo = {
  decisionId: 'DEC-20260506-001',
  decisionTitle: '5.7 是否优先冻结 API / 数据库 Skill 最小链路',
  background: '里程碑二 Mock 已闭环，但真实 API 质量与权限边界决定里程碑三稳定性。',
  sourceSummary: 'MSUM-20260506-NEED-EXEC-001',
  riskLevel: 'high',
  optionA: '主链路优先，先保证 Staff 写入/Manager 查询/Task 查询稳定。',
  optionB: '维持多线并行，Landing Page 与注册方案同步推进。',
  recommendedOption: 'A',
  reasoningSummary: 'Workflow First：先闭合主链路，再扩展支线，避免联调反复。',
  expectedImpact: '降低 5.8 联调失败概率，保证任务回流闭环可验证。',
  generatedTasks: ['TASK-20260507-BACKEND-001', 'TASK-20260507-AGENT-001', 'TASK-20260507-ARCH-001'],
  humanConfirmStatus: 'pending',
  confirmedBy: 'chenzong',
  confirmedAt: '2026-05-06T21:40:00+08:00',
}

export const taskBoardDemo = [
  {
    taskId: 'TASK-20260507-BACKEND-001',
    publicId: 'TSK-BE-001',
    title: '提供三条最小 API 调用样例',
    assignee: 'xiongjinwen',
    source: 'executive_decision',
    priority: 'critical',
    dueAt: '2026-05-07 12:00',
    status: 'pending',
    latestUpdate: '等待最终样例回包',
    relatedDecision: 'DEC-20260506-001',
    relatedIncident: 'INC-20260506-API-SKILL-001',
  },
  {
    taskId: 'TASK-20260507-AGENT-001',
    publicId: 'TSK-AG-001',
    title: '替换 mock 为真实 API 调用',
    assignee: 'huwentao',
    source: 'executive_decision',
    priority: 'high',
    dueAt: '2026-05-07 20:00',
    status: 'in_progress',
    latestUpdate: 'Staff 写入已接通，任务查询验证中',
    relatedDecision: 'DEC-20260506-001',
    relatedIncident: 'INC-20260506-API-SKILL-001',
  },
  {
    taskId: 'TASK-20260507-ARCH-001',
    publicId: 'TSK-AR-001',
    title: '输出 DB 与 Mock 字段差异清单',
    assignee: 'yangzhuo',
    source: 'executive_decision',
    priority: 'high',
    dueAt: '2026-05-07 18:00',
    status: 'completed',
    latestUpdate: '映射表已提交，待评审',
    relatedDecision: 'DEC-20260506-001',
    relatedIncident: 'INC-20260506-API-SKILL-001',
  },
  {
    taskId: 'TASK-20260507-RBAC-001',
    publicId: 'TSK-SEC-001',
    title: '修复 manager_cross_dept 拒绝校验',
    assignee: 'backend-team',
    source: 'integration_acceptance',
    priority: 'medium',
    dueAt: '2026-05-10 18:00',
    status: 'blocked',
    latestUpdate: '已复现，等待 RBAC 中间件补丁',
    relatedDecision: 'DEC-20260506-001',
    relatedIncident: 'INC-20260508-RBAC-001',
  },
]

export const incidentDemo = [
  {
    title: '高风险 Staff 报告：真实 API / Skill 未完全可回归',
    source: 'Staff',
    severity: 'high',
    status: 'tracking',
    relatedTask: 'TASK-20260507-BACKEND-001',
    nextAction: '补齐可复现脚本并固化回归步骤',
  },
  {
    title: 'Manager top risk：跨部门提交拒绝缺失',
    source: 'Manager',
    severity: 'medium',
    status: 'open',
    relatedTask: 'TASK-20260507-RBAC-001',
    nextAction: '里程碑三前关闭为上线前置项',
  },
]

export const integrationStatus = {
  backendStarted: true,
  healthz: true,
  realApiMainFlow: true,
  dbSelectVerified: true,
  pytestPassed: 30,
  uniqueRisk: 'manager_cross_dept 当前未拒绝，非阻塞，里程碑三前关闭',
}

export const auditTimelineDemo = [
  '09:10 Staff schema_v1_staff 提交并通过校验',
  '09:16 Manager 汇总写入 summaries / summary_source_links',
  '09:24 Dream 归并输出决策卡片 DEC-20260506-001',
  '09:33 老板确认推荐方案 A',
  '09:36 任务生成写入 tasks / task_assignments / task_updates',
  '09:42 Staff 拉取任务并写入下一轮日报种子',
]

export const dashboardCards: Array<{ title: string; value: string; tone: HealthTone; description: string }> = [
  { title: '今日组织健康度', value: 'Yellow', tone: 'yellow', description: '来自 Manager 汇总 + 风险归并' },
  { title: '待决策事项', value: '1 条（高优先）', tone: 'yellow', description: '含 A/B 方案，来源 MVP 核心组' },
  { title: '高风险事项', value: '2 条', tone: 'red', description: '均已挂接任务/决策追踪' },
  { title: '今日任务状态', value: '待处理1 / 进行中1 / 已完成1 / 阻塞1', tone: 'yellow', description: '状态来自 tasks + task_updates' },
  { title: '数据可信状态', value: 'Schema/幂等/审计/落库: 已启用', tone: 'green', description: '数据库作为最终事实源' },
  { title: '当前联调状态', value: '主链路已通过', tone: 'green', description: '仅剩 1 项 RBAC 非阻塞风险' },
]
