import { useCallback, useEffect, useState } from 'react'
import type { Candidate, InterviewSession, Job } from '../api/contracts'
import { HiringApiError, hiringApi } from '../api/hiringApi'
import { useAuth } from '../auth/AuthProvider'

export function InterviewsPage() {
  const auth = useAuth()
  const [jobs, setJobs] = useState<Job[]>([])
  const [candidates, setCandidates] = useState<Candidate[]>([])
  const [items, setItems] = useState<InterviewSession[]>([])
  const [candidateId, setCandidateId] = useState('')
  const [jobId, setJobId] = useState('')
  const [title, setTitle] = useState('Screening interview')
  const [notes, setNotes] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [selected, setSelected] = useState<InterviewSession | null>(null)

  const load = useCallback(async () => {
    if (!auth.orgId) return
    try {
      const [jobList, candList, interviews] = await Promise.all([
        hiringApi.listJobs({ limit: 100 }),
        hiringApi.listCandidates({ limit: 100 }),
        hiringApi.listInterviews(),
      ])
      setJobs(jobList.items)
      setCandidates(candList.items)
      setItems(interviews.items)
      setCandidateId((c) => c || candList.items[0]?.id || '')
      setJobId((c) => c || jobList.items[0]?.id || '')
      setError(null)
    } catch (caught) {
      setError(caught instanceof HiringApiError ? caught.message : 'Could not load interviews')
    }
  }, [auth.orgId])

  useEffect(() => {
    void load()
  }, [load])

  async function onCreate(event: React.FormEvent) {
    event.preventDefault()
    if (!candidateId) {
      setError('Pick a candidate.')
      return
    }
    setBusy(true)
    setError(null)
    try {
      const row = await hiringApi.createInterview({
        candidate_id: candidateId,
        job_id: jobId || null,
        title: title.trim() || 'Interview',
        notes: notes || undefined,
        generate_with_ai: true,
      })
      setSelected(row)
      await load()
    } catch (caught) {
      setError(caught instanceof HiringApiError ? caught.message : 'Interview prep failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <p className="auth-eyebrow">Interview prep</p>
          <h1>Interviews</h1>
          <p>Generate question packs and briefs. Scheduling stays human — no calendar auto-book.</p>
        </div>
      </header>
      {error ? <p className="auth-error">{error}</p> : null}
      <div className="two-col">
        <form className="panel" onSubmit={(e) => void onCreate(e)}>
          <h2>Prep session</h2>
          <label className="field">
            <span>Title</span>
            <input value={title} onChange={(e) => setTitle(e.target.value)} required />
          </label>
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
            <span>Notes</span>
            <textarea rows={3} value={notes} onChange={(e) => setNotes(e.target.value)} />
          </label>
          <button type="submit" disabled={busy}>
            {busy ? 'Generating…' : 'Create prep pack'}
          </button>
        </form>
        <section className="panel">
          <h2>{selected ? selected.title : 'Selected prep'}</h2>
          {!selected ? <p className="muted">Create or select a session.</p> : null}
          {selected?.summary ? <p>{selected.summary}</p> : null}
          {selected && selected.questions.length > 0 ? (
            <ol>
              {selected.questions.map((q) => (
                <li key={q}>{q}</li>
              ))}
            </ol>
          ) : null}
        </section>
      </div>
      <section className="panel" style={{ marginTop: 14 }}>
        <h2>Sessions</h2>
        <ul className="stack-list">
          {items.map((item) => (
            <li key={item.id}>
              <button type="button" className="secondary" onClick={() => setSelected(item)}>
                {item.title}
              </button>
              <span className="muted"> · {item.created_at}</span>
            </li>
          ))}
        </ul>
      </section>
    </div>
  )
}
