interface Props {
  mode: 'demo' | 'api'
}

export function SystemStatusBar({ mode }: Props) {
  const isApi = mode === 'api'
  return (
    <span
      className={`rounded-full border px-3 py-1 text-xs font-semibold ${
        isApi
          ? 'border-emerald-300 bg-emerald-50 text-emerald-700'
          : 'border-amber-300 bg-amber-50 text-amber-700'
      }`}
    >
      {isApi ? 'MVP Real API Passed' : 'Demo Mode'}
    </span>
  )
}
