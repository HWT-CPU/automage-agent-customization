/** 中文标签映射 — 统一翻译所有 API 字段名 */
export const fieldLabels: Record<string, string> = {
  // 用户 & 身份
  username: '用户名',
  display_name: '姓名',
  user_id: '用户 ID',
  node_id: '节点 ID',
  role: '角色',
  level: '层级',
  department_id: '部门 ID',
  org_id: '组织 ID',
  email: '邮箱',
  phone: '手机号',
  job_title: '岗位',
  status: '状态',
  meta: '元数据',

  // 日报
  work_progress: '工作进展',
  issues_faced: '遇到的问题',
  solution_attempt: '解决方案',
  need_support: '是否需要支持',
  next_day_plan: '明日计划',
  risk_level: '风险等级',
  resource_usage: '资源消耗',
  record_date: '日期',
  schema_id: 'Schema ID',
  staff_report: '员工日报',
  staff_reports: '员工日报列表',

  // 汇总
  dept_id: '部门 ID',
  aggregated_summary: '汇总摘要',
  overall_health: '整体健康度',
  top_3_risks: 'Top 3 风险',
  workforce_efficiency: '团队效能',
  pending_approvals: '待审批',
  summary_date: '汇总日期',
  source_record_ids: '来源记录',
  manager_report: '经理汇总',

  // 任务
  task_id: '任务 ID',
  task_title: '任务标题',
  task_description: '任务描述',
  assignee_user_id: '执行人',
  creator_user_id: '创建人',
  priority: '优先级',
  due_at: '截止时间',
  task_payload: '任务负载',

  // 决策
  decision_summary: '决策摘要',
  selected_option_id: '选中方案',
  option_id: '方案 ID',
  decision_options: '决策方案',
  recommended_option: '推荐方案',
  reasoning_summary: '推荐理由',
  source_summary_id: '来源汇总',

  // 审计 & 系统
  action: '操作类型',
  target_type: '目标类型',
  target_id: '目标 ID',
  actor_user_id: '操作人',
  summary: '描述',
  event_at: '时间',
  request_id: '请求 ID',
  payload: '负载数据',
  task_queue: '任务队列',
  audit_logs: '审计日志',
  agent_sessions: 'Agent 会话',
  open_incidents: '未关闭异常',
  total_users: '用户总数',
  reports_today: '今日日报',

  // 通用
  id: 'ID',
  public_id: '公开 ID',
  title: '标题',
  description: '描述',
  content: '内容',
  message: '消息',
  detail: '详情',
  created_at: '创建时间',
  updated_at: '更新时间',
  deleted_at: '删除时间',

  // 状态
  pending: '待处理',
  in_progress: '进行中',
  done: '已完成',
  completed: '已完成',
  closed: '已关闭',
  not_started: '未开始',

  // 优先级
  critical: '紧急',
  high: '高',
  medium: '中',
  low: '低',
  normal: '普通',

  // 角色
  staff: '员工',
  manager: '经理',
  executive: '老板',
  admin: '管理员',

  // 健康度
  green: '健康',
  yellow: '警告',
  red: '危险',

  // 异常
  incident: '异常事件',
  incidents: '异常列表',
  severity: '严重程度',
  reporter_user_id: '报告人',
}

/** 翻译字段名 */
export function label(key: string): string {
  return fieldLabels[key] ?? key
}

/** 翻译对象的所有 key */
export function translateKeys(obj: Record<string, unknown>): Record<string, unknown> {
  const result: Record<string, unknown> = {}
  for (const [k, v] of Object.entries(obj)) {
    const key = fieldLabels[k] ?? k
    result[key] = v
  }
  return result
}

/** 翻译值 */
export function translateValue(value: string | number | null | undefined): string {
  if (value == null) return '—'
  return fieldLabels[String(value)] ?? String(value)
}
