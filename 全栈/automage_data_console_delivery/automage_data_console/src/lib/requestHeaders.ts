import { appEnv } from '../config/env'
import type { IdentityProfile } from '../config/identities'
import { createIdempotencyKey, createRequestId } from './idempotency'

export interface HeaderMeta {
  requestId: string
  idempotencyKey: string
  headers: Record<string, string>
}

export const buildHeaders = (identity: IdentityProfile, withIdem = true): HeaderMeta => {
  const requestId = createRequestId('automage')
  const idempotencyKey = createIdempotencyKey('automage')
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    Authorization: `Bearer ${appEnv.authToken}`,
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
