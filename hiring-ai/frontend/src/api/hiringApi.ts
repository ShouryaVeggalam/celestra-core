import { hiringApiBaseUrl, hiringOrgId, hiringUserId, authMode } from '../config/hiringApiBaseUrl'
import type {
  Candidate,
  DiscoverResponse,
  InviteCodeListItem,
  Job,
  MeResponse,
  OrganizationCreated,
  RedeemInviteResponse,
  SourcingProject,
} from './contracts'

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
    const response = await fetch(this.url('/api/v1/auth/me'), { headers: await authHeaders() })
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

  async listInviteCodes(orgId: string): Promise<{ items: InviteCodeListItem[]; total: number }> {
    const response = await fetch(this.url(`/api/v1/organizations/${orgId}/invite-codes`), {
      headers: await authHeaders(),
    })
    if (!response.ok) throw await parseError(response)
    return (await response.json()) as { items: InviteCodeListItem[]; total: number }
  }

  async listJobs(opts?: { limit?: number; offset?: number }): Promise<{ items: Job[]; total: number }> {
    const limit = opts?.limit ?? 50
    const offset = opts?.offset ?? 0
    const response = await fetch(this.url(`/api/v1/jobs?limit=${limit}&offset=${offset}`), {
      headers: await authHeaders(),
    })
    if (!response.ok) throw await parseError(response)
    return (await response.json()) as { items: Job[]; total: number }
  }

  async createJob(body: {
    title: string
    department?: string
    location?: string
    description?: string
  }): Promise<Job> {
    const response = await fetch(this.url('/api/v1/jobs'), {
      method: 'POST',
      headers: await authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(body),
    })
    if (!response.ok) throw await parseError(response)
    return (await response.json()) as Job
  }

  async listCandidates(opts?: {
    limit?: number
    offset?: number
  }): Promise<{ items: Candidate[]; total: number }> {
    const limit = opts?.limit ?? 50
    const offset = opts?.offset ?? 0
    const response = await fetch(this.url(`/api/v1/candidates?limit=${limit}&offset=${offset}`), {
      headers: await authHeaders(),
    })
    if (!response.ok) throw await parseError(response)
    return (await response.json()) as { items: Candidate[]; total: number }
  }

  async createCandidate(body: {
    first_name: string
    last_name: string
    email?: string
    headline?: string
    location?: string
    summary?: string
    skills?: string[]
  }): Promise<Candidate> {
    const response = await fetch(this.url('/api/v1/candidates'), {
      method: 'POST',
      headers: await authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(body),
    })
    if (!response.ok) throw await parseError(response)
    return (await response.json()) as Candidate
  }

  async updateCandidateStatus(candidateId: string, status: string): Promise<Candidate> {
    const response = await fetch(this.url(`/api/v1/candidates/${candidateId}/status`), {
      method: 'POST',
      headers: await authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ status }),
    })
    if (!response.ok) throw await parseError(response)
    return (await response.json()) as Candidate
  }

  async createSourcingProject(body: { name: string; job_id?: string | null }): Promise<SourcingProject> {
    const response = await fetch(this.url('/api/v1/source/projects'), {
      method: 'POST',
      headers: await authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(body),
    })
    if (!response.ok) throw await parseError(response)
    return (await response.json()) as SourcingProject
  }

  async discoverTalent(body: {
    project_id: string
    query: string
    limit: number
  }): Promise<DiscoverResponse> {
    const response = await fetch(this.url('/api/v1/source/discover'), {
      method: 'POST',
      headers: await authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(body),
    })
    if (!response.ok) throw await parseError(response)
    return (await response.json()) as DiscoverResponse
  }

  async importSourcingCsv(projectId: string, file: File): Promise<DiscoverResponse> {
    const form = new FormData()
    form.append('file', file)
    const response = await fetch(this.url(`/api/v1/source/projects/${projectId}/import-csv`), {
      method: 'POST',
      headers: await authHeaders(),
      body: form,
    })
    if (!response.ok) throw await parseError(response)
    return (await response.json()) as DiscoverResponse
  }

  async importDiscovery(discoveryId: string): Promise<{
    discovery: DiscoverResponse['discoveries'][number]
    candidate_id: string
    candidate_first_name: string
    candidate_last_name: string
  }> {
    const response = await fetch(this.url(`/api/v1/source/import/${discoveryId}`), {
      method: 'POST',
      headers: await authHeaders(),
    })
    if (!response.ok) throw await parseError(response)
    return await response.json()
  }
}

export const hiringApi = new HiringApi()
