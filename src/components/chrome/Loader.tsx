"use client";

import { useLayoutEffect, useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { useLoading } from "@/components/chrome/LoadingProvider";
import { TypeLine } from "@/components/chrome/TypeLine";

function wasSeen() {
  try {
    return sessionStorage.getItem("celestra-loaded") === "1";
  } catch {
    return false;
  }
}

export function Loader() {
  const { ready, markReady } = useLoading();
  const [play, setPlay] = useState(false);
  const [phase, setPhase] = useState<"brand" | "type" | "hold">("brand");

  useLayoutEffect(() => {
    if (ready) return;
    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduced || wasSeen()) {
      markReady();
    }
  }, [markReady, ready]);

  useEffect(() => {
    if (ready || wasSeen()) return;
    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduced) return;

    setPlay(true);
    const brand = window.setTimeout(() => setPhase("type"), 700);
    const failsafe = window.setTimeout(markReady, 4200);
    return () => {
      window.clearTimeout(brand);
      window.clearTimeout(failsafe);
    };
  }, [markReady, ready]);

  useEffect(() => {
    if (phase !== "hold") return;
    const done = window.setTimeout(markReady, 720);
    return () => window.clearTimeout(done);
  }, [phase, markReady]);

  if (ready) return null;

  return (
    <AnimatePresence>
      <motion.div
        className="fixed inset-0 z-[90] flex items-center justify-center bg-black"
        initial={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        transition={{ duration: 0.85, ease: [0.22, 1, 0.36, 1] }}
      >
        {play ? (
          <div className="flex w-[min(92vw,36rem)] flex-col items-start gap-8 px-6">
            <motion.p
              className="label text-foreground"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
            >
              Celestra
            </motion.p>
            <p className="display-md text-foreground">
              {phase === "brand" ? (
                <span className="invisible">Building the Intelligence Stack...</span>
              ) : (
                <TypeLine
                  text="Building the Intelligence Stack..."
                  started
                  cursor
                  interval={34}
                  onComplete={() => setPhase("hold")}
                />
              )}
            </p>
          </div>
        ) : null}
      </motion.div>
    </AnimatePresence>
  );
}
