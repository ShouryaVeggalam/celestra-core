import type { AgentArtifact } from '../api/contracts'

function stringifyPayload(payload: Record<string, unknown>): string {
  try {
    return JSON.stringify(payload, null, 2)
  } catch {
    return String(payload)
  }
}

export function ArtifactPanel({ artifact }: { artifact: AgentArtifact | null }) {
  if (!artifact) {
    return <p className="muted">No draft yet. Generate one to review — nothing is sent automatically.</p>
  }
  return (
    <div className="match-draft">
      <p>
        <strong>{artifact.title}</strong>
        {artifact.model ? <span className="muted"> · {artifact.model}</span> : null}
      </p>
      {artifact.body ? <p style={{ whiteSpace: 'pre-wrap' }}>{artifact.body}</p> : null}
      {artifact.payload && Object.keys(artifact.payload).length > 0 ? (
        <pre className="artifact-json">{stringifyPayload(artifact.payload)}</pre>
      ) : null}
    </div>
  )
}
