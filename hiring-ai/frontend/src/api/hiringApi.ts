import { hiringApiBaseUrl, hiringOrgId, hiringUserId, authMode } from '../config/hiringApiBaseUrl'
import type { MeResponse, OrganizationCreated, RedeemInviteResponse } from './contracts'

export class HiringApiError extends Error {
  readonly status: number
  readonly code: string

  constructor(message: string, status = 0, code = 'request_failed') {
    super(message)
    this.name = 'HiringApiError'
    this.status = status
    this.code = code
  }
}

type TokenProvider = () => Promise<string | null>

let tokenProvider: TokenProvider | null = null
let orgIdOverride: string | null = null

export function setAuthTokenProvider(provider: TokenProvider | null) {
  tokenProvider = provider
}

export function setOrganizationId(orgId: string | null) {
  orgIdOverride = orgId
  if (orgId) localStorage.setItem('hiring_org_id', orgId)
  else localStorage.removeItem('hiring_org_id')
}

export function getOrganizationId(): string {
  if (orgIdOverride) return orgIdOverride
  const stored = localStorage.getItem('hiring_org_id')
  if (stored) return stored
  return hiringOrgId()
}

async function parseError(response: Response): Promise<HiringApiError> {
  try {
    const body = await response.json()
    const detail = body?.detail
    if (typeof detail === 'string') return new HiringApiError(detail, response.status)
    if (detail && typeof detail === 'object') {
      return new HiringApiError(
        detail.message || 'Request failed',
        response.status,
        detail.code || 'request_failed',
      )
    }
  } catch {
    /* ignore */
  }
  return new HiringApiError(`Request failed (${response.status})`, response.status)
}

async function authHeaders(extra?: HeadersInit): Promise<Headers> {
  const headers = new Headers(extra)
  if (authMode() === 'firebase') {
    const token = tokenProvider ? await tokenProvider() : null
    if (!token) throw new HiringApiError('Sign in required.', 401, 'unauthenticated')
    headers.set('Authorization', `Bearer ${token}`)
  } else {
    headers.set('Authorization', `Bearer ${hiringUserId()}`)
  }
  const orgId = getOrganizationId()
  if (orgId) headers.set('X-Organization-Id', orgId)
  return headers
}

class HiringApi {
  private url(path: string) {
    return `${hiringApiBaseUrl()}${path}`
  }

  async getMe(): Promise<MeResponse> {
    const response = await fetch(this.url('/api/v1/auth/me'), {
      headers: await authHeaders(),
    })
    if (!response.ok) throw await parseError(response)
    return (await response.json()) as MeResponse
  }

  async createOrganization(body: { name: string; slug: string }): Promise<OrganizationCreated> {
    const response = await fetch(this.url('/api/v1/auth/organizations'), {
      method: 'POST',
      headers: await authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(body),
    })
    if (!response.ok) throw await parseError(response)
    return (await response.json()) as OrganizationCreated
  }

  async redeemInvite(code: string): Promise<RedeemInviteResponse> {
    const response = await fetch(this.url('/api/v1/invite-codes/redeem'), {
      method: 'POST',
      headers: await authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ code }),
    })
    if (!response.ok) throw await parseError(response)
    return (await response.json()) as RedeemInviteResponse
  }

  async createInviteCode(orgId: string, role: 'admin' | 'member'): Promise<{ code: string }> {
    const response = await fetch(this.url(`/api/v1/organizations/${orgId}/invite-codes`), {
      method: 'POST',
      headers: await authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ role }),
    })
    if (!response.ok) throw await parseError(response)
    return (await response.json()) as { code: string }
  }
}

export const hiringApi = new HiringApi()
