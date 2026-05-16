import {
  decisionCardDemo,
  integrationStatus,
  managerSummaryDemo,
  staffReportDemo,
  taskBoardDemo,
} from '../data/demoData'

const API_BASE = import.meta.env.VITE_AUTOMAGE_API_BASE ?? 'http://localhost:8000'
const AUTH_TOKEN = import.meta.env.VITE_AUTOMAGE_AUTH_TOKEN ?? 'dev-token'
const DEMO_MODE = String(import.meta.env.VITE_AUTOMAGE_DEMO_MODE ?? 'true') === 'true'

const withAuth = {
  'Content-Type': 'application/json',
  Authorization: `Bearer ${AUTH_TOKEN}`,
}

async function safeGet<T>(path: string, fallback: T): Promise<T> {
  if (DEMO_MODE) return fallback
  try {
    const res = await fetch(`${API_BASE}${path}`, { headers: withAuth })
    if (!res.ok) throw new Error(`${path} failed`)
    return (await res.json()) as T
  } catch {
    return fallback
  }
}

export async function fetchLandingData() {
  const [healthz, staff, manager, tasks] = await Promise.all([
    safeGet<{ status?: string }>('/healthz', { status: 'UP' }),
    safeGet('/api/v1/report/staff', staffReportDemo),
    safeGet('/api/v1/report/manager', managerSummaryDemo),
    safeGet('/api/v1/tasks', taskBoardDemo),
  ])

  return {
    healthz,
    staff,
    manager,
    tasks,
    decision: decisionCardDemo,
    integration: {
      ...integrationStatus,
      healthz: Boolean(healthz?.status),
    },
    mode: (DEMO_MODE ? 'demo' : 'api') as 'demo' | 'api',
    apiBase: API_BASE,
  }
}
