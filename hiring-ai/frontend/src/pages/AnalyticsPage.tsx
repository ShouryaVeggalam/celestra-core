import { useCallback, useEffect, useState } from 'react'
import type { AnalyticsSummary } from '../api/contracts'
import { HiringApiError, hiringApi } from '../api/hiringApi'
import { useAuth } from '../auth/AuthProvider'

export function AnalyticsPage() {
  const auth = useAuth()
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    if (!auth.orgId) return
    try {
      const data = await hiringApi.analyticsSummary()
      setSummary(data)
      setError(null)
    } catch (caught) {
      setError(caught instanceof HiringApiError ? caught.message : 'Could not load analytics')
    }
  }, [auth.orgId])

  useEffect(() => {
    void load()
  }, [load])

  const statusEntries = Object.entries(summary?.candidates_by_status ?? {})

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <p className="auth-eyebrow">Funnel</p>
          <h1>Analytics</h1>
          <p>Org-scoped pipeline and intelligence counts. Read-only operational view.</p>
        </div>
      </header>
      {error ? <p className="auth-error">{error}</p> : null}
      <section className="ops-today">
        <h2>Snapshot</h2>
        <div className="ops-metric-grid">
          <article className="ops-metric">
            <p>Open jobs</p>
            <strong>{summary ? summary.open_jobs : '—'}</strong>
          </article>
          <article className="ops-metric">
            <p>Match drafts</p>
            <strong>{summary ? summary.match_drafts : '—'}</strong>
          </article>
          <article className="ops-metric">
            <p>Reviews</p>
            <strong>{summary ? summary.reviews : '—'}</strong>
          </article>
          <article className="ops-metric">
            <p>Interviews</p>
            <strong>{summary ? summary.interviews : '—'}</strong>
          </article>
        </div>
        <div className="ops-metric-grid">
          <article className="ops-metric">
            <p>Referrals</p>
            <strong>{summary ? summary.referrals : '—'}</strong>
          </article>
          <article className="ops-metric">
            <p>Documents</p>
            <strong>{summary ? summary.documents : '—'}</strong>
          </article>
          <article className="ops-metric">
            <p>Portal links</p>
            <strong>{summary ? summary.portal_links : '—'}</strong>
          </article>
          <article className="ops-metric">
            <p>Statuses tracked</p>
            <strong>{statusEntries.length || '—'}</strong>
          </article>
        </div>
      </section>
      <section className="panel">
        <h2>Candidates by status</h2>
        {statusEntries.length === 0 ? <p className="muted">No candidates yet.</p> : null}
        <ul className="stack-list">
          {statusEntries.map(([status, count]) => (
            <li key={status}>
              <strong>{status}</strong>
              <span className="muted"> · {count}</span>
            </li>
          ))}
        </ul>
      </section>
    </div>
  )
}
