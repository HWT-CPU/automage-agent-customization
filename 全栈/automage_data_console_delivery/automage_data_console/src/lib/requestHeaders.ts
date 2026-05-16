import { appEnv } from '../config/env'
import type { IdentityProfile } from '../config/identities'
import { createIdempotencyKey, createRequestId } from './idempotency'

export interface HeaderMeta {
  requestId: string
  idempotencyKey: string
  headers: Record<string, string>
}

function getJwtToken(): string | null {
  try {
    return localStorage.getItem('automage_access_token')
  } catch {
    return null
  }
}

export const buildHeaders = (identity: IdentityProfile, withIdem = true): HeaderMeta => {
  const requestId = createRequestId('automage')
  const idempotencyKey = createIdempotencyKey('automage')

  // JWT priority > shared Bearer token
  const jwtToken = getJwtToken()
  const authToken = jwtToken ? `Bearer ${jwtToken}` : `Bearer ${appEnv.authToken}`

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    Authorization: authToken,
    'X-User-Id': identity.userId,
    'X-Role': identity.role,
    'X-Node-Id': identity.nodeId,
    'X-Level': identity.level,
    'X-Department-Id': identity.departmentId,
    'X-Request-Id': requestId,
  }

  if (identity.role !== 'executive') {
    headers['X-Manager-Node-Id'] = identity.managerNodeId
  }

  if (withIdem) headers['Idempotency-Key'] = idempotencyKey
  return { requestId, idempotencyKey, headers }
}
