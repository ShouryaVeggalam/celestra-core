import { useCallback, useEffect, useState } from 'react'
import type { InviteCodeListItem } from '../api/contracts'
import { HiringApiError, hiringApi } from '../api/hiringApi'
import { useAuth } from '../auth/AuthProvider'

export function SettingsPage() {
  const auth = useAuth()
  const orgId = auth.orgId
  const membership =
    auth.memberships.find((item) => item.organization_id === orgId) ?? auth.memberships[0]
  const canManage = membership?.role === 'owner' || membership?.role === 'admin'
  const [invites, setInvites] = useState<InviteCodeListItem[]>([])
  const [createdCode, setCreatedCode] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  const load = useCallback(async () => {
    if (!canManage || !orgId) {
      setInvites([])
      return
    }
    try {
      const result = await hiringApi.listInviteCodes(orgId)
      setInvites(result.items)
    } catch (caught) {
      setError(caught instanceof HiringApiError ? caught.message : 'Could not load invites')
    }
  }, [canManage, orgId])

  useEffect(() => {
    void load()
  }, [load])

  async function createInvite(role: 'admin' | 'member') {
    if (!orgId) return
    setBusy(true)
    setError(null)
    try {
      const created = await hiringApi.createInviteCode(orgId, role)
      setCreatedCode(created.code)
      await load()
    } catch (caught) {
      setError(caught instanceof HiringApiError ? caught.message : 'Invite failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <p className="auth-eyebrow">Organization</p>
          <h1>Settings</h1>
          <p>Invite recruiters to this org. Share the hosted app URL plus a one-time invite code.</p>
        </div>
      </header>
      {error ? <p className="auth-error">{error}</p> : null}
      <section className="panel">
        <h2>{membership?.organization_name ?? 'Organization'}</h2>
        <p className="muted">
          You are signed in as {auth.me?.email || auth.me?.display_name} ({membership?.role ?? 'member'}).
        </p>
        {canManage ? (
          <div className="button-row">
            <button type="button" disabled={busy} onClick={() => void createInvite('member')}>
              Create member invite
            </button>
            <button type="button" className="secondary" disabled={busy} onClick={() => void createInvite('admin')}>
              Create admin invite
            </button>
          </div>
        ) : (
          <p className="muted">Only owners and admins can create invites.</p>
        )}
        {createdCode ? (
          <p className="auth-success">
            Share this code now (shown once): <strong>{createdCode}</strong>
          </p>
        ) : null}
        <ul className="stack-list">
          {invites.map((invite) => (
            <li key={invite.id}>
              <strong>{invite.role}</strong> · {invite.status}
              <p className="muted">Expires {new Date(invite.expires_at).toLocaleString()}</p>
            </li>
          ))}
        </ul>
      </section>
    </div>
  )
}
