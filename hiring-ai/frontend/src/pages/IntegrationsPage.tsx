import { useCallback, useEffect, useState } from 'react'
import type {
  Candidate,
  HiringDocument,
  IntegrationsResponse,
  Job,
  PortalAccess,
} from '../api/contracts'
import { HiringApiError, hiringApi } from '../api/hiringApi'
import { useAuth } from '../auth/AuthProvider'

export function IntegrationsPage() {
  const auth = useAuth()
  const [data, setData] = useState<IntegrationsResponse | null>(null)
  const [docs, setDocs] = useState<HiringDocument[]>([])
  const [portals, setPortals] = useState<PortalAccess[]>([])
  const [jobs, setJobs] = useState<Job[]>([])
  const [candidates, setCandidates] = useState<Candidate[]>([])
  const [provider, setProvider] = useState('ats_webhook')
  const [notes, setNotes] = useState('')
  const [docType, setDocType] = useState<'hiring_brief' | 'offer_letter'>('hiring_brief')
  const [jobId, setJobId] = useState('')
  const [candidateId, setCandidateId] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [lastDoc, setLastDoc] = useState<HiringDocument | null>(null)
  const [lastPortal, setLastPortal] = useState<PortalAccess | null>(null)

  const load = useCallback(async () => {
    if (!auth.orgId) return
    try {
      const [integrations, documents, portalList, jobList, candList] = await Promise.all([
        hiringApi.listIntegrations(),
        hiringApi.listDocuments(),
        hiringApi.listPortalAccess(),
        hiringApi.listJobs({ limit: 100 }),
        hiringApi.listCandidates({ limit: 100 }),
      ])
      setData(integrations)
      setDocs(documents.items)
      setPortals(portalList.items)
      setJobs(jobList.items)
      setCandidates(candList.items)
      setJobId((c) => c || jobList.items[0]?.id || '')
      setCandidateId((c) => c || candList.items[0]?.id || '')
      setError(null)
    } catch (caught) {
      setError(caught instanceof HiringApiError ? caught.message : 'Could not load integrations')
    }
  }, [auth.orgId])

  useEffect(() => {
    void load()
  }, [load])

  async function onAddIntegration(event: React.FormEvent) {
    event.preventDefault()
    setBusy(true)
    setError(null)
    try {
      await hiringApi.createIntegration({ provider, notes: notes || undefined })
      setNotes('')
      await load()
    } catch (caught) {
      setError(caught instanceof HiringApiError ? caught.message : 'Integration save failed')
    } finally {
      setBusy(false)
    }
  }

  async function onDocument() {
    setBusy(true)
    setError(null)
    try {
      const doc = await hiringApi.createDocument({
        doc_type: docType,
        job_id: jobId || null,
        candidate_id: candidateId || null,
      })
      setLastDoc(doc)
      await load()
    } catch (caught) {
      setError(caught instanceof HiringApiError ? caught.message : 'Document draft failed')
    } finally {
      setBusy(false)
    }
  }

  async function onPortal() {
    if (!candidateId) {
      setError('Pick a candidate for the portal link.')
      return
    }
    setBusy(true)
    setError(null)
    try {
      const portal = await hiringApi.createPortalAccess({ candidate_id: candidateId })
      setLastPortal(portal)
      await load()
    } catch (caught) {
      setError(caught instanceof HiringApiError ? caught.message : 'Portal link failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <p className="auth-eyebrow">Connections</p>
          <h1>Integrations</h1>
          <p>Auth, AI, sourcing status, document drafts, and candidate portal links.</p>
        </div>
      </header>
      {error ? <p className="auth-error">{error}</p> : null}

      <section className="panel">
        <h2>Built-in</h2>
        <ul className="stack-list">
          {(data?.builtins ?? []).map((item) => (
            <li key={item.provider}>
              <strong>{item.provider}</strong>
              <span className="muted"> · {item.status}</span>
            </li>
          ))}
        </ul>
      </section>

      <div className="two-col" style={{ marginTop: 14 }}>
        <form className="panel" onSubmit={(e) => void onAddIntegration(e)}>
          <h2>Record a link</h2>
          <label className="field">
            <span>Provider</span>
            <input value={provider} onChange={(e) => setProvider(e.target.value)} required />
          </label>
          <label className="field">
            <span>Notes</span>
            <textarea rows={3} value={notes} onChange={(e) => setNotes(e.target.value)} />
          </label>
          <button type="submit" disabled={busy}>
            Save
          </button>
          {(data?.items.length ?? 0) > 0 ? (
            <ul className="stack-list" style={{ marginTop: 16 }}>
              {data!.items.map((item) => (
                <li key={item.id}>
                  <strong>{item.provider}</strong>
                  <span className="muted"> · {item.status}</span>
                </li>
              ))}
            </ul>
          ) : null}
        </form>

        <section className="panel">
          <h2>Documents & portal</h2>
          <label className="field">
            <span>Document type</span>
            <select
              value={docType}
              onChange={(e) => setDocType(e.target.value as 'hiring_brief' | 'offer_letter')}
            >
              <option value="hiring_brief">Hiring brief</option>
              <option value="offer_letter">Offer letter draft</option>
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
            <span>Candidate</span>
            <select value={candidateId} onChange={(e) => setCandidateId(e.target.value)}>
              <option value="">Optional / required for portal</option>
              {candidates.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.first_name} {c.last_name}
                </option>
              ))}
            </select>
          </label>
          <div className="button-row">
            <button type="button" disabled={busy} onClick={() => void onDocument()}>
              Draft document
            </button>
            <button type="button" className="secondary" disabled={busy} onClick={() => void onPortal()}>
              Create portal link
            </button>
          </div>
          {lastDoc ? (
            <div style={{ marginTop: 16 }}>
              <h3>{lastDoc.title}</h3>
              <p style={{ whiteSpace: 'pre-wrap' }}>{lastDoc.body}</p>
            </div>
          ) : null}
          {lastPortal ? (
            <p className="auth-success" style={{ marginTop: 12 }}>
              Portal path: <strong>{lastPortal.portal_path}</strong>
            </p>
          ) : null}
          {docs.length > 0 ? (
            <p className="muted" style={{ marginTop: 12 }}>
              {docs.length} document(s) · {portals.length} portal link(s)
            </p>
          ) : null}
        </section>
      </div>
    </div>
  )
}
