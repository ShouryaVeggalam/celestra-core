import { useCallback, useEffect, useRef, useState } from 'react'
import type { CandidateDiscovery, Job } from '../api/contracts'
import { HiringApiError, hiringApi } from '../api/hiringApi'

const LIMITS = [5, 10, 20, 30] as const

function isOpenToWork(item: CandidateDiscovery) {
  return item.skills.some((skill) => skill.toLowerCase() === 'open-to-work')
}

export function SourcingPage() {
  const [jobs, setJobs] = useState<Job[]>([])
  const [query, setQuery] = useState('python engineer')
  const [limit, setLimit] = useState(10)
  const [jobId, setJobId] = useState('')
  const [discoveries, setDiscoveries] = useState<CandidateDiscovery[]>([])
  const [busy, setBusy] = useState(false)
  const [importingId, setImportingId] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const fileRef = useRef<HTMLInputElement>(null)

  const loadJobs = useCallback(async () => {
    try {
      const result = await hiringApi.listJobs({ limit: 100 })
      setJobs(result.items)
    } catch {
      setJobs([])
    }
  }, [])

  useEffect(() => {
    void loadJobs()
  }, [loadJobs])

  async function ensureProject(name: string) {
    return hiringApi.createSourcingProject({
      name: name.slice(0, 120),
      job_id: jobId || null,
    })
  }

  async function onDiscover() {
    const trimmed = query.trim()
    if (!trimmed) {
      setError('Describe who you want to hire.')
      return
    }
    setBusy(true)
    setError(null)
    try {
      const project = await ensureProject(trimmed)
      const result = await hiringApi.discoverTalent({
        project_id: project.id,
        query: trimmed,
        limit,
      })
      setDiscoveries(result.discoveries)
    } catch (caught) {
      setError(caught instanceof HiringApiError ? caught.message : 'Discovery failed')
    } finally {
      setBusy(false)
    }
  }

  async function onCsv(file: File | null) {
    if (!file) return
    setBusy(true)
    setError(null)
    try {
      const project = await ensureProject(query.trim() || `CSV · ${file.name}`)
      const result = await hiringApi.importSourcingCsv(project.id, file)
      setDiscoveries(result.discoveries)
    } catch (caught) {
      setError(caught instanceof HiringApiError ? caught.message : 'CSV import failed')
    } finally {
      setBusy(false)
      if (fileRef.current) fileRef.current.value = ''
    }
  }

  async function onImport(id: string) {
    setImportingId(id)
    setError(null)
    try {
      const result = await hiringApi.importDiscovery(id)
      setDiscoveries((current) => current.map((item) => (item.id === id ? result.discovery : item)))
    } catch (caught) {
      setError(caught instanceof HiringApiError ? caught.message : 'Import failed')
    } finally {
      setImportingId(null)
    }
  }

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <p className="auth-eyebrow">Talent</p>
          <h1>Sourcing</h1>
          <p>
            Discover hireable GitHub profiles, or upload a CSV export you already own. Import turns a
            discovery into a Candidate your org can hire.
          </p>
        </div>
      </header>
      {error ? <p className="auth-error">{error}</p> : null}
      <div className="two-col">
        <section className="panel">
          <h2>Find job seekers</h2>
          <label className="field">
            <span>Search</span>
            <textarea rows={3} value={query} onChange={(e) => setQuery(e.target.value)} />
          </label>
          <label className="field">
            <span>Limit</span>
            <select value={limit} onChange={(e) => setLimit(Number(e.target.value))}>
              {LIMITS.map((value) => (
                <option key={value} value={value}>
                  {value}
                </option>
              ))}
            </select>
          </label>
          <label className="field">
            <span>Link job (optional)</span>
            <select value={jobId} onChange={(e) => setJobId(e.target.value)}>
              <option value="">No linked job</option>
              {jobs.map((job) => (
                <option key={job.id} value={job.id}>
                  {job.title}
                </option>
              ))}
            </select>
          </label>
          <div className="button-row">
            <button type="button" disabled={busy} onClick={() => void onDiscover()}>
              {busy ? 'Working…' : 'Discover job seekers'}
            </button>
            <label className="file-btn">
              Import board CSV
              <input
                ref={fileRef}
                className="sr-only"
                type="file"
                accept=".csv,text/csv"
                disabled={busy}
                onChange={(e) => void onCsv(e.target.files?.[0] ?? null)}
              />
            </label>
          </div>
        </section>
        <section className="panel">
          <h2>Discoveries</h2>
          {discoveries.length === 0 ? (
            <p className="muted">Run Discover or upload a CSV. Nothing enters Candidates until you Import.</p>
          ) : null}
          <ul className="stack-list">
            {discoveries.map((item) => (
              <li key={item.id} className="discovery-card">
                <div className="discovery-card__head">
                  <strong>{item.full_name}</strong>
                  <span>{Math.round(item.confidence * 100)}%</span>
                </div>
                {isOpenToWork(item) ? <p className="badge">Open to work</p> : null}
                {item.headline ? <p>{item.headline}</p> : null}
                <p className="muted">
                  {[item.company, item.location, item.source].filter(Boolean).join(' · ')}
                </p>
                <div className="button-row">
                  {item.profile_url ? (
                    <a className="secondary-link" href={item.profile_url} target="_blank" rel="noreferrer">
                      View profile
                    </a>
                  ) : null}
                  {item.status === 'imported' ? (
                    <span className="badge">Imported</span>
                  ) : (
                    <button type="button" disabled={importingId === item.id} onClick={() => void onImport(item.id)}>
                      {importingId === item.id ? 'Importing…' : 'Import Candidate'}
                    </button>
                  )}
                </div>
              </li>
            ))}
          </ul>
        </section>
      </div>
    </div>
  )
}
