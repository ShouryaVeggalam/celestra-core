import { useState, type FormEvent } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { hiringApi, setOrganizationId } from '../api/hiringApi'
import { useAuth } from '../auth/AuthProvider'

function slugify(value: string) {
  return value
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '')
    .slice(0, 100)
}

export function OnboardingPage() {
  const auth = useAuth()
  const navigate = useNavigate()
  const [name, setName] = useState('')
  const [slug, setSlug] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [inviteCode, setInviteCode] = useState<string | null>(null)

  if (auth.mode === 'firebase' && !auth.loading && !auth.firebaseUser) {
    return <Navigate to="/login" replace />
  }
  if (!auth.loading && auth.memberships.length > 0) {
    return <Navigate to="/workspace" replace />
  }

  async function onSubmit(event: FormEvent) {
    event.preventDefault()
    setBusy(true)
    setError(null)
    try {
      const created = await hiringApi.createOrganization({
        name: name.trim(),
        slug: (slug || slugify(name)).trim(),
      })
      setOrganizationId(created.organization_id)
      await auth.refreshMe()
      const invite = await hiringApi.createInviteCode(created.organization_id, 'member')
      setInviteCode(invite.code)
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Organization could not be created')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <p className="auth-eyebrow">Hiring AI</p>
        <h1>Create your organization</h1>
        <p className="auth-lead">You become the owner. Invite recruiters after setup.</p>
        {error ? <p className="auth-error" role="alert">{error}</p> : null}
        {inviteCode ? (
          <div className="auth-success">
            <p>
              Organization ready. Share this invite code with your client recruiters:{' '}
              <strong>{inviteCode}</strong>
            </p>
            <button type="button" onClick={() => navigate('/workspace')}>
              Continue to workspace
            </button>
          </div>
        ) : (
          <form className="auth-form" onSubmit={(event) => void onSubmit(event)}>
            <label>
              <span>Organization name</span>
              <input
                value={name}
                onChange={(event) => {
                  setName(event.target.value)
                  if (!slug) setSlug(slugify(event.target.value))
                }}
                required
              />
            </label>
            <label>
              <span>Slug</span>
              <input value={slug} onChange={(event) => setSlug(event.target.value)} required />
            </label>
            <button type="submit" disabled={busy}>
              {busy ? 'Creating…' : 'Create organization'}
            </button>
          </form>
        )}
      </div>
    </div>
  )
}
