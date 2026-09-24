"use client";

import { type ReactNode } from "react";
import { CursorProvider } from "@/components/chrome/CursorProvider";
import { CustomCursor } from "@/components/chrome/CustomCursor";
import { Loader } from "@/components/chrome/Loader";
import { LoadingProvider } from "@/components/chrome/LoadingProvider";
import { Navigation } from "@/components/chrome/Navigation";
import { NoiseOverlay } from "@/components/chrome/NoiseOverlay";

export function SiteShell({ children }: { children: ReactNode }) {
  return (
    <LoadingProvider>
      <CursorProvider>
        <Loader />
        <CustomCursor />
        <NoiseOverlay />
        <Navigation />
        <div className="relative z-0 flex min-h-full flex-1 flex-col">{children}</div>
      </CursorProvider>
    </LoadingProvider>
  );
}
