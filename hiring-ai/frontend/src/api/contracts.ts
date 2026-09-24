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
