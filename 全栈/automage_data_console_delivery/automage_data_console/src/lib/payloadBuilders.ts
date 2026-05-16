import type { IdentityProfile } from '../config/identities'

export function apiIdentityBlock(profile: IdentityProfile) {
  return {
    node_id: profile.nodeId,
    user_id: profile.userId,
    role: profile.role,
    level: profile.level,
    department_id: profile.departmentId,
    manager_node_id: profile.role === 'executive' ? null : profile.managerNodeId,
    metadata: {
      display_name: profile.userId,
      org_id: profile.orgId,
    },
  }
}

export interface StaffComposerInput {
  work_progress: string
  issues_faced: string[]
  solution_attempt: string
  need_support: boolean
  support_detail: string
  next_day_plan: string
  risk_level: string
  employee_comment: string
  related_task_ids: string[]
  task_progress: Array<Record<string, unknown>>
}

export function buildStaffReportBody(profile: IdentityProfile, runDate: string, input: StaffComposerInput) {
  const ts = `${runDate}T20:00:00+08:00`
  return {
    identity: apiIdentityBlock(profile),
    report: {
      schema_id: 'schema_v1_staff',
      schema_version: '1.0.0',
      timestamp: ts,
      org_id: profile.orgId,
      department_id: profile.departmentId,
      user_id: profile.userId,
      node_id: profile.nodeId,
      record_date: runDate,
      task_progress: input.task_progress,
      work_progress: input.work_progress,
      issues_faced: input.issues_faced,
      solution_attempt: input.solution_attempt,
      need_support: input.need_support,
      support_detail: input.support_detail,
      need_decision: false,
      decision_detail: '',
      next_day_plan: input.next_day_plan,
      resource_usage: {
        work_hours: 8,
        tools: ['AutoMage Data Console'],
        budget: 0,
        materials: [],
        other: '',
      },
      artifacts: [] as unknown[],
      related_task_ids: input.related_task_ids,
      risk_level: input.risk_level,
      employee_comment: input.employee_comment,
      signature: {
        confirm_status: 'confirmed',
        signed_by: profile.userId,
        signed_by_role: profile.role,
        signed_at: ts,
        signature_method: 'web_console',
        payload_hash: 'sha256:pending_client_hash',
        signature_value: 'console_placeholder',
        comment: 'Submitted from AutoMage Data Console',
      },
      meta: {
        channel: 'data_console_web',
        api_endpoint: 'POST /api/v1/report/staff',
      },
    },
  }
}

export type StaffReportRow = {
  user_id?: string
  work_record_public_id?: string
  report?: { record_date?: string; work_progress?: string; risk_level?: string; related_task_ids?: string[] }
}

export function collectSourceRecordIds(staffRows: StaffReportRow[]): string[] {
  const ids: string[] = []
  for (const row of staffRows) {
    if (row.work_record_public_id) ids.push(row.work_record_public_id)
  }
  return ids
}

export function buildManagerReportBody(
  profile: IdentityProfile,
  runDate: string,
  staffRows: StaffReportRow[],
  aggregatedSummary: string,
) {
  const ts = `${runDate}T21:15:00+08:00`
  const source_record_ids = collectSourceRecordIds(staffRows)
  const staff_report_count = staffRows.length || 1

  return {
    identity: apiIdentityBlock(profile),
    report: {
      schema_id: 'schema_v1_manager',
      schema_version: '1.0.0',
      timestamp: ts,
      org_id: profile.orgId,
      dept_id: profile.departmentId,
      manager_user_id: profile.userId,
      manager_node_id: profile.nodeId,
      summary_date: runDate,
      staff_report_count,
      missing_report_count: 0,
      missing_staff_ids: [] as string[],
      overall_health: 'yellow',
      aggregated_summary: aggregatedSummary,
      top_3_risks: [] as unknown[],
      workforce_efficiency: {
        score: 70,
        level: 'medium',
        explanation: 'Auto-generated from Data Console draft',
      },
      pending_approvals: 0,
      highlight_staff: [] as unknown[],
      blocked_items: [] as unknown[],
      manager_decisions: [] as unknown[],
      need_executive_decision: [] as unknown[],
      next_day_adjustment: [] as unknown[],
      source_record_ids,
      source_task_ids: [] as string[],
      source_incident_ids: [] as string[],
      signature: {
        confirm_status: 'confirmed',
        signed_by: profile.userId,
        signed_by_role: 'manager',
        signed_at: ts,
        signature_method: 'web_console',
        payload_hash: 'sha256:pending_manager_hash',
        signature_value: 'console_placeholder',
        comment: 'Manager summary draft from Data Console',
      },
      meta: {
        summary_type: 'department_daily',
        scope_type: 'department',
        api_endpoint: 'POST /api/v1/report/manager',
      },
    },
  }
}

type DreamDecisionOption = {
  option_id: string
  task_candidates?: Array<Record<string, unknown>>
}

export function buildDecisionCommitBody(
  profile: IdentityProfile,
  summaryPublicId: string,
  selectedOptionId: 'A' | 'B',
  decisionSummary: string,
  dreamData: Record<string, unknown> | null,
) {
  const options = (dreamData?.decision_options as DreamDecisionOption[] | undefined) ?? []
  const chosen = options.find((o) => o.option_id === selectedOptionId)
  const task_candidates =
    chosen?.task_candidates?.map((t) => ({
      ...t,
      org_id: profile.orgId,
      department_id: profile.departmentId,
      creator_user_id: profile.userId,
      manager_user_id: 'lijingli',
      manager_node_id: 'manager_agent_mvp_001',
      assignee_user_id: (t.assignee_user_id as string) ?? 'zhangsan',
      assignee_node_id: 'staff_agent_mvp_001',
      priority: (t.priority as string) ?? 'high',
      status: (t.status as string) ?? 'pending',
    })) ?? []

  return {
    identity: apiIdentityBlock(profile),
    decision: {
      org_id: profile.orgId,
      department_id: profile.departmentId,
      summary_id: summaryPublicId,
      selected_option_id: selectedOptionId,
      selected_option_label: selectedOptionId,
      decision_summary: decisionSummary,
      task_candidates,
    },
  }
}

export function buildCreateTasksBody(tasks: Array<Record<string, unknown>>) {
  return { tasks }
}
