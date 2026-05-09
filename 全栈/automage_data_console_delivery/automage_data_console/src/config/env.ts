const env = import.meta.env

export const appEnv = {
  apiBase: env.VITE_AUTOMAGE_API_BASE ?? 'http://localhost:8000',
  authToken: env.VITE_AUTOMAGE_AUTH_TOKEN ?? '',
  demoMode: (env.VITE_AUTOMAGE_DEMO_MODE ?? 'false') === 'true',
  enableRealWrite: (env.VITE_AUTOMAGE_ENABLE_REAL_WRITE ?? 'false') === 'true',
  defaultOrgId: env.VITE_AUTOMAGE_DEFAULT_ORG_ID ?? 'org_automage_mvp',
  defaultDepartmentId: env.VITE_AUTOMAGE_DEFAULT_DEPARTMENT_ID ?? 'dept_mvp_core',
}
