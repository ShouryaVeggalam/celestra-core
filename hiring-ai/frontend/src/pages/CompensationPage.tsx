import { useCallback, useEffect, useState } from 'react'
import type { AgentArtifact, Job } from '../api/contracts'
import { HiringApiError, hiringApi } from '../api/hiringApi'
import { useAuth } from '../auth/AuthProvider'
import { ArtifactPanel } from '../components/ArtifactPanel'

export function CompensationPage() {
  const auth = useAuth()
  const [jobs, setJobs] = useState<Job[]>([])
  const [jobId, setJobId] = useState('')
  const [context, setContext] = useState('')
  const [draft, setDraft] = useState<AgentArtifact | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    if (!auth.orgId) return
    try {
      const jobList = await hiringApi.listJobs({ limit: 100 })
      setJobs(jobList.items)
      setJobId((c) => c || jobList.items[0]?.id || '')
      setError(null)
    } catch (caught) {
      setError(caught instanceof HiringApiError ? caught.message : 'Could not load jobs')
    }
  }, [auth.orgId])

  useEffect(() => {
    void load()
  }, [load])

  async function onGenerate() {
    if (!jobId) {
      setError('Pick a job.')
      return
    }
    setBusy(true)
    setError(null)
    try {
      const result = await hiringApi.draftCompensation({
        job_id: jobId,
        extra_context: context || undefined,
      })
      setDraft(result)
    } catch (caught) {
      setError(caught instanceof HiringApiError ? caught.message : 'Compensation draft failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <p className="auth-eyebrow">Advisory ranges</p>
          <h1>Compensation</h1>
          <p>Guidance for hiring managers. This is not an offer — humans finalize numbers.</p>
        </div>
      </header>
      {error ? <p className="auth-error">{error}</p> : null}
      <div className="two-col">
        <section className="panel">
          <h2>Role</h2>
          <label className="field">
            <span>Job</span>
            <select value={jobId} onChange={(e) => setJobId(e.target.value)}>
              <option value="">Select</option>
              {jobs.map((j) => (
                <option key={j.id} value={j.id}>
                  {j.title}
                </option>
              ))}
            </select>
          </label>
          <label className="field">
            <span>Market notes</span>
            <textarea rows={4} value={context} onChange={(e) => setContext(e.target.value)} />
          </label>
          <button type="button" disabled={busy} onClick={() => void onGenerate()}>
            {busy ? 'Estimating…' : 'Draft compensation guidance'}
          </button>
        </section>
        <section className="panel">
          <h2>Draft</h2>
          <ArtifactPanel artifact={draft} />
        </section>
      </div>
    </div>
  )
}
