import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../auth/AuthProvider'

export function RequireAuth() {
  const auth = useAuth()
  if (auth.loading) {
    return (
      <div className="auth-page">
        <p>Loading session…</p>
      </div>
    )
  }
  if (auth.mode === 'firebase' && !auth.firebaseUser) {
    return <Navigate to="/login" replace />
  }
  return <Outlet />
}
