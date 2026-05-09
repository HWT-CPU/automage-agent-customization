import { create } from 'zustand'

function todayIsoDate(): string {
  const d = new Date()
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

interface RunContextState {
  runDate: string
  setRunDate: (value: string) => void
}

export const useRunContextStore = create<RunContextState>((set) => ({
  runDate: todayIsoDate(),
  setRunDate: (runDate) => set({ runDate }),
}))
