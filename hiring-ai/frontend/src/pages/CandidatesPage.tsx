import { useCallback, useEffect, useState, type FormEvent } from 'react'
import type { Candidate } from '../api/contracts'
import { HiringApiError, hiringApi } from '../api/hiringApi'

export function CandidatesPage() {
  const [candidates, setCandidates] = useState<Candidate[]>([])
  const [firstName, setFirstName] = useState('')
  const [lastName, setLastName] = useState('')
  const [headline, setHeadline] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  const load = useCallback(async () => {
    try {
      const result = await hiringApi.listCandidates({ limit: 100 })
      setCandidates(result.items)
    } catch (caught) {
      setError(caught instanceof HiringApiError ? caught.message : 'Could not load candidates')
    }
  }, [])

  useEffect(() => {
    void load()
  }, [load])

  async function onCreate(event: FormEvent) {
    event.preventDefault()
    setBusy(true)
    setError(null)
    try {
      await hiringApi.createCandidate({
        first_name: firstName.trim(),
        last_name: lastName.trim(),
        headline: headline.trim() || undefined,
      })
      setFirstName('')
      setLastName('')
      setHeadline('')
      await load()
    } catch (caught) {
      setError(caught instanceof HiringApiError ? caught.message : 'Could not create candidate')
    } finally {
      setBusy(false)
    }
  }

  async function markHired(id: string) {
    setError(null)
    try {
      await hiringApi.updateCandidateStatus(id, 'hired')
      await load()
    } catch (caught) {
      setError(caught instanceof HiringApiError ? caught.message : 'Could not update status')
    }
  }

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <p className="auth-eyebrow">Pipeline</p>
          <h1>Candidates</h1>
          <p>People imported from sourcing or added manually. Hire decisions are human-only.</p>
        </div>
      </header>
      {error ? <p className="auth-error">{error}</p> : null}
      <div className="two-col">
        <form className="panel auth-form" onSubmit={(event) => void onCreate(event)}>
          <h2>Add candidate</h2>
          <label>
            <span>First name</span>
            <input value={firstName} onChange={(e) => setFirstName(e.target.value)} required />
          </label>
          <label>
            <span>Last name</span>
            <input value={lastName} onChange={(e) => setLastName(e.target.value)} required />
          </label>
          <label>
            <span>Headline</span>
            <input value={headline} onChange={(e) => setHeadline(e.target.value)} />
          </label>
          <button type="submit" disabled={busy}>
            {busy ? 'Saving…' : 'Add candidate'}
          </button>
        </form>
        <section className="panel">
          <h2>Pipeline ({candidates.length})</h2>
          {candidates.length === 0 ? <p className="muted">No candidates yet — import from Sourcing.</p> : null}
          <ul className="stack-list">
            {candidates.map((candidate) => (
              <li key={candidate.id} className="candidate-row">
                <div>
                  <strong>
                    {candidate.first_name} {candidate.last_name}
                  </strong>
                  <p className="muted">
                    {[candidate.headline, candidate.location, candidate.status].filter(Boolean).join(' · ')}
                  </p>
                  {candidate.github_url || candidate.linkedin_url ? (
                    <a href={candidate.github_url || candidate.linkedin_url || '#'} target="_blank" rel="noreferrer">
                      View profile
                    </a>
                  ) : null}
                </div>
                {candidate.status !== 'hired' ? (
                  <button type="button" onClick={() => void markHired(candidate.id)}>
                    Mark hired
                  </button>
                ) : (
                  <span className="badge">Hired</span>
                )}
              </li>
            ))}
          </ul>
        </section>
      </div>
    </div>
  )
}
