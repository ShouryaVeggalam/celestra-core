import { NavLink, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../../auth/AuthProvider'

const NAV = [
  {
    label: 'Hiring',
    items: [
      { to: '/workspace', label: 'Workspace' },
      { to: '/jobs', label: 'Jobs' },
      { to: '/candidates', label: 'Candidates' },
      { to: '/sourcing', label: 'Sourcing' },
      { to: '/outreach', label: 'Outreach' },
      { to: '/referrals', label: 'Referrals' },
    ],
  },
  {
    label: 'Intelligence',
    items: [
      { to: '/reviews', label: 'Reviews' },
      { to: '/interviews', label: 'Interviews' },
      { to: '/skills', label: 'Skills' },
      { to: '/compensation', label: 'Compensation' },
      { to: '/forecast', label: 'Forecast' },
      { to: '/playbooks', label: 'Playbooks' },
    ],
  },
  {
    label: 'System',
    items: [
      { to: '/hiring-chief', label: 'Hiring Chief' },
      { to: '/autonomous', label: 'Autonomous' },
      { to: '/analytics', label: 'Analytics' },
      { to: '/integrations', label: 'Integrations' },
      { to: '/settings', label: 'Settings' },
    ],
  },
]

function titleFromPath(pathname: string): string {
  const part = pathname.split('/').filter(Boolean)[0] ?? 'workspace'
  return part
    .split('-')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}

export function AppShell() {
  const auth = useAuth()
  const location = useLocation()
  const membership =
    auth.memberships.find((item) => item.organization_id === auth.orgId) ?? auth.memberships[0]
  const pageTitle = titleFromPath(location.pathname)

  return (
    <div className="ops-shell">
      <aside className="ops-nav">
        <div className="ops-brand">
          <span className="ops-brand__mark" aria-hidden>
            H
          </span>
          <div>
            <strong>Hiring AI</strong>
            <p>{membership?.organization_name ?? 'Organization'}</p>
          </div>
        </div>

        {NAV.map((section) => (
          <div key={section.label} className="ops-nav__section">
            <p className="ops-nav__label">{section.label}</p>
            <nav>
              {section.items.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={({ isActive }) => (isActive ? 'active' : undefined)}
                >
                  {item.label}
                </NavLink>
              ))}
            </nav>
          </div>
        ))}

        <div className="ops-nav__footer">
          <p>{auth.me?.display_name || auth.me?.email || 'Recruiter'}</p>
          <button type="button" className="ops-signout" onClick={() => void auth.signOutUser()}>
            Sign out
          </button>
        </div>
      </aside>

      <div className="ops-main">
        <header className="ops-topbar">
          <div className="ops-crumbs">
            <span>Hiring AI</span>
            <span aria-hidden>/</span>
            <strong>{pageTitle}</strong>
          </div>
          <div className="ops-topbar__right">
            <span className="ops-review-pill">
              <span className="ops-review-dot" aria-hidden />
              Human review required
            </span>
            <label className="ops-search">
              <span className="sr-only">Search</span>
              <input type="search" placeholder="Search candidates, jobs, reviews…" disabled />
              <kbd>⌘K</kbd>
            </label>
            <button type="button" className="ops-bell" aria-label="Notifications">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden>
                <path
                  d="M6 9a6 6 0 1 1 12 0c0 7 3 7 3 7H3s3 0 3-7Zm6 11a2 2 0 0 0 2-2h-4a2 2 0 0 0 2 2Z"
                  stroke="currentColor"
                  strokeWidth="1.6"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </button>
          </div>
        </header>
        <div className="ops-content">
          <Outlet />
        </div>
      </div>
    </div>
  )
}
