import { useState, type FormEvent } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthProvider'

export function LoginPage() {
  const auth = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [mode, setMode] = useState<'signin' | 'signup'>('signin')

  if (auth.mode === 'dev') {
    return <Navigate to="/workspace" replace />
  }

  if (!auth.loading && auth.firebaseUser) {
    if (auth.memberships.length === 0) return <Navigate to="/onboarding" replace />
    return <Navigate to="/workspace" replace />
  }

  async function onSubmit(event: FormEvent) {
    event.preventDefault()
    setBusy(true)
    setError(null)
    try {
      if (mode === 'signin') await auth.signInEmail(email, password)
      else await auth.signUpEmail(email, password)
      navigate('/workspace')
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Sign-in failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <p className="auth-eyebrow">Hiring AI</p>
        <h1>{mode === 'signin' ? 'Sign in' : 'Create account'}</h1>
        <p className="auth-lead">Recruiters sign in to hire through your organization.</p>
        {error ? <p className="auth-error" role="alert">{error}</p> : null}
        <form className="auth-form" onSubmit={(event) => void onSubmit(event)}>
          <label>
            <span>Email</span>
            <input
              type="email"
              autoComplete="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />
          </label>
          <label>
            <span>Password</span>
            <input
              type="password"
              autoComplete={mode === 'signin' ? 'current-password' : 'new-password'}
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
              minLength={6}
            />
          </label>
          <button type="submit" disabled={busy}>
            {busy ? 'Working…' : mode === 'signin' ? 'Sign in' : 'Create account'}
          </button>
        </form>
        <button
          type="button"
          className="auth-secondary"
          disabled={busy}
          onClick={() => void auth.signInGoogle().then(() => navigate('/workspace')).catch((err) => setError(err.message))}
        >
          Continue with Google
        </button>
        <p className="auth-switch">
          {mode === 'signin' ? (
            <>
              New here?{' '}
              <button type="button" onClick={() => setMode('signup')}>
                Create an account
              </button>
            </>
          ) : (
            <>
              Already have an account?{' '}
              <button type="button" onClick={() => setMode('signin')}>
                Sign in
              </button>
            </>
          )}
        </p>
        <p className="auth-switch">
          Have an invite? <Link to="/join">Join an organization</Link>
        </p>
      </div>
    </div>
  )
}
