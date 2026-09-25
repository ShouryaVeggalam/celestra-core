import { useCallback, useEffect, useState } from 'react'
import type { Job, Referral } from '../api/contracts'
import { HiringApiError, hiringApi } from '../api/hiringApi'
import { useAuth } from '../auth/AuthProvider'

export function ReferralsPage() {
  const auth = useAuth()
  const [jobs, setJobs] = useState<Job[]>([])
  const [items, setItems] = useState<Referral[]>([])
  const [referrerName, setReferrerName] = useState('')
  const [referrerEmail, setReferrerEmail] = useState('')
  const [candidateName, setCandidateName] = useState('')
  const [candidateEmail, setCandidateEmail] = useState('')
  const [jobId, setJobId] = useState('')
  const [notes, setNotes] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    if (!auth.orgId) return
    try {
      const [jobList, referrals] = await Promise.all([
        hiringApi.listJobs({ limit: 100 }),
        hiringApi.listReferrals(),
      ])
      setJobs(jobList.items)
      setItems(referrals.items)
      setJobId((c) => c || jobList.items[0]?.id || '')
      setError(null)
    } catch (caught) {
      setError(caught instanceof HiringApiError ? caught.message : 'Could not load referrals')
    }
  }, [auth.orgId])

  useEffect(() => {
    void load()
  }, [load])

  async function onSubmit(event: React.FormEvent) {
    event.preventDefault()
    if (!referrerName.trim() || !candidateName.trim()) {
      setError('Referrer and candidate names are required.')
      return
    }
    setBusy(true)
    setError(null)
    try {
      await hiringApi.createReferral({
        referrer_name: referrerName.trim(),
        referrer_email: referrerEmail || undefined,
        candidate_name: candidateName.trim(),
        candidate_email: candidateEmail || undefined,
        job_id: jobId || null,
        notes: notes || undefined,
        enrich_with_ai: true,
      })
      setReferrerName('')
      setReferrerEmail('')
      setCandidateName('')
      setCandidateEmail('')
      setNotes('')
      await load()
    } catch (caught) {
      setError(caught instanceof HiringApiError ? caught.message : 'Referral failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <p className="auth-eyebrow">Employee channel</p>
          <h1>Referrals</h1>
          <p>Capture referrals into the same hire path. AI adds screening notes — humans decide next steps.</p>
        </div>
      </header>
      {error ? <p className="auth-error">{error}</p> : null}
      <div className="two-col">
        <form className="panel" onSubmit={(e) => void onSubmit(e)}>
          <h2>New referral</h2>
          <label className="field">
            <span>Referrer name</span>
            <input value={referrerName} onChange={(e) => setReferrerName(e.target.value)} required />
          </label>
          <label className="field">
            <span>Referrer email</span>
            <input value={referrerEmail} onChange={(e) => setReferrerEmail(e.target.value)} type="email" />
          </label>
          <label className="field">
            <span>Candidate name</span>
            <input value={candidateName} onChange={(e) => setCandidateName(e.target.value)} required />
          </label>
          <label className="field">
            <span>Candidate email</span>
            <input value={candidateEmail} onChange={(e) => setCandidateEmail(e.target.value)} type="email" />
          </label>
          <label className="field">
            <span>Job</span>
            <select value={jobId} onChange={(e) => setJobId(e.target.value)}>
              <option value="">Unspecified</option>
              {jobs.map((j) => (
                <option key={j.id} value={j.id}>
                  {j.title}
                </option>
              ))}
            </select>
          </label>
          <label className="field">
            <span>Notes</span>
            <textarea rows={3} value={notes} onChange={(e) => setNotes(e.target.value)} />
          </label>
          <button type="submit" disabled={busy}>
            {busy ? 'Saving…' : 'Save referral + AI notes'}
          </button>
        </form>
        <section className="panel">
          <h2>Pipeline</h2>
          {items.length === 0 ? <p className="muted">No referrals yet.</p> : null}
          <ul className="stack-list">
            {items.map((item) => (
              <li key={item.id} className="ops-queue-card" style={{ position: 'relative' }}>
                <p className="ops-queue-card__eyebrow">{item.status}</p>
                <h3>
                  {item.candidate_name}
                </h3>
                <p>
                  Referred by {item.referrer_name}
                  {item.intelligence ? ' · AI notes attached' : ''}
                </p>
              </li>
            ))}
          </ul>
        </section>
      </div>
    </div>
  )
}
