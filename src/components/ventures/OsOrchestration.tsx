"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Reveal } from "@/components/chrome/Reveal";
import { cn } from "@/lib/utils";

const runtime = [
  {
    id: "workflow",
    title: "Workflow Engine",
    body: "Coordinate agents, people, and systems across multi-step enterprise processes.",
  },
  {
    id: "ops",
    title: "Operational Intelligence",
    body: "Continuously observe, analyze, and optimize real-time business operations.",
  },
  {
    id: "agents",
    title: "Agent Runtime",
    body: "Persistent workers with memory, tools, and permissions — governed by the OS.",
  },
  {
    id: "gov",
    title: "Governance",
    body: "Permissions, audit logs, security, observability, and compliance as first-class controls.",
  },
] as const;

export function OsOrchestration() {
  const [active, setActive] = useState<(typeof runtime)[number]["id"] | null>(
    "workflow",
  );
  const selected = runtime.find((item) => item.id === active);

  return (
    <section className="border-t border-border py-28 md:py-36">
      <div className="grid-page grid gap-16 lg:grid-cols-12">
        <div className="lg:col-span-4">
          <Reveal>
            <p className="label">Architecture</p>
            <h2 className="display-md mt-8 max-w-[12ch]">
              From systems to execution.
            </h2>
            <p className="editorial mt-8 max-w-[26rem]">
              Celestra OS sits between enterprise systems and business execution —
              orchestrating agents, workflows, operational intelligence, and
              governance above language intelligence and foundation models.
            </p>
          </Reveal>
        </div>

        <div className="lg:col-span-8">
          <Reveal delay={0.08}>
            <div className="border border-border">
              <DiagramRow label="01" title="Enterprise Systems" muted />

              <Connector />

              <DiagramRow
                label="02"
                title="Celestra OS"
                emphasis
                body="AI Operating System · Execution Layer"
              />

              <Connector />

              <div className="border-t border-border px-6 py-8 md:px-10">
                <p className="label mb-6">Runtime</p>
                <div className="grid gap-px bg-border sm:grid-cols-2">
                  {runtime.map((item) => {
                    const open = active === item.id;
                    return (
                      <button
                        key={item.id}
                        type="button"
                        data-cursor="expand"
                        onClick={() => setActive(open ? null : item.id)}
                        aria-pressed={open}
                        className={cn(
                          "bg-black px-5 py-5 text-left transition-colors duration-500",
                          open
                            ? "text-foreground"
                            : "text-muted hover:text-foreground",
                        )}
                      >
                        <span className="text-[12px] tracking-[0.16em] uppercase">
                          {item.title}
                        </span>
                      </button>
                    );
                  })}
                </div>
                <AnimatePresence mode="wait">
                  {selected ? (
                    <motion.p
                      key={selected.id}
                      initial={{ opacity: 0, y: 8 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -6 }}
                      transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
                      className="mt-6 max-w-[34rem] text-[15px] leading-relaxed text-muted"
                    >
                      {selected.body}
                    </motion.p>
                  ) : null}
                </AnimatePresence>
              </div>

              <Connector />

              <DiagramRow label="03" title="Language Intelligence" muted />

              <Connector />

              <DiagramRow label="04" title="Foundation Models" muted />

              <Connector />

              <DiagramRow label="05" title="Business Execution" emphasis />
            </div>
          </Reveal>
        </div>
      </div>
    </section>
  );
}

function DiagramRow({
  label,
  title,
  body,
  muted,
  emphasis,
}: {
  label: string;
  title: string;
  body?: string;
  muted?: boolean;
  emphasis?: boolean;
}) {
  return (
    <div
      className={cn(
        "flex flex-col gap-3 px-6 py-8 md:flex-row md:items-baseline md:gap-10 md:px-10",
        emphasis && "bg-foreground/[0.03]",
      )}
    >
      <span className="label shrink-0">{label}</span>
      <div>
        <h3
          className={cn(
            "tracking-tight",
            emphasis ? "text-3xl text-foreground md:text-4xl" : "text-2xl",
            muted && "text-muted",
          )}
        >
          {title}
        </h3>
        {body ? (
          <p className="mt-3 text-[14px] tracking-[0.04em] text-muted">{body}</p>
        ) : null}
      </div>
    </div>
  );
}

function Connector() {
  return (
    <div className="flex justify-center border-t border-border py-3" aria-hidden>
      <motion.span
        className="text-[11px] tracking-[0.28em] text-muted"
        animate={{ opacity: [0.35, 1, 0.35] }}
        transition={{ duration: 2.4, repeat: Infinity, ease: "easeInOut" }}
      >
        ↓
      </motion.span>
    </div>
  );
}
