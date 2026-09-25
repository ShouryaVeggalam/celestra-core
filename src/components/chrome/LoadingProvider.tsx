"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

let hasLoaded = false;

type LoadingContextValue = {
  ready: boolean;
  markReady: () => void;
};

const LoadingContext = createContext<LoadingContextValue | null>(null);

function alreadyLoaded() {
  if (hasLoaded) return true;
  if (typeof window === "undefined") return false;
  try {
    return sessionStorage.getItem("celestra-loaded") === "1";
  } catch {
    return false;
  }
}

export function LoadingProvider({ children }: { children: ReactNode }) {
  const [ready, setReady] = useState(false);

  const markReady = useCallback(() => {
    hasLoaded = true;
    try {
      sessionStorage.setItem("celestra-loaded", "1");
    } catch {
      /* ignore */
    }
    setReady(true);
  }, []);

  useEffect(() => {
    if (alreadyLoaded()) markReady();
  }, [markReady]);

  const value = useMemo(() => ({ ready, markReady }), [ready, markReady]);

  return <LoadingContext.Provider value={value}>{children}</LoadingContext.Provider>;
}

export function useLoading() {
  const context = useContext(LoadingContext);
  if (!context) {
    throw new Error("useLoading must be used within LoadingProvider");
  }
  return context;
}
