import { useCallback, useEffect, useState } from 'react'
import type { AgentArtifact, Candidate } from '../api/contracts'
import { HiringApiError, hiringApi } from '../api/hiringApi'
import { useAuth } from '../auth/AuthProvider'
import { ArtifactPanel } from '../components/ArtifactPanel'

export function SkillsPage() {
  const auth = useAuth()
  const [candidates, setCandidates] = useState<Candidate[]>([])
  const [candidateId, setCandidateId] = useState('')
  const [draft, setDraft] = useState<AgentArtifact | null>(null)
  const [history, setHistory] = useState<AgentArtifact[]>([])
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    if (!auth.orgId) return
    try {
      const [candList, artifacts] = await Promise.all([
        hiringApi.listCandidates({ limit: 100 }),
        hiringApi.listArtifacts('skills'),
      ])
      setCandidates(candList.items)
      setHistory(artifacts.items)
      setCandidateId((c) => c || candList.items[0]?.id || '')
      setError(null)
    } catch (caught) {
      setError(caught instanceof HiringApiError ? caught.message : 'Could not load skills')
    }
  }, [auth.orgId])

  useEffect(() => {
    void load()
  }, [load])

  async function onGenerate() {
    if (!candidateId) {
      setError('Pick a candidate.')
      return
    }
    setBusy(true)
    setError(null)
    try {
      const result = await hiringApi.draftSkills({ candidate_id: candidateId })
      setDraft(result)
      await load()
    } catch (caught) {
      setError(caught instanceof HiringApiError ? caught.message : 'Skills draft failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <p className="auth-eyebrow">Evidence graph</p>
          <h1>Skills</h1>
          <p>Surface skill evidence from profiles for recruiter judgment — never an auto-qualify.</p>
        </div>
      </header>
      {error ? <p className="auth-error">{error}</p> : null}
      <div className="two-col">
        <section className="panel">
          <h2>Candidate</h2>
          <label className="field">
            <span>Profile</span>
            <select value={candidateId} onChange={(e) => setCandidateId(e.target.value)}>
              <option value="">Select</option>
              {candidates.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.first_name} {c.last_name}
                </option>
              ))}
            </select>
          </label>
          <button type="button" disabled={busy} onClick={() => void onGenerate()}>
            {busy ? 'Analyzing…' : 'Build skills graph'}
          </button>
          {history.length > 0 ? (
            <div style={{ marginTop: 16 }}>
              <h3>History</h3>
              <ul className="stack-list">
                {history.slice(0, 5).map((item) => (
                  <li key={item.id}>
                    <button type="button" className="secondary" onClick={() => setDraft(item)}>
                      {item.title}
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          ) : null}
        </section>
        <section className="panel">
          <h2>Draft</h2>
          <ArtifactPanel artifact={draft} />
        </section>
      </div>
    </div>
  )
}
