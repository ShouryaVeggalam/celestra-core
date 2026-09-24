import { Link } from 'react-router-dom'
import { useAuth } from '../auth/AuthProvider'

export function WorkspacePage() {
  const auth = useAuth()
  const membership =
    auth.memberships.find((item) => item.organization_id === auth.orgId) ?? auth.memberships[0]

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <p className="auth-eyebrow">Today</p>
          <h1>{membership?.organization_name ?? 'Workspace'}</h1>
          <p>Find job seekers, import them, and hire through your organization.</p>
        </div>
      </header>
      <section className="card-grid">
        <Link className="action-card" to="/sourcing">
          <h2>Source talent</h2>
          <p>Discover open-to-work profiles or upload a board CSV, then import candidates.</p>
        </Link>
        <Link className="action-card" to="/jobs">
          <h2>Open a job</h2>
          <p>Create roles so sourcing and candidates stay linked to hiring needs.</p>
        </Link>
        <Link className="action-card" to="/candidates">
          <h2>Review pipeline</h2>
          <p>Imported candidates land here. Mark hired when your team decides.</p>
        </Link>
        <Link className="action-card" to="/settings">
          <h2>Invite your client team</h2>
          <p>Create invite codes for recruiters. Share the app URL + code.</p>
        </Link>
      </section>
    </div>
  )
}
