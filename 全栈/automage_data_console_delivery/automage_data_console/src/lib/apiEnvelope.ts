export type ApiEnvelope<T = unknown> = {
  code: number
  data: T
  msg?: string
}

export function unwrapApiBody(json: unknown): { data: unknown; code?: number; msg?: string; isEnvelope: boolean } {
  if (json && typeof json === 'object' && 'data' in json && 'code' in json) {
    const env = json as ApiEnvelope
    return { data: env.data, code: env.code, msg: env.msg, isEnvelope: true }
  }
  return { data: json, isEnvelope: false }
}
