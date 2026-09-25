import { useCallback, useEffect, useState } from 'react'
import type { AgentArtifact } from '../api/contracts'
import { HiringApiError, hiringApi } from '../api/hiringApi'
import { useAuth } from '../auth/AuthProvider'
import { ArtifactPanel } from '../components/ArtifactPanel'

export function ForecastPage() {
  const auth = useAuth()
  const [topic, setTopic] = useState('Next quarter hiring capacity')
  const [draft, setDraft] = useState<AgentArtifact | null>(null)
  const [history, setHistory] = useState<AgentArtifact[]>([])
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    if (!auth.orgId) return
    try {
      const artifacts = await hiringApi.listArtifacts('forecast')
      setHistory(artifacts.items)
      setError(null)
    } catch (caught) {
      setError(caught instanceof HiringApiError ? caught.message : 'Could not load forecasts')
    }
  }, [auth.orgId])

  useEffect(() => {
    void load()
  }, [load])

  async function onGenerate() {
    setBusy(true)
    setError(null)
    try {
      const result = await hiringApi.draftForecast({ topic })
      setDraft(result)
      await load()
    } catch (caught) {
      setError(caught instanceof HiringApiError ? caught.message : 'Forecast failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <p className="auth-eyebrow">Pipeline outlook</p>
          <h1>Forecast</h1>
          <p>Capacity and pipeline narrative from live org metrics. Advisory only.</p>
        </div>
      </header>
      {error ? <p className="auth-error">{error}</p> : null}
      <div className="two-col">
        <section className="panel">
          <h2>Focus</h2>
          <label className="field">
            <span>Topic</span>
            <input value={topic} onChange={(e) => setTopic(e.target.value)} />
          </label>
          <button type="button" disabled={busy} onClick={() => void onGenerate()}>
            {busy ? 'Forecasting…' : 'Generate forecast'}
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
          <h2>Outlook</h2>
          <ArtifactPanel artifact={draft} />
        </section>
      </div>
    </div>
  )
}
