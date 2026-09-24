import { Link } from 'react-router-dom'
import { useAuth } from '../auth/AuthProvider'

export function WorkspacePage() {
  const auth = useAuth()
  const membership = auth.memberships.find((item) => item.organization_id === auth.orgId) ?? auth.memberships[0]

  return (
    <div className="workspace-page">
      <header className="workspace-header">
        <div>
          <p className="auth-eyebrow">Hiring AI</p>
          <h1>{membership?.organization_name ?? 'Workspace'}</h1>
          <p>
            Signed in as {auth.me?.display_name || auth.me?.email || 'recruiter'}
            {membership ? ` · ${membership.role}` : ''}
          </p>
        </div>
        <div className="workspace-actions">
          <Link to="/join">Redeem invite</Link>
          <button type="button" onClick={() => void auth.signOutUser()}>
            Sign out
          </button>
        </div>
      </header>
      <section className="workspace-panel">
        <h2>Ready for your client pilot</h2>
        <p>
          Auth is live. Create invite codes from the owner account, share the hosted app URL, and
          let recruiters join with Firebase sign-in.
        </p>
        {auth.memberships.length === 0 ? (
          <p>
            No organization yet. <Link to="/onboarding">Create one</Link> or{' '}
            <Link to="/join">join with an invite</Link>.
          </p>
        ) : (
          <ul>
            {auth.memberships.map((item) => (
              <li key={item.membership_id}>
                <button type="button" onClick={() => auth.selectOrg(item.organization_id)}>
                  {item.organization_name} ({item.role})
                </button>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  )
}
