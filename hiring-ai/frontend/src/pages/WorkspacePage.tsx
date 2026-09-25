import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { hiringApi } from '../api/hiringApi'
import type { Candidate } from '../api/contracts'
import { useAuth } from '../auth/AuthProvider'

function greetingName(displayName: string | null | undefined, email: string | null | undefined) {
  if (displayName?.trim()) return displayName.trim().split(/\s+/)[0]
  if (email?.includes('@')) return email.split('@')[0]
  return 'Recruiter'
}

function dayPart(now = new Date()) {
  const hour = now.getHours()
  if (hour < 12) return 'morning'
  if (hour < 18) return 'afternoon'
  return 'evening'
}

export function WorkspacePage() {
  const auth = useAuth()
  const [candidates, setCandidates] = useState<Candidate[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    void hiringApi
      .listCandidates({ limit: 20 })
      .then((result) => {
        if (!cancelled) setCandidates(result.items)
      })
      .catch(() => {
        if (!cancelled) setCandidates([])
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [auth.orgId])

  const name = greetingName(auth.me?.display_name, auth.me?.email)
  const newCandidates = candidates.filter((item) => item.status === 'active').length
  const metrics = [
    { label: 'Pending Reviews', value: '—' },
    { label: 'Interviews Today', value: '—' },
    { label: 'Offer Responses', value: '—' },
    { label: 'New Candidates', value: loading ? '—' : String(newCandidates || '—') },
  ]

  const queue = candidates.slice(0, 5)

  return (
    <div className="ops-workspace">
      <header className="ops-workspace__header">
        <p className="ops-kicker">HIRING Workspace</p>
        <h1>
          Good {dayPart()}, {name}.
        </h1>
        <p className="ops-lead">Your recruiting priorities for this organization.</p>
      </header>

      <div className="ops-banner" role="note">
        Read-only operational workspace. Hiring actions stay human and happen in their own screens.
      </div>

      <section className="ops-today">
        <h2>Today</h2>
        <div className="ops-metric-grid">
          {metrics.map((metric) => (
            <article key={metric.label} className="ops-metric">
              <p>{metric.label}</p>
              <strong>{metric.value}</strong>
            </article>
          ))}
        </div>
      </section>

      <section className="ops-queue">
        <div className="ops-queue__head">
          <h2>Priority Queue</h2>
          <Link to="/sourcing">Open sourcing</Link>
        </div>

        {queue.length === 0 && !loading ? (
          <article className="ops-queue-card">
            <p className="ops-queue-card__eyebrow">Ready to hire</p>
            <h3>No priorities yet</h3>
            <p>Discover open-to-work talent or import a CSV, then review candidates here.</p>
            <Link className="ops-queue-card__action" to="/sourcing">
              Open
            </Link>
          </article>
        ) : (
          <ul className="ops-queue-list">
            {queue.map((candidate) => (
              <li key={candidate.id}>
                <article className="ops-queue-card">
                  <p className="ops-queue-card__eyebrow">New candidate discovered</p>
                  <h3>
                    {candidate.first_name} {candidate.last_name}
                  </h3>
                  <p>
                    {candidate.headline ||
                      'Imported talent is waiting for a human hiring decision.'}
                  </p>
                  <Link className="ops-queue-card__action" to="/candidates">
                    Open
                  </Link>
                </article>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  )
}
