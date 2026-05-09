export const fmtJson = (value: unknown) => JSON.stringify(value, null, 2)

export const toLocalTime = (iso: string) => {
  try {
    return new Date(iso).toLocaleString('zh-CN')
  } catch {
    return iso
  }
}

export const statusTone = (status: string) => {
  if (['passed', 'completed', 'ok', '正常'].includes(status)) return 'bg-emerald-100 text-emerald-700'
  if (['running', 'in_progress'].includes(status)) return 'bg-cyan-100 text-cyan-700'
  if (['failed', 'error', 'blocked'].includes(status)) return 'bg-rose-100 text-rose-700'
  if (['fallback', 'needs human confirmation'].includes(status)) return 'bg-amber-100 text-amber-800'
  return 'bg-slate-100 text-slate-700'
}
