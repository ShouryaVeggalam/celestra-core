import { initializeApp, type FirebaseApp } from 'firebase/app'
import {
  getAuth,
  GoogleAuthProvider,
  createUserWithEmailAndPassword,
  onAuthStateChanged,
  signInWithEmailAndPassword,
  signInWithPopup,
  signOut,
  type Auth,
  type User as FirebaseUser,
} from 'firebase/auth'
import {
  createContext,
  createElement,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import { authMode, firebaseConfig } from '../config/hiringApiBaseUrl'
import { hiringApi, setAuthTokenProvider, setOrganizationId, getOrganizationId } from '../api/hiringApi'
import type { MeResponse, Membership } from '../api/contracts'

type AuthContextValue = {
  mode: 'dev' | 'firebase'
  loading: boolean
  firebaseUser: FirebaseUser | null
  me: MeResponse | null
  memberships: Membership[]
  orgId: string | null
  error: string | null
  signInEmail: (email: string, password: string) => Promise<void>
  signUpEmail: (email: string, password: string) => Promise<void>
  signInGoogle: () => Promise<void>
  signOutUser: () => Promise<void>
  refreshMe: () => Promise<MeResponse | null>
  selectOrg: (orgId: string) => void
}

const AuthContext = createContext<AuthContextValue | null>(null)

let app: FirebaseApp | null = null
let auth: Auth | null = null

function ensureFirebase(): Auth {
  if (auth) return auth
  const config = firebaseConfig()
  if (!config.apiKey || !config.projectId) {
    throw new Error('Firebase is not configured. Set VITE_FIREBASE_* env vars.')
  }
  app = initializeApp(config)
  auth = getAuth(app)
  return auth
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const mode = authMode()
  const [loading, setLoading] = useState(true)
  const [firebaseUser, setFirebaseUser] = useState<FirebaseUser | null>(null)
  const [me, setMe] = useState<MeResponse | null>(null)
  const [orgId, setOrgId] = useState<string | null>(() => getOrganizationId())
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (mode === 'dev') {
      setAuthTokenProvider(null)
      void hiringApi
        .getMe()
        .then((profile) => {
          setMe(profile)
          if (!orgId && profile.memberships[0]) {
            const next = profile.memberships[0].organization_id
            setOrganizationId(next)
            setOrgId(next)
          }
        })
        .catch(() => setMe(null))
        .finally(() => setLoading(false))
      return
    }

    const firebaseAuth = ensureFirebase()
    setAuthTokenProvider(async () => {
      const current = firebaseAuth.currentUser
      if (!current) return null
      return current.getIdToken()
    })

    const unsub = onAuthStateChanged(firebaseAuth, async (user) => {
      setFirebaseUser(user)
      if (!user) {
        setMe(null)
        setLoading(false)
        return
      }
      try {
        const profile = await hiringApi.getMe()
        setMe(profile)
        if (!getOrganizationId() && profile.memberships[0]) {
          const next = profile.memberships[0].organization_id
          setOrganizationId(next)
          setOrgId(next)
        }
      } catch (caught) {
        setError(caught instanceof Error ? caught.message : 'Session failed')
        setMe(null)
      } finally {
        setLoading(false)
      }
    })
    return () => unsub()
  }, [mode])

  const value = useMemo<AuthContextValue>(
    () => ({
      mode,
      loading,
      firebaseUser,
      me,
      memberships: me?.memberships ?? [],
      orgId,
      error,
      async signInEmail(email, password) {
        setError(null)
        await signInWithEmailAndPassword(ensureFirebase(), email, password)
      },
      async signUpEmail(email, password) {
        setError(null)
        await createUserWithEmailAndPassword(ensureFirebase(), email, password)
      },
      async signInGoogle() {
        setError(null)
        await signInWithPopup(ensureFirebase(), new GoogleAuthProvider())
      },
      async signOutUser() {
        if (mode === 'firebase') await signOut(ensureFirebase())
        setMe(null)
        setOrganizationId(null)
        setOrgId(null)
      },
      async refreshMe() {
        const profile = await hiringApi.getMe()
        setMe(profile)
        return profile
      },
      selectOrg(next) {
        setOrganizationId(next)
        setOrgId(next)
      },
    }),
    [mode, loading, firebaseUser, me, orgId, error],
  )

  return createElement(AuthContext.Provider, { value }, children)
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}

export function useRequireAuth() {
  return useAuth()
}
