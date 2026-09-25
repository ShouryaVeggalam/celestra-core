import { useCallback, useEffect, useState } from 'react'
import type { AgentArtifact, Candidate, Job } from '../api/contracts'
import { HiringApiError, hiringApi } from '../api/hiringApi'
import { useAuth } from '../auth/AuthProvider'
import { ArtifactPanel } from '../components/ArtifactPanel'

export function OutreachPage() {
  const auth = useAuth()
  const [jobs, setJobs] = useState<Job[]>([])
  const [candidates, setCandidates] = useState<Candidate[]>([])
  const [history, setHistory] = useState<AgentArtifact[]>([])
  const [jobId, setJobId] = useState('')
  const [candidateId, setCandidateId] = useState('')
  const [context, setContext] = useState('')
  const [draft, setDraft] = useState<AgentArtifact | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    if (!auth.orgId) return
    try {
      const [jobList, candList, artifacts] = await Promise.all([
        hiringApi.listJobs({ limit: 100 }),
        hiringApi.listCandidates({ limit: 100 }),
        hiringApi.listArtifacts('outreach'),
      ])
      setJobs(jobList.items)
      setCandidates(candList.items)
      setHistory(artifacts.items)
      setJobId((c) => c || jobList.items[0]?.id || '')
      setCandidateId((c) => c || candList.items[0]?.id || '')
      setError(null)
    } catch (caught) {
      setError(caught instanceof HiringApiError ? caught.message : 'Could not load outreach')
    }
  }, [auth.orgId])

  useEffect(() => {
    void load()
  }, [load])

  async function onDraft() {
    if (!candidateId) {
      setError('Pick a candidate.')
      return
    }
    setBusy(true)
    setError(null)
    try {
      const result = await hiringApi.draftOutreach({
        candidate_id: candidateId,
        job_id: jobId || null,
        extra_context: context || undefined,
      })
      setDraft(result)
      await load()
    } catch (caught) {
      setError(caught instanceof HiringApiError ? caught.message : 'Outreach draft failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <p className="auth-eyebrow">Groq draft</p>
          <h1>Outreach</h1>
          <p>Draft recruiter messages for review. Sends stay human-approved — nothing is emailed from here.</p>
        </div>
      </header>
      {error ? <p className="auth-error">{error}</p> : null}
      <div className="two-col">
        <section className="panel">
          <h2>Compose</h2>
          <label className="field">
            <span>Candidate</span>
            <select value={candidateId} onChange={(e) => setCandidateId(e.target.value)}>
              <option value="">Select candidate</option>
              {candidates.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.first_name} {c.last_name}
                </option>
              ))}
            </select>
          </label>
          <label className="field">
            <span>Job (optional)</span>
            <select value={jobId} onChange={(e) => setJobId(e.target.value)}>
              <option value="">Open role</option>
              {jobs.map((j) => (
                <option key={j.id} value={j.id}>
                  {j.title}
                </option>
              ))}
            </select>
          </label>
          <label className="field">
            <span>Extra context</span>
            <textarea rows={4} value={context} onChange={(e) => setContext(e.target.value)} />
          </label>
          <button type="button" disabled={busy} onClick={() => void onDraft()}>
            {busy ? 'Drafting…' : 'Generate outreach draft'}
          </button>
        </section>
        <section className="panel">
          <h2>Latest draft</h2>
          <ArtifactPanel artifact={draft} />
        </section>
      </div>
      <section className="panel" style={{ marginTop: 14 }}>
        <h2>Recent drafts</h2>
        {history.length === 0 ? <p className="muted">No outreach drafts yet.</p> : null}
        <ul className="stack-list">
          {history.map((item) => (
            <li key={item.id}>
              <strong>{item.title}</strong>
              <p className="muted">{item.created_at}</p>
            </li>
          ))}
        </ul>
      </section>
    </div>
  )
}
