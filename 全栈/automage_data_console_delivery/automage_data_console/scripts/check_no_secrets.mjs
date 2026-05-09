import fs from 'node:fs'
import path from 'node:path'
import process from 'node:process'

const root = process.cwd()
const denyPatterns = [
  /postgres:\/\/[^/\s]+:[^@\s]+@/i,
  /VITE_AUTOMAGE_AUTH_TOKEN\s*=\s*.+/i,
  /password\s*[:=]\s*['"][^'"]+/i,
]

const ignore = new Set(['node_modules', '.git', 'dist'])
let violated = false

function walk(dir) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (ignore.has(entry.name)) continue
    const full = path.join(dir, entry.name)
    if (entry.isDirectory()) walk(full)
    else {
      const content = fs.readFileSync(full, 'utf8')
      for (const pattern of denyPatterns) {
        if (pattern.test(content)) {
          violated = true
          console.error(`[SECRET_CHECK] potential secret in ${full}`)
          break
        }
      }
    }
  }
}

walk(root)
if (violated) process.exit(1)
console.log('[SECRET_CHECK] PASS')
