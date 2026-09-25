import { useCallback, useEffect, useState } from 'react'
import type { Candidate, Job, ReviewScorecard } from '../api/contracts'
import { HiringApiError, hiringApi } from '../api/hiringApi'
import { useAuth } from '../auth/AuthProvider'

export function ReviewsPage() {
  const auth = useAuth()
  const [jobs, setJobs] = useState<Job[]>([])
  const [candidates, setCandidates] = useState<Candidate[]>([])
  const [items, setItems] = useState<ReviewScorecard[]>([])
  const [candidateId, setCandidateId] = useState('')
  const [jobId, setJobId] = useState('')
  const [score, setScore] = useState(3.5)
  const [recommendation, setRecommendation] = useState('advance')
  const [notes, setNotes] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    if (!auth.orgId) return
    try {
      const [jobList, candList, reviews] = await Promise.all([
        hiringApi.listJobs({ limit: 100 }),
        hiringApi.listCandidates({ limit: 100 }),
        hiringApi.listReviews(),
      ])
      setJobs(jobList.items)
      setCandidates(candList.items)
      setItems(reviews.items)
      setCandidateId((c) => c || candList.items[0]?.id || '')
      setJobId((c) => c || jobList.items[0]?.id || '')
      setError(null)
    } catch (caught) {
      setError(caught instanceof HiringApiError ? caught.message : 'Could not load reviews')
    }
  }, [auth.orgId])

  useEffect(() => {
    void load()
  }, [load])

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault()
    if (!candidateId) {
      setError('Pick a candidate.')
      return
    }
    setBusy(true)
    setError(null)
    try {
      await hiringApi.createReview({
        candidate_id: candidateId,
        job_id: jobId || null,
        overall_score: score,
        notes: notes || undefined,
        recommendation,
        scores: { overall: score },
      })
      setNotes('')
      await load()
    } catch (caught) {
      setError(caught instanceof HiringApiError ? caught.message : 'Review failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <p className="auth-eyebrow">Human scorecard</p>
          <h1>Reviews</h1>
          <p>Record recruiter judgment on discoveries and matches. AI never marks hire/reject for you.</p>
        </div>
      </header>
      {error ? <p className="auth-error">{error}</p> : null}
      <div className="two-col">
        <form className="panel" onSubmit={(e) => void onSubmit(e)}>
          <h2>New scorecard</h2>
          <label className="field">
            <span>Candidate</span>
            <select value={candidateId} onChange={(e) => setCandidateId(e.target.value)} required>
              <option value="">Select</option>
              {candidates.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.first_name} {c.last_name}
                </option>
              ))}
            </select>
          </label>
          <label className="field">
            <span>Job</span>
            <select value={jobId} onChange={(e) => setJobId(e.target.value)}>
              <option value="">Optional</option>
              {jobs.map((j) => (
                <option key={j.id} value={j.id}>
                  {j.title}
                </option>
              ))}
            </select>
          </label>
          <label className="field">
            <span>Overall score (0–5)</span>
            <input
              type="number"
              min={0}
              max={5}
              step={0.1}
              value={score}
              onChange={(e) => setScore(Number(e.target.value))}
            />
          </label>
          <label className="field">
            <span>Recommendation</span>
            <select value={recommendation} onChange={(e) => setRecommendation(e.target.value)}>
              <option value="advance">Advance</option>
              <option value="hold">Hold</option>
              <option value="pass">Pass</option>
            </select>
          </label>
          <label className="field">
            <span>Notes</span>
            <textarea rows={4} value={notes} onChange={(e) => setNotes(e.target.value)} />
          </label>
          <button type="submit" disabled={busy}>
            {busy ? 'Saving…' : 'Save review'}
          </button>
        </form>
        <section className="panel">
          <h2>Queue</h2>
          {items.length === 0 ? <p className="muted">No reviews yet.</p> : null}
          <ul className="stack-list">
            {items.map((item) => (
              <li key={item.id}>
                <strong>
                  {item.overall_score.toFixed(1)} / 5 · {item.recommendation || 'n/a'}
                </strong>
                <p className="muted">{item.notes || 'No notes'}</p>
              </li>
            ))}
          </ul>
        </section>
      </div>
    </div>
  )
}
