import { Navigate, Route, Routes } from 'react-router-dom'
import { AppShell } from '../components/layout/AppShell'
import { authMode } from '../config/hiringApiBaseUrl'
import { AnalyticsPage } from '../pages/AnalyticsPage'
import { AutonomousPage } from '../pages/AutonomousPage'
import { CandidatePortalPage } from '../pages/CandidatePortalPage'
import { CandidatesPage } from '../pages/CandidatesPage'
import { CompensationPage } from '../pages/CompensationPage'
import { ForecastPage } from '../pages/ForecastPage'
import { HiringChiefPage } from '../pages/HiringChiefPage'
import { InterviewsPage } from '../pages/InterviewsPage'
import { IntegrationsPage } from '../pages/IntegrationsPage'
import { JoinPage } from '../pages/JoinPage'
import { JobsPage } from '../pages/JobsPage'
import { LoginPage } from '../pages/LoginPage'
import { MatchPage } from '../pages/MatchPage'
import { OnboardingPage } from '../pages/OnboardingPage'
import { OutreachPage } from '../pages/OutreachPage'
import { PlaybooksPage } from '../pages/PlaybooksPage'
import { ReferralsPage } from '../pages/ReferralsPage'
import { ReviewsPage } from '../pages/ReviewsPage'
import { SettingsPage } from '../pages/SettingsPage'
import { SkillsPage } from '../pages/SkillsPage'
import { SourcingPage } from '../pages/SourcingPage'
import { WorkspacePage } from '../pages/WorkspacePage'
import { RequireAuth } from './RequireAuth'

export function AppRoutes() {
  const mode = authMode()
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/join" element={<JoinPage />} />
      <Route path="/portal/:token" element={<CandidatePortalPage />} />
      <Route path="/auth/callback" element={<Navigate to="/workspace" replace />} />
      <Route element={<RequireAuth />}>
        <Route path="/onboarding" element={<OnboardingPage />} />
        <Route element={<AppShell />}>
          <Route path="/workspace" element={<WorkspacePage />} />
          <Route path="/jobs" element={<JobsPage />} />
          <Route path="/candidates" element={<CandidatesPage />} />
          <Route path="/sourcing" element={<SourcingPage />} />
          <Route path="/match" element={<MatchPage />} />
          <Route path="/outreach" element={<OutreachPage />} />
          <Route path="/referrals" element={<ReferralsPage />} />
          <Route path="/reviews" element={<ReviewsPage />} />
          <Route path="/interviews" element={<InterviewsPage />} />
          <Route path="/skills" element={<SkillsPage />} />
          <Route path="/compensation" element={<CompensationPage />} />
          <Route path="/forecast" element={<ForecastPage />} />
          <Route path="/playbooks" element={<PlaybooksPage />} />
          <Route path="/hiring-chief" element={<HiringChiefPage />} />
          <Route path="/autonomous" element={<AutonomousPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/integrations" element={<IntegrationsPage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route index element={<Navigate to={mode === 'firebase' ? '/login' : '/workspace'} replace />} />
        </Route>
      </Route>
      <Route path="*" element={<Navigate to="/workspace" replace />} />
    </Routes>
  )
}
