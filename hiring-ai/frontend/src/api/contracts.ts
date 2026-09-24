export type Membership = {
  organization_id: string
  organization_name: string
  organization_slug: string
  membership_id: string
  role: string
}

export type MeResponse = {
  user_id: string
  email: string | null
  display_name: string | null
  memberships: Membership[]
}

export type OrganizationCreated = {
  organization_id: string
  organization_name: string
  organization_slug: string
  membership_id: string
  role: string
}

export type RedeemInviteResponse = {
  organization_id: string
  organization_name: string
  membership_id: string
  role: string
}

export type Job = {
  id: string
  org_id: string
  title: string
  department: string | null
  location: string | null
  description: string | null
  status: string
  created_at: string
}

export type Candidate = {
  id: string
  org_id: string
  first_name: string
  last_name: string
  email: string | null
  headline: string | null
  location: string | null
  linkedin_url: string | null
  github_url: string | null
  portfolio_url: string | null
  summary: string | null
  skills: string[]
  status: string
  sourced_from_discovery_id: string | null
  created_at: string
}

export type CandidateDiscovery = {
  id: string
  organization_id: string
  sourcing_project_id: string
  full_name: string
  headline: string | null
  company: string | null
  location: string | null
  profile_url: string | null
  source: string
  summary: string | null
  skills: string[]
  confidence: number
  status: string
  imported_candidate_id: string | null
  created_at: string
}

export type DiscoverResponse = {
  project_id: string
  discoveries: CandidateDiscovery[]
}

export type SourcingProject = {
  id: string
  organization_id: string
  name: string
  job_id: string | null
  created_by_user_id: string
  created_at: string
  discoveries: CandidateDiscovery[]
}

export type InviteCodeListItem = {
  id: string
  organization_id: string
  role: string
  status: string
  expires_at: string
  used_at: string | null
  used_by_user_id: string | null
  created_by_user_id: string
  created_at: string
}

export type MatchDraft = {
  id: string
  org_id: string
  job_id: string
  candidate_id: string
  score: number
  summary: string | null
  strengths: string[]
  gaps: string[]
  evidence: string[]
  model: string | null
  created_at: string
}
