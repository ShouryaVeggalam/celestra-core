import { useCallback, useEffect, useState, type FormEvent } from 'react'
import type { Job } from '../api/contracts'
import { HiringApiError, hiringApi } from '../api/hiringApi'

export function JobsPage() {
  const [jobs, setJobs] = useState<Job[]>([])
  const [title, setTitle] = useState('')
  const [location, setLocation] = useState('')
  const [description, setDescription] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  const load = useCallback(async () => {
    try {
      const result = await hiringApi.listJobs({ limit: 50 })
      setJobs(result.items)
    } catch (caught) {
      setError(caught instanceof HiringApiError ? caught.message : 'Could not load jobs')
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
      await hiringApi.createJob({
        title: title.trim(),
        location: location.trim() || undefined,
        description: description.trim() || undefined,
      })
      setTitle('')
      setLocation('')
      setDescription('')
      await load()
    } catch (caught) {
      setError(caught instanceof HiringApiError ? caught.message : 'Could not create job')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <p className="auth-eyebrow">Hiring</p>
          <h1>Jobs</h1>
          <p>Open roles for your organization.</p>
        </div>
      </header>
      {error ? <p className="auth-error">{error}</p> : null}
      <div className="two-col">
        <form className="panel auth-form" onSubmit={(event) => void onCreate(event)}>
          <h2>Create job</h2>
          <label>
            <span>Title</span>
            <input value={title} onChange={(e) => setTitle(e.target.value)} required />
          </label>
          <label>
            <span>Location</span>
            <input value={location} onChange={(e) => setLocation(e.target.value)} />
          </label>
          <label>
            <span>Description</span>
            <textarea rows={4} value={description} onChange={(e) => setDescription(e.target.value)} />
          </label>
          <button type="submit" disabled={busy}>
            {busy ? 'Saving…' : 'Create job'}
          </button>
        </form>
        <section className="panel">
          <h2>Open roles ({jobs.length})</h2>
          {jobs.length === 0 ? <p className="muted">No jobs yet.</p> : null}
          <ul className="stack-list">
            {jobs.map((job) => (
              <li key={job.id}>
                <strong>{job.title}</strong>
                <p className="muted">
                  {[job.location, job.status].filter(Boolean).join(' · ')}
                </p>
              </li>
            ))}
          </ul>
        </section>
      </div>
    </div>
  )
}
