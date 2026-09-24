import { Navigate, Route, Routes } from 'react-router-dom'
import { AppShell } from '../components/layout/AppShell'
import { authMode } from '../config/hiringApiBaseUrl'
import { CandidatesPage } from '../pages/CandidatesPage'
import { JoinPage } from '../pages/JoinPage'
import { JobsPage } from '../pages/JobsPage'
import { LoginPage } from '../pages/LoginPage'
import { MatchPage } from '../pages/MatchPage'
import { OnboardingPage } from '../pages/OnboardingPage'
import { SettingsPage } from '../pages/SettingsPage'
import { SourcingPage } from '../pages/SourcingPage'
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
        <Route element={<AppShell />}>
          <Route path="/workspace" element={<WorkspacePage />} />
          <Route path="/jobs" element={<JobsPage />} />
          <Route path="/candidates" element={<CandidatesPage />} />
          <Route path="/sourcing" element={<SourcingPage />} />
          <Route path="/match" element={<MatchPage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route index element={<Navigate to={mode === 'firebase' ? '/login' : '/workspace'} replace />} />
        </Route>
      </Route>
      <Route path="*" element={<Navigate to="/workspace" replace />} />
    </Routes>
  )
}
