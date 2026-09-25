# Production client launch checklist

Complete before any paying pilot goes live.

## 1. Auth (Firebase)

- [ ] Firebase project created for the client
- [ ] Email/Password + Google providers enabled
- [ ] Authorized domain = Vercel host
- [ ] `AUTH_MODE=firebase` (never `dev` for clients)
- [ ] `FIREBASE_PROJECT_ID` set on Render
- [ ] `VITE_AUTH_MODE=firebase` + `VITE_FIREBASE_*` set on Vercel
- [ ] `OAUTH_REDIRECT_URL=https://<vercel>/auth/callback`
- [ ] First owner signs in and creates the organization
- [ ] Invite codes issued for other recruiters
- [ ] Roles verified: owner/admin can invite; members redeem only

## 2. Hosting & data

- [ ] Render API + Vercel frontend (`hiring-ai/` roots)
- [ ] Hosted PostgreSQL (not SQLite, not localhost)
- [ ] `alembic upgrade head` on boot; `/ready` → `database=ok`
- [ ] CORS locked to Vercel origins
- [ ] Strong `INVITE_CODE_PEPPER`
- [ ] `SEED_DEMO_TENANT=false`

## 3. Share package for the client

Send:

1. App URL (Vercel)
2. One-time invite code (from owner Settings / onboarding)
3. Optional: this checklist + support contact

Client steps: open URL → create Firebase account / Google sign-in → redeem invite → workspace.

## 4. Sign-off

No go-live with `AUTH_MODE=dev` or SQLite. `/ready` must show `firebase=ok`.
