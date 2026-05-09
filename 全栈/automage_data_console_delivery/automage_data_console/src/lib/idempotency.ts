import { nanoid } from 'nanoid'

export const createRequestId = (prefix = 'req') => `${prefix}_${Date.now()}_${nanoid(6)}`

export const createIdempotencyKey = (scope = 'idem') => `${scope}_${Date.now()}_${nanoid(8)}`
