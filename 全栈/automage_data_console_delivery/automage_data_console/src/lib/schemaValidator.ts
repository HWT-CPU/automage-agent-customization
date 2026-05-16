type ValidateResult = {
  ok: boolean
  errors: string[]
}

export const validateBasicStaffSchema = (payload: Record<string, unknown>): ValidateResult => {
  const report = (payload.report as Record<string, unknown> | undefined) ?? payload
  const required = ['record_date', 'work_progress', 'issues_faced', 'next_day_plan', 'risk_level']
  const errors = required.filter((key) => !(key in report) || report[key] === '' || report[key] === undefined).map((key) => `缺少字段: ${key}`)
  return { ok: errors.length === 0, errors }
}

export const validateStaffSubmitEnvelope = (body: Record<string, unknown>): ValidateResult => {
  if (!body.identity || !body.report) {
    return { ok: false, errors: ['请求体必须为 { identity, report } 结构（与联调验收包一致）。'] }
  }
  return validateBasicStaffSchema(body)
}
