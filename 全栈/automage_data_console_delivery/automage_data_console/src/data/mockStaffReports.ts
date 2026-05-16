export const mockStaffReports = [
  {
    record_date: '2026-05-06',
    user_id: 'zhangsan',
    risk_level: 'low',
    work_progress: ['完成日报提交流程验证', '完成任务查询页面联调'],
    issues_faced: [],
    next_day_plan: ['跟进任务状态更新', '补充 artifact 字段'],
    related_task_ids: ['TASK-20260507-AGENT-001'],
  },
  {
    record_date: '2026-05-06',
    user_id: 'user_backend_001',
    risk_level: 'high',
    work_progress: ['真实库连接可用', '发现 API/Skill 最小链路未完整验证'],
    issues_faced: ['manager_cross_dept 当前未拒绝，需里程碑三前关闭'],
    next_day_plan: ['补齐 API 调用样例'],
    related_task_ids: ['TASK-20260507-BACKEND-001'],
  },
]
