"use client";

import dynamic from "next/dynamic";
import Link from "next/link";
import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Magnetic } from "@/components/chrome/Magnetic";
import { TypeLine } from "@/components/chrome/TypeLine";
import { useLoading } from "@/components/chrome/LoadingProvider";
import { BookDemoCta } from "@/components/book-demo/book-demo-cta";
import { Button } from "@/components/ui/button";
import { usePrefersReducedMotion } from "@/lib/motion";

const HeroScene = dynamic(() => import("@/components/home/HeroScene"), {
  ssr: false,
});

let heroHasTyped = false;

export function Hero() {
  const { ready } = useLoading();
  const reduced = usePrefersReducedMotion();
  const [typed, setTyped] = useState(heroHasTyped);
  const [start, setStart] = useState(false);

  useEffect(() => {
    if (!ready) return;
    if (heroHasTyped) {
      setTyped(true);
      return;
    }
    const id = window.setTimeout(() => setStart(true), reduced ? 0 : 220);
    return () => window.clearTimeout(id);
  }, [ready, reduced]);

  const headline = "Building the Intelligence Stack.";

  return (
    <section className="relative flex min-h-[100svh] items-end overflow-hidden bg-black">
      <div className="absolute inset-0">
        {reduced ? <div className="hero-fallback" /> : <HeroScene />}
        <div className="pointer-events-none absolute inset-0 bg-black/25" />
        <div className="pointer-events-none absolute inset-x-0 bottom-0 h-40 bg-black/80" />
      </div>

      <div className="relative z-10 grid-page w-full pb-20 pt-32 md:pb-24">
        <p className="label mb-8 text-foreground/70">Celestra</p>
        <h1 className="display max-w-[14ch] text-foreground">
          {typed && !start ? (
            headline
          ) : start ? (
            <TypeLine
              text={headline}
              started={start}
              hideCursorWhenDone
              interval={32}
              onComplete={() => {
                heroHasTyped = true;
                setTyped(true);
              }}
            />
          ) : (
            <span className="opacity-0">{headline}</span>
          )}
        </h1>

        <motion.p
          className="editorial mt-8 max-w-[36rem]"
          initial={{ opacity: 0, y: 12 }}
          animate={typed || reduced ? { opacity: 1, y: 0 } : { opacity: 0, y: 12 }}
          transition={{ duration: 0.9, ease: [0.22, 1, 0.36, 1] }}
        >
          From AI Agents to Quantum Computing, Celestra is building the systems
          that will power the next generation of intelligence.
        </motion.p>

        <motion.div
          className="mt-12 flex flex-col gap-4 sm:flex-row sm:items-center"
          initial={{ opacity: 0, y: 12 }}
          animate={typed || reduced ? { opacity: 1, y: 0 } : { opacity: 0, y: 12 }}
          transition={{ duration: 0.9, delay: 0.12, ease: [0.22, 1, 0.36, 1] }}
        >
          <Magnetic>
            <Button asChild>
              <Link href="/vision">Explore Vision</Link>
            </Button>
          </Magnetic>
          <Magnetic>
            <Button asChild variant="ghost">
              <Link href="/ventures">Explore Ventures</Link>
            </Button>
          </Magnetic>
          <BookDemoCta variant="ghost" label="Book Demo" />
        </motion.div>

        <div className="mt-20 flex items-center gap-4 text-[10px] tracking-[0.28em] text-muted uppercase">
          <span className="block h-10 w-px bg-border" />
          Scroll
        </div>
      </div>
    </section>
  );
}
