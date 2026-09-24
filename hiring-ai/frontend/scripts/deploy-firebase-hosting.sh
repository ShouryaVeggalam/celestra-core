#!/usr/bin/env bash
# Deploy Hiring AI frontend to Firebase Hosting (free, permanent, no vercel.com).
# Prerequisite: firebase login (same Google account as Revenue AI).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

if [[ -z "${VITE_HIRING_API_URL:-}" ]]; then
  echo "Set VITE_HIRING_API_URL to your public API (e.g. https://hiring-api.onrender.com)" >&2
  exit 1
fi

export VITE_AUTH_MODE=firebase
export VITE_FIREBASE_API_KEY="${VITE_FIREBASE_API_KEY:-AIzaSyC8eKKUStSHrTyuVeva9UnbDDRerLagIOM}"
export VITE_FIREBASE_AUTH_DOMAIN="${VITE_FIREBASE_AUTH_DOMAIN:-celestra-revenue-dev.firebaseapp.com}"
export VITE_FIREBASE_PROJECT_ID="${VITE_FIREBASE_PROJECT_ID:-celestra-revenue-dev}"
export VITE_FIREBASE_APP_ID="${VITE_FIREBASE_APP_ID:-1:258268341724:web:aa69dbbb120b7591b3db19}"
export VITE_FIREBASE_MESSAGING_SENDER_ID="${VITE_FIREBASE_MESSAGING_SENDER_ID:-258268341724}"

npm run build
npx --yes firebase-tools deploy --only hosting --project celestra-revenue-dev --non-interactive

echo
echo "App URL: https://celestra-revenue-dev.web.app"
echo "Also:    https://celestra-revenue-dev.firebaseapp.com"
