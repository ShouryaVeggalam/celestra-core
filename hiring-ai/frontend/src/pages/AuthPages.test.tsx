import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const { getMe, redeemInvite, createOrganization, listJobs, listCandidates } = vi.hoisted(() => ({
  getMe: vi.fn(),
  redeemInvite: vi.fn(),
  createOrganization: vi.fn(),
  listJobs: vi.fn(),
  listCandidates: vi.fn(),
}))

vi.mock('../api/hiringApi', async () => {
  const actual = await vi.importActual<typeof import('../api/hiringApi')>('../api/hiringApi')
  return {
    ...actual,
    hiringApi: {
      getMe,
      redeemInvite,
      createOrganization,
      createInviteCode: vi.fn().mockResolvedValue({ code: 'ABCD1234' }),
      listInviteCodes: vi.fn().mockResolvedValue({ items: [], total: 0 }),
      listJobs,
      listCandidates,
      createJob: vi.fn(),
      createCandidate: vi.fn(),
      createSourcingProject: vi.fn(),
      discoverTalent: vi.fn(),
      importSourcingCsv: vi.fn(),
      importDiscovery: vi.fn(),
    },
  }
})

vi.mock('../config/hiringApiBaseUrl', () => ({
  authMode: () => 'dev' as const,
  hiringApiBaseUrl: () => '',
  hiringOrgId: () => 'org-demo',
  hiringUserId: () => 'user-demo',
  firebaseConfig: () => ({}),
}))

import { AuthProvider } from '../auth/AuthProvider'
import { JoinPage } from '../pages/JoinPage'
import { AppRoutes } from '../routes/AppRoutes'

describe('auth frontend', () => {
  beforeEach(() => {
    getMe.mockReset()
    redeemInvite.mockReset()
    createOrganization.mockReset()
    listJobs.mockReset()
    listCandidates.mockReset()
    localStorage.clear()
    listJobs.mockResolvedValue({ items: [], total: 0 })
    listCandidates.mockResolvedValue({ items: [], total: 0 })
    getMe.mockResolvedValue({
      user_id: 'user-demo',
      email: 'demo@hiring.local',
      display_name: 'Demo Recruiter',
      memberships: [
        {
          organization_id: 'org-demo',
          organization_name: 'Hiring AI Demo',
          organization_slug: 'hiring-demo',
          membership_id: 'mem-1',
          role: 'owner',
        },
      ],
    })
  })

  it('loads workspace shell in dev mode without Firebase login', async () => {
    render(
      <MemoryRouter initialEntries={['/workspace']}>
        <AuthProvider>
          <AppRoutes />
        </AuthProvider>
      </MemoryRouter>,
    )
    expect(await screen.findByText(/Good (morning|afternoon|evening), Demo\./i)).toBeInTheDocument()
    expect(screen.getByText('Priority Queue')).toBeInTheDocument()
    expect(screen.getByText('Human review required')).toBeInTheDocument()
    expect(screen.getAllByText('Demo Recruiter').length).toBeGreaterThan(0)
    expect(screen.getByRole('link', { name: 'Workspace' })).toHaveClass('active')
  })

  it('redeems invite codes on join page', async () => {
    redeemInvite.mockResolvedValue({
      organization_id: 'org-2',
      organization_name: 'Client Co',
      membership_id: 'mem-2',
      role: 'member',
    })
    const user = userEvent.setup()
    render(
      <MemoryRouter initialEntries={['/join']}>
        <AuthProvider>
          <JoinPage />
        </AuthProvider>
      </MemoryRouter>,
    )
    await user.type(screen.getByLabelText('Invite code'), 'ZZZZ9999')
    await user.click(screen.getByRole('button', { name: 'Redeem invite' }))
    await waitFor(() => expect(redeemInvite).toHaveBeenCalledWith('ZZZZ9999'))
  })
})
