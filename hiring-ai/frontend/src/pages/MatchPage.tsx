import { useCallback, useEffect, useState } from 'react'
import type { Candidate, Job, MatchDraft } from '../api/contracts'
import { HiringApiError, hiringApi } from '../api/hiringApi'
import { useAuth } from '../auth/AuthProvider'

export function MatchPage() {
  const auth = useAuth()
  const [jobs, setJobs] = useState<Job[]>([])
  const [candidates, setCandidates] = useState<Candidate[]>([])
  const [jobId, setJobId] = useState('')
  const [candidateId, setCandidateId] = useState('')
  const [match, setMatch] = useState<MatchDraft | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    if (!auth.orgId) return
    try {
      const [jobList, candList] = await Promise.all([
        hiringApi.listJobs({ limit: 100 }),
        hiringApi.listCandidates({ limit: 100 }),
      ])
      setJobs(jobList.items)
      setCandidates(candList.items)
      setJobId((current) => current || jobList.items[0]?.id || '')
      setCandidateId((current) => current || candList.items[0]?.id || '')
      setError(null)
    } catch (caught) {
      setError(caught instanceof HiringApiError ? caught.message : 'Could not load match inputs')
    }
  }, [auth.orgId])

  useEffect(() => {
    void load()
  }, [load])

  async function onMatch() {
    if (!jobId || !candidateId) {
      setError('Pick a job and a candidate.')
      return
    }
    setBusy(true)
    setError(null)
    try {
      const draft = await hiringApi.createMatch({ job_id: jobId, candidate_id: candidateId })
      setMatch(draft)
    } catch (caught) {
      setError(
        caught instanceof HiringApiError
          ? caught.message
          : 'Match failed. Set GROQ_API_KEY on the API.',
      )
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <p className="auth-eyebrow">Groq AI</p>
          <h1>Match</h1>
          <p>
            Compare one job to one candidate with Groq. This is review evidence — it never hires or
            rejects for you.
          </p>
        </div>
      </header>
      {error ? <p className="auth-error">{error}</p> : null}
      <div className="two-col">
        <section className="panel">
          <h2>Inputs</h2>
          <label className="field">
            <span>Job</span>
            <select value={jobId} onChange={(e) => setJobId(e.target.value)}>
              <option value="">Select job</option>
              {jobs.map((job) => (
                <option key={job.id} value={job.id}>
                  {job.title}
                </option>
              ))}
            </select>
          </label>
          <label className="field">
            <span>Candidate</span>
            <select value={candidateId} onChange={(e) => setCandidateId(e.target.value)}>
              <option value="">Select candidate</option>
              {candidates.map((candidate) => (
                <option key={candidate.id} value={candidate.id}>
                  {candidate.first_name} {candidate.last_name}
                </option>
              ))}
            </select>
          </label>
          <button type="button" disabled={busy} onClick={() => void onMatch()}>
            {busy ? 'Matching with Groq…' : 'Generate match draft'}
          </button>
        </section>
        <section className="panel">
          <h2>Draft</h2>
          {!match ? <p className="muted">No match yet.</p> : null}
          {match ? (
            <div className="match-draft">
              <p>
                <strong>{Math.round(match.score * 100)}% fit</strong>
                {match.model ? <span className="muted"> · {match.model}</span> : null}
              </p>
              {match.summary ? <p>{match.summary}</p> : null}
              {match.strengths.length > 0 ? (
                <>
                  <h3>Strengths</h3>
                  <ul>
                    {match.strengths.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </>
              ) : null}
              {match.gaps.length > 0 ? (
                <>
                  <h3>Gaps</h3>
                  <ul>
                    {match.gaps.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </>
              ) : null}
              {match.evidence.length > 0 ? (
                <>
                  <h3>Evidence</h3>
                  <ul>
                    {match.evidence.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </>
              ) : null}
            </div>
          ) : null}
        </section>
      </div>
    </div>
  )
}
