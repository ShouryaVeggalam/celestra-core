import { useState, type FormEvent } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { hiringApi, setOrganizationId } from '../api/hiringApi'
import { useAuth } from '../auth/AuthProvider'

export function JoinPage() {
  const auth = useAuth()
  const navigate = useNavigate()
  const [code, setCode] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  if (auth.mode === 'firebase' && !auth.loading && !auth.firebaseUser) {
    return <Navigate to="/login" replace />
  }

  async function onSubmit(event: FormEvent) {
    event.preventDefault()
    setBusy(true)
    setError(null)
    try {
      const result = await hiringApi.redeemInvite(code.trim())
      setOrganizationId(result.organization_id)
      await auth.refreshMe()
      navigate('/workspace')
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Invite could not be redeemed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <p className="auth-eyebrow">Hiring AI</p>
        <h1>Join organization</h1>
        <p className="auth-lead">Enter the invite code your admin shared with you.</p>
        {error ? <p className="auth-error" role="alert">{error}</p> : null}
        <form className="auth-form" onSubmit={(event) => void onSubmit(event)}>
          <label>
            <span>Invite code</span>
            <input
              value={code}
              onChange={(event) => setCode(event.target.value)}
              placeholder="ABCD1234"
              aria-label="Invite code"
              required
            />
          </label>
          <button type="submit" disabled={busy}>
            {busy ? 'Joining…' : 'Redeem invite'}
          </button>
        </form>
        <p className="auth-switch">
          <Link to="/login">Back to sign in</Link>
        </p>
      </div>
    </div>
  )
}
