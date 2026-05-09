import { create } from 'zustand'

interface ExecutiveSessionState {
  summaryPublicId: string
  lastDreamResult: unknown | null
  setSummaryPublicId: (id: string) => void
  setLastDreamResult: (payload: unknown | null) => void
}

export const useExecutiveSessionStore = create<ExecutiveSessionState>((set) => ({
  summaryPublicId: '',
  lastDreamResult: null,
  setSummaryPublicId: (summaryPublicId) => set({ summaryPublicId }),
  setLastDreamResult: (lastDreamResult) => set({ lastDreamResult }),
}))
