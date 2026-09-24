const DEMO_ORG_ID = '00000000-0000-4000-8000-000000000001'
const DEMO_USER_ID = '00000000-0000-4000-8000-000000000002'

export type AuthMode = 'dev' | 'firebase'

export function hiringApiBaseUrl(): string {
  return (import.meta.env.VITE_HIRING_API_URL as string | undefined)?.replace(/\/$/, '') ?? ''
}

export function authMode(): AuthMode {
  const mode = (import.meta.env.VITE_AUTH_MODE as string | undefined)?.trim().toLowerCase()
  return mode === 'firebase' ? 'firebase' : 'dev'
}

export function hiringOrgId(): string {
  return (import.meta.env.VITE_HIRING_ORG_ID as string | undefined) || DEMO_ORG_ID
}

export function hiringUserId(): string {
  return (import.meta.env.VITE_HIRING_USER_ID as string | undefined) || DEMO_USER_ID
}

export function firebaseConfig() {
  return {
    apiKey: import.meta.env.VITE_FIREBASE_API_KEY as string | undefined,
    authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN as string | undefined,
    projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID as string | undefined,
    appId: import.meta.env.VITE_FIREBASE_APP_ID as string | undefined,
    messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID as string | undefined,
  }
}
