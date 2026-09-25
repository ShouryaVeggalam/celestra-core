import { useCallback, useEffect, useState } from 'react'
import type { AgentArtifact } from '../api/contracts'
import { HiringApiError, hiringApi } from '../api/hiringApi'
import { useAuth } from '../auth/AuthProvider'
import { ArtifactPanel } from '../components/ArtifactPanel'

export function PlaybooksPage() {
  const auth = useAuth()
  const [topic, setTopic] = useState('Standard engineering hire')
  const [context, setContext] = useState('')
  const [draft, setDraft] = useState<AgentArtifact | null>(null)
  const [history, setHistory] = useState<AgentArtifact[]>([])
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    if (!auth.orgId) return
    try {
      const artifacts = await hiringApi.listArtifacts('playbook')
      setHistory(artifacts.items)
      setError(null)
    } catch (caught) {
      setError(caught instanceof HiringApiError ? caught.message : 'Could not load playbooks')
    }
  }, [auth.orgId])

  useEffect(() => {
    void load()
  }, [load])

  async function onGenerate() {
    setBusy(true)
    setError(null)
    try {
      const result = await hiringApi.draftPlaybook({
        topic,
        extra_context: context || undefined,
      })
      setDraft(result)
      await load()
    } catch (caught) {
      setError(caught instanceof HiringApiError ? caught.message : 'Playbook failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <p className="auth-eyebrow">Repeatable process</p>
          <h1>Playbooks</h1>
          <p>Reusable hiring stages and checklists. Guardrails keep hire/send/schedule human.</p>
        </div>
      </header>
      {error ? <p className="auth-error">{error}</p> : null}
      <div className="two-col">
        <section className="panel">
          <h2>Create</h2>
          <label className="field">
            <span>Topic</span>
            <input value={topic} onChange={(e) => setTopic(e.target.value)} />
          </label>
          <label className="field">
            <span>Context</span>
            <textarea rows={4} value={context} onChange={(e) => setContext(e.target.value)} />
          </label>
          <button type="button" disabled={busy} onClick={() => void onGenerate()}>
            {busy ? 'Building…' : 'Generate playbook'}
          </button>
          {history.length > 0 ? (
            <ul className="stack-list" style={{ marginTop: 16 }}>
              {history.slice(0, 5).map((item) => (
                <li key={item.id}>
                  <button type="button" className="secondary" onClick={() => setDraft(item)}>
                    {item.title}
                  </button>
                </li>
              ))}
            </ul>
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
