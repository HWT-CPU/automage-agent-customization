export interface ApiErrorDisplay {
  title: string
  suggestion: string
}

export const mapError = (status: number): ApiErrorDisplay => {
  if (status === 401) {
    return { title: '401 鉴权失败', suggestion: '请检查 Settings 中的 Token 配置，当前草稿不会丢失。' }
  }
  if (status === 403) {
    return { title: '403 权限不足', suggestion: '请确认当前角色与目标操作是否匹配。' }
  }
  if (status === 409) {
    return { title: '409 幂等冲突', suggestion: '可复用既有记录或重新生成幂等键后重试。' }
  }
  if (status === 422) {
    return { title: '422 Schema 校验失败', suggestion: '请按字段级错误修正 payload 后再提交。' }
  }
  if (status >= 500) {
    return { title: '5xx 后端异常', suggestion: '当前建议切回 Demo 模式并保留请求日志。' }
  }
  return { title: `HTTP ${status}`, suggestion: '请查看请求与响应详情。' }
}
