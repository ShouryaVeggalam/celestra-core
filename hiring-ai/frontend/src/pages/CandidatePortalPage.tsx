import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { HiringApiError, hiringApi } from '../api/hiringApi'

type PortalView = {
  token: string
  status: string
  offer_title: string | null
  offer_body: string | null
  candidate_name: string | null
  response_note: string | null
}

export function CandidatePortalPage() {
  const { token = '' } = useParams()
  const [view, setView] = useState<PortalView | null>(null)
  const [note, setNote] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    let cancelled = false
    if (!token) return
    void hiringApi
      .getPublicPortal(token)
      .then((data) => {
        if (!cancelled) setView(data)
      })
      .catch((caught) => {
        if (!cancelled) {
          setError(caught instanceof HiringApiError ? caught.message : 'Portal not found')
        }
      })
    return () => {
      cancelled = true
    }
  }, [token])

  async function respond(status: 'accepted' | 'declined' | 'maybe') {
    if (!token) return
    setBusy(true)
    setError(null)
    try {
      const result = await hiringApi.respondPublicPortal(token, {
        response_status: status,
        response_note: note || undefined,
      })
      setView((current) =>
        current
          ? { ...current, status: result.response_status, response_note: note || current.response_note }
          : current,
      )
    } catch (caught) {
      setError(caught instanceof HiringApiError ? caught.message : 'Response failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card" style={{ width: 'min(560px, 100%)' }}>
        <p className="auth-eyebrow">Candidate portal</p>
        <h1>{view?.offer_title || 'Offer review'}</h1>
        {view?.candidate_name ? <p className="auth-lead">Hello, {view.candidate_name}.</p> : null}
        {error ? <p className="auth-error">{error}</p> : null}
        {view?.offer_body ? <p style={{ whiteSpace: 'pre-wrap' }}>{view.offer_body}</p> : null}
        {view ? (
          <p className="muted">
            Status: <strong>{view.status}</strong>
          </p>
        ) : (
          <p className="muted">Loading…</p>
        )}
        {view && view.status === 'pending' ? (
          <div className="auth-form">
            <label>
              <span>Note (optional)</span>
              <input value={note} onChange={(e) => setNote(e.target.value)} />
            </label>
            <div className="button-row">
              <button type="button" disabled={busy} onClick={() => void respond('accepted')}>
                Accept
              </button>
              <button
                type="button"
                className="secondary"
                disabled={busy}
                onClick={() => void respond('maybe')}
              >
                Maybe
              </button>
              <button
                type="button"
                className="secondary"
                disabled={busy}
                onClick={() => void respond('declined')}
              >
                Decline
              </button>
            </div>
          </div>
        ) : null}
        <p className="muted" style={{ marginTop: 16 }}>
          This link is not a binding offer until countersigned by your recruiter.
        </p>
      </div>
    </div>
  )
}
