import { Navigate, Route, Routes } from 'react-router-dom'
import { authMode } from '../config/hiringApiBaseUrl'
import { JoinPage } from '../pages/JoinPage'
import { LoginPage } from '../pages/LoginPage'
import { OnboardingPage } from '../pages/OnboardingPage'
import { WorkspacePage } from '../pages/WorkspacePage'
import { RequireAuth } from './RequireAuth'

export function AppRoutes() {
  const mode = authMode()
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/join" element={<JoinPage />} />
      <Route path="/auth/callback" element={<Navigate to="/workspace" replace />} />
      <Route element={<RequireAuth />}>
        <Route path="/onboarding" element={<OnboardingPage />} />
        <Route path="/workspace" element={<WorkspacePage />} />
        <Route index element={<Navigate to={mode === 'firebase' ? '/login' : '/workspace'} replace />} />
      </Route>
      <Route path="*" element={<Navigate to="/workspace" replace />} />
    </Routes>
  )
}
