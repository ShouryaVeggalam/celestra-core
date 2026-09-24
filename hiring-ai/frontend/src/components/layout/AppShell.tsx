import { NavLink, Outlet } from 'react-router-dom'
import { useAuth } from '../../auth/AuthProvider'

const LINKS = [
  { to: '/workspace', label: 'Workspace' },
  { to: '/jobs', label: 'Jobs' },
  { to: '/candidates', label: 'Candidates' },
  { to: '/sourcing', label: 'Sourcing' },
  { to: '/settings', label: 'Settings' },
]

export function AppShell() {
  const auth = useAuth()
  const membership =
    auth.memberships.find((item) => item.organization_id === auth.orgId) ?? auth.memberships[0]

  return (
    <div className="app-shell">
      <aside className="app-nav">
        <p className="auth-eyebrow">Hiring AI</p>
        <strong>{membership?.organization_name ?? 'Your org'}</strong>
        <nav>
          {LINKS.map((link) => (
            <NavLink key={link.to} to={link.to} className={({ isActive }) => (isActive ? 'active' : undefined)}>
              {link.label}
            </NavLink>
          ))}
        </nav>
        <div className="app-nav__footer">
          <p>{auth.me?.display_name || auth.me?.email || 'Recruiter'}</p>
          <button type="button" onClick={() => void auth.signOutUser()}>
            Sign out
          </button>
        </div>
      </aside>
      <main className="app-main">
        <Outlet />
      </main>
    </div>
  )
}
