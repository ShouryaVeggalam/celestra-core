import { useCallback, useEffect, useState } from 'react'
import type { AgentArtifact } from '../api/contracts'
import { HiringApiError, hiringApi } from '../api/hiringApi'
import { useAuth } from '../auth/AuthProvider'
import { ArtifactPanel } from '../components/ArtifactPanel'

export function HiringChiefPage() {
  const auth = useAuth()
  const [topic, setTopic] = useState('This week priorities')
  const [draft, setDraft] = useState<AgentArtifact | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const loadLatest = useCallback(async () => {
    if (!auth.orgId) return
    try {
      const artifacts = await hiringApi.listArtifacts('hiring_chief')
      if (artifacts.items[0]) setDraft(artifacts.items[0])
      setError(null)
    } catch (caught) {
      setError(caught instanceof HiringApiError ? caught.message : 'Could not load brief')
    }
  }, [auth.orgId])

  useEffect(() => {
    void loadLatest()
  }, [loadLatest])

  async function onGenerate() {
    setBusy(true)
    setError(null)
    try {
      const result = await hiringApi.draftHiringChief({ topic })
      setDraft(result)
    } catch (caught) {
      setError(caught instanceof HiringApiError ? caught.message : 'Hiring Chief failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <p className="auth-eyebrow">Org posture</p>
          <h1>Hiring Chief</h1>
          <p>Executive hiring brief from live pipeline stats. Actions still require humans.</p>
        </div>
      </header>
      {error ? <p className="auth-error">{error}</p> : null}
      <div className="two-col">
        <section className="panel">
          <h2>Brief</h2>
          <label className="field">
            <span>Focus</span>
            <input value={topic} onChange={(e) => setTopic(e.target.value)} />
          </label>
          <button type="button" disabled={busy} onClick={() => void onGenerate()}>
            {busy ? 'Briefing…' : 'Generate Hiring Chief brief'}
          </button>
        </section>
        <section className="panel">
          <h2>Latest</h2>
          <ArtifactPanel artifact={draft} />
        </section>
      </div>
    </div>
  )
}
