export const cnRisk = (level: string) => {
  switch (level) {
    case 'high':
      return '高'
    case 'medium':
      return '中'
    case 'low':
      return '低'
    default:
      return level
  }
}

export const statusBadgeClass = (status: string) => {
  switch (status) {
    case 'completed':
      return 'bg-emerald-500/20 text-emerald-300 border-emerald-400/40'
    case 'in_progress':
      return 'bg-cyan-500/20 text-cyan-300 border-cyan-400/40'
    case 'blocked':
      return 'bg-rose-500/20 text-rose-300 border-rose-400/40'
    case 'pending':
      return 'bg-amber-500/20 text-amber-200 border-amber-400/40'
    default:
      return 'bg-slate-500/20 text-slate-300 border-slate-400/40'
  }
}

export const toneDotClass = (tone: 'green' | 'yellow' | 'red') => {
  if (tone === 'green') return 'bg-emerald-400'
  if (tone === 'yellow') return 'bg-amber-300'
  return 'bg-rose-400'
}
