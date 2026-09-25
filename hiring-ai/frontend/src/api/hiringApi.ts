import { hiringApiBaseUrl, hiringOrgId, hiringUserId, authMode } from '../config/hiringApiBaseUrl'
import type {
  AgentArtifact,
  AnalyticsSummary,
  Candidate,
  DiscoverResponse,
  HiringDocument,
  IntegrationLink,
  IntegrationsResponse,
  InterviewSession,
  InviteCodeListItem,
  Job,
  MatchDraft,
  MeResponse,
  OrganizationCreated,
  PortalAccess,
  RedeemInviteResponse,
  Referral,
  ReviewScorecard,
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

/** Active org for API calls. Never invents a demo org in Firebase mode. */
export function getOrganizationId(): string | null {
  if (orgIdOverride) return orgIdOverride
  const stored = localStorage.getItem('hiring_org_id')
  if (stored) return stored
  if (authMode() === 'dev') return hiringOrgId()
  return null
}

export function resolveOrganizationId(membershipOrgIds: string[]): string | null {
  const current = getOrganizationId()
  if (current && membershipOrgIds.includes(current)) return current
  const next = membershipOrgIds[0] ?? null
  setOrganizationId(next)
  return next
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

  async createMatch(body: { job_id: string; candidate_id: string }): Promise<MatchDraft> {
    const response = await fetch(this.url('/api/v1/matches'), {
      method: 'POST',
      headers: await authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(body),
    })
    if (!response.ok) throw await parseError(response)
    return (await response.json()) as MatchDraft
  }

  async structureJob(text: string): Promise<{
    title: string
    department: string | null
    location: string | null
    description: string | null
  }> {
    const response = await fetch(this.url('/api/v1/ai/structure-job'), {
      method: 'POST',
      headers: await authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ text }),
    })
    if (!response.ok) throw await parseError(response)
    return await response.json()
  }

  async structureCandidate(text: string): Promise<{
    first_name: string
    last_name: string
    headline: string | null
    location: string | null
    summary: string | null
    skills: string[]
  }> {
    const response = await fetch(this.url('/api/v1/ai/structure-candidate'), {
      method: 'POST',
      headers: await authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ text }),
    })
    if (!response.ok) throw await parseError(response)
    return await response.json()
  }

  async listArtifacts(kind?: string): Promise<{ items: AgentArtifact[] }> {
    const qs = kind ? `?kind=${encodeURIComponent(kind)}` : ''
    const response = await fetch(this.url(`/api/v1/agents/artifacts${qs}`), {
      headers: await authHeaders(),
    })
    if (!response.ok) throw await parseError(response)
    return (await response.json()) as { items: AgentArtifact[] }
  }

  async draftOutreach(body: {
    candidate_id: string
    job_id?: string | null
    extra_context?: string
  }): Promise<AgentArtifact> {
    const response = await fetch(this.url('/api/v1/agents/outreach'), {
      method: 'POST',
      headers: await authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(body),
    })
    if (!response.ok) throw await parseError(response)
    return (await response.json()) as AgentArtifact
  }

  async draftSkills(body: { candidate_id: string }): Promise<AgentArtifact> {
    const response = await fetch(this.url('/api/v1/agents/skills'), {
      method: 'POST',
      headers: await authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(body),
    })
    if (!response.ok) throw await parseError(response)
    return (await response.json()) as AgentArtifact
  }

  async draftCompensation(body: {
    job_id: string
    extra_context?: string
  }): Promise<AgentArtifact> {
    const response = await fetch(this.url('/api/v1/agents/compensation'), {
      method: 'POST',
      headers: await authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(body),
    })
    if (!response.ok) throw await parseError(response)
    return (await response.json()) as AgentArtifact
  }

  async draftForecast(body?: { topic?: string }): Promise<AgentArtifact> {
    const response = await fetch(this.url('/api/v1/agents/forecast'), {
      method: 'POST',
      headers: await authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(body ?? {}),
    })
    if (!response.ok) throw await parseError(response)
    return (await response.json()) as AgentArtifact
  }

  async draftPlaybook(body: { topic?: string; extra_context?: string }): Promise<AgentArtifact> {
    const response = await fetch(this.url('/api/v1/agents/playbooks'), {
      method: 'POST',
      headers: await authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(body),
    })
    if (!response.ok) throw await parseError(response)
    return (await response.json()) as AgentArtifact
  }

  async draftHiringChief(body?: { topic?: string }): Promise<AgentArtifact> {
    const response = await fetch(this.url('/api/v1/agents/hiring-chief'), {
      method: 'POST',
      headers: await authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(body ?? {}),
    })
    if (!response.ok) throw await parseError(response)
    return (await response.json()) as AgentArtifact
  }

  async draftAutonomousPrep(body?: {
    topic?: string
    extra_context?: string
    job_id?: string | null
    candidate_id?: string | null
  }): Promise<AgentArtifact> {
    const response = await fetch(this.url('/api/v1/agents/autonomous-prep'), {
      method: 'POST',
      headers: await authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(body ?? {}),
    })
    if (!response.ok) throw await parseError(response)
    return (await response.json()) as AgentArtifact
  }

  async listReviews(): Promise<{ items: ReviewScorecard[] }> {
    const response = await fetch(this.url('/api/v1/reviews'), { headers: await authHeaders() })
    if (!response.ok) throw await parseError(response)
    return (await response.json()) as { items: ReviewScorecard[] }
  }

  async createReview(body: {
    candidate_id: string
    job_id?: string | null
    overall_score: number
    scores?: Record<string, number>
    notes?: string
    recommendation?: string
  }): Promise<ReviewScorecard> {
    const response = await fetch(this.url('/api/v1/reviews'), {
      method: 'POST',
      headers: await authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(body),
    })
    if (!response.ok) throw await parseError(response)
    return (await response.json()) as ReviewScorecard
  }

  async listInterviews(): Promise<{ items: InterviewSession[] }> {
    const response = await fetch(this.url('/api/v1/interviews'), { headers: await authHeaders() })
    if (!response.ok) throw await parseError(response)
    return (await response.json()) as { items: InterviewSession[] }
  }

  async createInterview(body: {
    candidate_id: string
    job_id?: string | null
    title: string
    notes?: string
    generate_with_ai?: boolean
  }): Promise<InterviewSession> {
    const response = await fetch(this.url('/api/v1/interviews'), {
      method: 'POST',
      headers: await authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(body),
    })
    if (!response.ok) throw await parseError(response)
    return (await response.json()) as InterviewSession
  }

  async listReferrals(): Promise<{ items: Referral[] }> {
    const response = await fetch(this.url('/api/v1/referrals'), { headers: await authHeaders() })
    if (!response.ok) throw await parseError(response)
    return (await response.json()) as { items: Referral[] }
  }

  async createReferral(body: {
    referrer_name: string
    referrer_email?: string
    candidate_name: string
    candidate_email?: string
    job_id?: string | null
    notes?: string
    enrich_with_ai?: boolean
  }): Promise<Referral> {
    const response = await fetch(this.url('/api/v1/referrals'), {
      method: 'POST',
      headers: await authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(body),
    })
    if (!response.ok) throw await parseError(response)
    return (await response.json()) as Referral
  }

  async listDocuments(): Promise<{ items: HiringDocument[] }> {
    const response = await fetch(this.url('/api/v1/documents'), { headers: await authHeaders() })
    if (!response.ok) throw await parseError(response)
    return (await response.json()) as { items: HiringDocument[] }
  }

  async createDocument(body: {
    doc_type: 'hiring_brief' | 'offer_letter'
    job_id?: string | null
    candidate_id?: string | null
    extra_context?: string
  }): Promise<HiringDocument> {
    const response = await fetch(this.url('/api/v1/documents'), {
      method: 'POST',
      headers: await authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(body),
    })
    if (!response.ok) throw await parseError(response)
    return (await response.json()) as HiringDocument
  }

  async listPortalAccess(): Promise<{ items: PortalAccess[] }> {
    const response = await fetch(this.url('/api/v1/candidate-portal'), {
      headers: await authHeaders(),
    })
    if (!response.ok) throw await parseError(response)
    return (await response.json()) as { items: PortalAccess[] }
  }

  async createPortalAccess(body: {
    candidate_id: string
    offer_title?: string
    offer_body?: string
  }): Promise<PortalAccess> {
    const response = await fetch(this.url('/api/v1/candidate-portal'), {
      method: 'POST',
      headers: await authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(body),
    })
    if (!response.ok) throw await parseError(response)
    return (await response.json()) as PortalAccess
  }

  async getPublicPortal(token: string): Promise<{
    token: string
    status: string
    offer_title: string | null
    offer_body: string | null
    candidate_name: string | null
    response_note: string | null
  }> {
    const response = await fetch(this.url(`/api/v1/candidate-portal/${encodeURIComponent(token)}`))
    if (!response.ok) throw await parseError(response)
    return await response.json()
  }

  async respondPublicPortal(
    token: string,
    body: { response_status: 'accepted' | 'declined' | 'maybe'; response_note?: string },
  ): Promise<{ token: string; response_status: string; responded_at: string | null }> {
    const response = await fetch(this.url(`/api/v1/candidate-portal/${encodeURIComponent(token)}/respond`), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    })
    if (!response.ok) throw await parseError(response)
    return await response.json()
  }

  async analyticsSummary(): Promise<AnalyticsSummary> {
    const response = await fetch(this.url('/api/v1/analytics/summary'), {
      headers: await authHeaders(),
    })
    if (!response.ok) throw await parseError(response)
    return (await response.json()) as AnalyticsSummary
  }

  async listIntegrations(): Promise<IntegrationsResponse> {
    const response = await fetch(this.url('/api/v1/integrations'), {
      headers: await authHeaders(),
    })
    if (!response.ok) throw await parseError(response)
    return (await response.json()) as IntegrationsResponse
  }

  async createIntegration(body: { provider: string; notes?: string }): Promise<IntegrationLink> {
    const response = await fetch(this.url('/api/v1/integrations'), {
      method: 'POST',
      headers: await authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(body),
    })
    if (!response.ok) throw await parseError(response)
    return (await response.json()) as IntegrationLink
  }
}

export const hiringApi = new HiringApi()
