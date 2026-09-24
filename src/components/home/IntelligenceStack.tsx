"use client";

import Link from "next/link";
import { useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { useGSAP } from "@gsap/react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { stackLayers } from "@/lib/stack";
import { cn } from "@/lib/utils";
import { usePrefersReducedMotion } from "@/lib/motion";

gsap.registerPlugin(ScrollTrigger, useGSAP);

type IntelligenceStackProps = {
  kicker?: string;
  compact?: boolean;
};

export function IntelligenceStack({
  kicker = "03 — Architecture",
  compact = false,
}: IntelligenceStackProps) {
  const [active, setActive] = useState<number | null>(null);
  const root = useRef<HTMLElement>(null);
  const reduced = usePrefersReducedMotion();

  useGSAP(
    () => {
      if (reduced) return;
      const line = root.current?.querySelector<HTMLElement>("[data-spine]");
      if (!line) return;
      gsap.set(line, { scaleY: 0 });
      gsap.to(line, {
        scaleY: 1,
        ease: "none",
        scrollTrigger: {
          trigger: root.current,
          start: "top 70%",
          end: "bottom 55%",
          scrub: 0.6,
        },
      });
    },
    { scope: root },
  );

  return (
    <section
      ref={root}
      className={cn("relative bg-black", compact ? "py-24 md:py-32" : "py-32 md:py-44")}
    >
      <div className="grid-page grid gap-16 lg:grid-cols-12">
        <div className="lg:col-span-4">
          <p className="label">{kicker}</p>
          <h2 className="display-md mt-8 max-w-[10ch] text-foreground">
            The Intelligence Stack
          </h2>
          <p className="editorial mt-8 max-w-[26rem]">
            One architecture. Four layers. Applications rest on intelligence.
            Intelligence rests on compute. Compute inhabits the physical world.
          </p>
        </div>

        <div className="relative lg:col-span-8">
          <div
            data-spine
            className="pointer-events-none absolute top-8 bottom-8 left-[15px] hidden w-px origin-top bg-border md:block"
          />

          <div className="flex flex-col">
            {stackLayers.map((layer, index) => {
              const open = active === index;
              return (
                <article
                  key={layer.id}
                  className="relative border-t border-border last:border-b"
                  onMouseEnter={() => setActive(index)}
                  onFocus={() => setActive(index)}
                >
                  <button
                    type="button"
                    data-cursor="expand"
                    className="flex w-full items-start gap-6 py-8 text-left md:gap-10 md:py-10"
                    onClick={() => setActive(open ? null : index)}
                    aria-expanded={open}
                  >
                    <span
                      className={cn(
                        "mt-2 hidden h-2.5 w-2.5 shrink-0 rounded-full border md:block",
                        open
                          ? "border-foreground bg-foreground"
                          : "border-muted bg-transparent",
                      )}
                    />
                    <span className="label mt-1 w-10 shrink-0">{layer.index}</span>
                    <div className="min-w-0 flex-1">
                      <div className="flex items-baseline justify-between gap-6">
                        <h3 className="text-3xl tracking-tight text-foreground md:text-5xl">
                          {layer.title}
                        </h3>
                        <span className="label hidden sm:block">
                          {open ? "Open" : "Layer"}
                        </span>
                      </div>
                      <p className="mt-3 max-w-[36rem] text-[15px] leading-relaxed text-muted md:text-base">
                        {layer.statement}
                      </p>
                    </div>
                  </button>

                  <AnimatePresence initial={false}>
                    {open ? (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.55, ease: [0.22, 1, 0.36, 1] }}
                        className="overflow-hidden"
                      >
                        <div className="pb-10 pl-0 md:pl-[5.75rem]">
                          <p className="max-w-[36rem] text-[15px] leading-relaxed text-muted">
                            {layer.body}
                          </p>
                          <div className="relative mt-8 flex flex-wrap gap-3">
                            <svg
                              className="pointer-events-none absolute -top-5 left-0 hidden h-5 w-full md:block"
                              aria-hidden
                            >
                              <motion.line
                                x1="0"
                                y1="16"
                                x2="100%"
                                y2="16"
                                stroke="#27272A"
                                strokeWidth="1"
                                initial={{ pathLength: 0 }}
                                animate={{ pathLength: 1 }}
                                transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
                              />
                            </svg>
                            {layer.nodes.map((node, nodeIndex) => (
                              <motion.div
                                key={node.href}
                                initial={{ opacity: 0, y: 8 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{
                                  delay: 0.08 * nodeIndex,
                                  duration: 0.5,
                                  ease: [0.22, 1, 0.36, 1],
                                }}
                              >
                                <Link
                                  href={node.href}
                                  data-cursor="expand"
                                  className="group inline-flex items-center gap-3 border border-border px-4 py-3 text-[12px] tracking-[0.16em] uppercase text-muted transition-colors duration-500 hover:border-foreground hover:text-foreground"
                                >
                                  <span className="h-px w-6 bg-border transition-colors group-hover:bg-foreground" />
                                  {node.label}
                                </Link>
                              </motion.div>
                            ))}
                          </div>
                        </div>
                      </motion.div>
                    ) : null}
                  </AnimatePresence>
                </article>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}
