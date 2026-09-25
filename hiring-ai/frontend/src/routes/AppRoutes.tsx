import { Navigate, Route, Routes } from 'react-router-dom'
import { AppShell } from '../components/layout/AppShell'
import { authMode } from '../config/hiringApiBaseUrl'
import { CandidatesPage } from '../pages/CandidatesPage'
import { JoinPage } from '../pages/JoinPage'
import { JobsPage } from '../pages/JobsPage'
import { LoginPage } from '../pages/LoginPage'
import { MatchPage } from '../pages/MatchPage'
import { OnboardingPage } from '../pages/OnboardingPage'
import { PlaceholderPage } from '../pages/PlaceholderPage'
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
          <Route
            path="/outreach"
            element={
              <PlaceholderPage
                title="Outreach"
                summary="Draft and track recruiter outreach. Sends stay human-approved."
                cta={{ to: '/candidates', label: 'Review candidates' }}
              />
            }
          />
          <Route
            path="/referrals"
            element={
              <PlaceholderPage
                title="Referrals"
                summary="Capture employee referrals into the same hire path as sourced talent."
                cta={{ to: '/candidates', label: 'Open pipeline' }}
              />
            }
          />
          <Route
            path="/reviews"
            element={
              <PlaceholderPage
                title="Reviews"
                summary="Human review queues for discoveries, matches, and stage changes."
                cta={{ to: '/workspace', label: 'Back to workspace' }}
              />
            }
          />
          <Route
            path="/interviews"
            element={
              <PlaceholderPage
                title="Interviews"
                summary="Interview plans and feedback stay human-led — no auto-scheduling."
              />
            }
          />
          <Route
            path="/skills"
            element={
              <PlaceholderPage
                title="Skills"
                summary="Skill evidence from profiles and matches, for recruiter judgment."
                cta={{ to: '/match', label: 'Open Match' }}
              />
            }
          />
          <Route
            path="/compensation"
            element={
              <PlaceholderPage
                title="Compensation"
                summary="Compensation ranges and offer framing for hiring managers."
              />
            }
          />
          <Route
            path="/forecast"
            element={
              <PlaceholderPage
                title="Forecast"
                summary="Hiring capacity and pipeline forecast for your organization."
              />
            }
          />
          <Route
            path="/playbooks"
            element={
              <PlaceholderPage
                title="Playbooks"
                summary="Repeatable hiring playbooks your team can follow screen by screen."
              />
            }
          />
          <Route
            path="/hiring-chief"
            element={
              <PlaceholderPage
                title="Hiring Chief"
                summary="Org-level hiring posture and priorities. Actions still require humans."
                cta={{ to: '/workspace', label: 'Open workspace' }}
              />
            }
          />
          <Route
            path="/autonomous"
            element={
              <PlaceholderPage
                title="Autonomous"
                summary="Guardrails for any assisted workflows. Hire/reject stays explicit."
              />
            }
          />
          <Route
            path="/analytics"
            element={
              <PlaceholderPage
                title="Analytics"
                summary="Funnel and source analytics for this organization."
              />
            }
          />
          <Route
            path="/integrations"
            element={
              <PlaceholderPage
                title="Integrations"
                summary="GitHub sourcing, Groq drafts, and Firebase auth connections."
                cta={{ to: '/settings', label: 'Open settings' }}
              />
            }
          />
          <Route index element={<Navigate to={mode === 'firebase' ? '/login' : '/workspace'} replace />} />
        </Route>
      </Route>
      <Route path="*" element={<Navigate to="/workspace" replace />} />
    </Routes>
  )
}
