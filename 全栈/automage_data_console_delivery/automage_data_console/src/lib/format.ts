export const fmtJson = (value: unknown) => JSON.stringify(value, null, 2)

export const toLocalTime = (iso: string) => {
  try {
    return new Date(iso).toLocaleString('zh-CN')
  } catch {
    return iso
  }
}

export const statusTone = (status: string) => {
  if (['passed', 'completed', 'ok', '正常'].includes(status))
    return 'border border-emerald-200 bg-emerald-50 text-emerald-800'
  if (['running', 'in_progress'].includes(status))
    return 'border border-sky-200 bg-sky-50 text-sky-900'
  if (['failed', 'error', 'blocked'].includes(status))
    return 'border border-rose-200 bg-rose-50 text-rose-800'
  if (['fallback', 'needs human confirmation'].includes(status))
    return 'border border-amber-200 bg-amber-50 text-amber-900'
  return 'border border-slate-200 bg-slate-50 text-slate-800'
}
