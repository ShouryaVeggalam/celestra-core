import { useState } from 'react'
import type { AgentArtifact } from '../api/contracts'
import { HiringApiError, hiringApi } from '../api/hiringApi'
import { ArtifactPanel } from '../components/ArtifactPanel'

export function AutonomousPage() {
  const [topic, setTopic] = useState('Prep next hiring actions')
  const [context, setContext] = useState('')
  const [draft, setDraft] = useState<AgentArtifact | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function onGenerate() {
    setBusy(true)
    setError(null)
    try {
      const result = await hiringApi.draftAutonomousPrep({
        topic,
        extra_context: context || undefined,
      })
      setDraft(result)
    } catch (caught) {
      setError(caught instanceof HiringApiError ? caught.message : 'Prep pack failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <p className="auth-eyebrow">Safe prep only</p>
          <h1>Autonomous</h1>
          <p>
            Suggest preparation tasks with hard guardrails. Hire, reject, email, and schedule stay
            explicit human actions.
          </p>
        </div>
      </header>
      <div className="ops-banner" role="note">
        Every suggested task is marked requires_human=true. Nothing executes from this screen.
      </div>
      {error ? <p className="auth-error">{error}</p> : null}
      <div className="two-col">
        <section className="panel">
          <h2>Request</h2>
          <label className="field">
            <span>Topic</span>
            <input value={topic} onChange={(e) => setTopic(e.target.value)} />
          </label>
          <label className="field">
            <span>Context</span>
            <textarea rows={4} value={context} onChange={(e) => setContext(e.target.value)} />
          </label>
          <button type="button" disabled={busy} onClick={() => void onGenerate()}>
            {busy ? 'Preparing…' : 'Generate prep pack'}
          </button>
        </section>
        <section className="panel">
          <h2>Suggestions</h2>
          <ArtifactPanel artifact={draft} />
        </section>
      </div>
    </div>
  )
}
