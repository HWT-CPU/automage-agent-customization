import { create } from 'zustand'
import { appEnv } from '../config/env'

export interface ApiLogItem {
  timestamp: string
  method: string
  path: string
  status: number
  role: string
  requestId: string
  idempotencyKey: string
  durationMs: number
  fallback: boolean
  errorMessage?: string
}

interface RuntimeState {
  demoMode: boolean
  enableRealWrite: boolean
  lastRequestPayload?: unknown
  lastResponsePayload?: unknown
  apiLogs: ApiLogItem[]
  setDemoMode: (demoMode: boolean) => void
  setEnableRealWrite: (enable: boolean) => void
  pushApiLog: (log: ApiLogItem) => void
  setLastPayloads: (req: unknown, res: unknown) => void
}

export const useRuntimeStore = create<RuntimeState>((set) => ({
  demoMode: appEnv.demoMode,
  enableRealWrite: appEnv.enableRealWrite,
  apiLogs: [],
  setDemoMode: (demoMode) => set({ demoMode }),
  setEnableRealWrite: (enableRealWrite) => set({ enableRealWrite }),
  pushApiLog: (log) => set((state) => ({ apiLogs: [log, ...state.apiLogs].slice(0, 120) })),
  setLastPayloads: (req, res) => set({ lastRequestPayload: req, lastResponsePayload: res }),
}))
