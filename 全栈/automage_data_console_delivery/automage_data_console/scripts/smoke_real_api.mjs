import process from 'node:process'

const base = process.env.VITE_AUTOMAGE_API_BASE || 'http://localhost:8000'
const token = process.env.VITE_AUTOMAGE_AUTH_TOKEN || ''

const headers = {
  Authorization: `Bearer ${token}`,
  'X-User-Id': 'zhangsan',
  'X-Role': 'staff',
  'X-Node-Id': 'staff_agent_mvp_001',
  'X-Level': 'l1_staff',
  'X-Department-Id': 'dept_mvp_core',
  'X-Manager-Node-Id': 'manager_agent_mvp_001',
  'X-Request-Id': `smoke_${Date.now()}`,
  'Idempotency-Key': `smoke_${Date.now()}_idem`,
}

async function run() {
  const targets = ['/healthz', '/api/v1/tasks']
  for (const path of targets) {
    const res = await fetch(`${base}${path}`, { headers })
    const text = await res.text()
    console.log(`[SMOKE] ${path} -> ${res.status}`)
    console.log(text.slice(0, 300))
  }
}

run().catch((err) => {
  console.error('[SMOKE] failed', err)
  process.exit(1)
})
