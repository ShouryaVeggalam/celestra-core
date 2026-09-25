"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Reveal } from "@/components/chrome/Reveal";
import { cn } from "@/lib/utils";

const core = ["Reasoning", "Memory", "Routing"] as const;
const models = ["GPT", "Claude", "Gemini", "Llama", "Qwen", "Future Models"] as const;

export function LanguageOrchestration() {
  const [active, setActive] = useState<(typeof core)[number] | null>("Reasoning");

  return (
    <section className="border-t border-border py-28 md:py-36">
      <div className="grid-page grid gap-16 lg:grid-cols-12">
        <div className="lg:col-span-4">
          <Reveal>
            <p className="label">Orchestration</p>
            <h2 className="display-md mt-8 max-w-[12ch]">
              The layer above the models.
            </h2>
            <p className="editorial mt-8 max-w-[26rem]">
              Language Intelligence is the orchestration layer. Foundation models
              are interchangeable. Celestra does not own GPT or Claude — it owns
              the system that can call them under enterprise control.
            </p>
          </Reveal>
        </div>

        <div className="lg:col-span-8">
          <Reveal delay={0.08}>
            <div className="border border-border">
              <DiagramRow label="01" title="Enterprise Applications" muted />

              <Connector />

              <DiagramRow
                label="02"
                title="Language Intelligence"
                emphasis
                body="Reasoning · Memory · Routing · Governance"
              />

              <Connector />

              <div className="border-t border-border px-6 py-8 md:px-10">
                <p className="label mb-6">Core</p>
                <div className="flex flex-wrap gap-3">
                  {core.map((item) => {
                    const open = active === item;
                    return (
                      <button
                        key={item}
                        type="button"
                        data-cursor="expand"
                        onClick={() => setActive(open ? null : item)}
                        aria-pressed={open}
                        className={cn(
                          "border px-5 py-3 text-[12px] tracking-[0.16em] uppercase transition-colors duration-500",
                          open
                            ? "border-foreground text-foreground"
                            : "border-border text-muted hover:border-foreground/50 hover:text-foreground",
                        )}
                      >
                        {item}
                      </button>
                    );
                  })}
                </div>
                <AnimatePresence mode="wait">
                  {active ? (
                    <motion.p
                      key={active}
                      initial={{ opacity: 0, y: 8 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -6 }}
                      transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
                      className="mt-6 max-w-[34rem] text-[15px] leading-relaxed text-muted"
                    >
                      {active === "Reasoning" &&
                        "Structured and unstructured understanding — the capacity to interpret institutional language without collapsing it into a chat reply."}
                      {active === "Memory" &&
                        "Persistent contextual memory across workflows, roles, and time — so systems retain what the institution has already decided."}
                      {active === "Routing" &&
                        "Select the optimal foundation model for quality, latency, and cost. Models change. The routing policy remains."}
                    </motion.p>
                  ) : null}
                </AnimatePresence>
              </div>

              <Connector />

              <div className="border-t border-border px-6 py-8 md:px-10">
                <p className="label mb-6">Foundation Models</p>
                <div className="flex flex-wrap gap-3">
                  {models.map((model) => (
                    <span
                      key={model}
                      className="border border-border px-4 py-2.5 text-[12px] tracking-[0.14em] text-muted uppercase"
                    >
                      {model}
                    </span>
                  ))}
                </div>
                <p className="mt-6 max-w-[34rem] text-[13px] leading-relaxed text-muted">
                  Interchangeable providers. Not owned by Celestra. Called through
                  Language Intelligence under policy.
                </p>
              </div>
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
            emphasis ? "text-3xl md:text-4xl text-foreground" : "text-2xl",
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
      <span className="text-[11px] tracking-[0.28em] text-muted">↓</span>
    </div>
  );
}
