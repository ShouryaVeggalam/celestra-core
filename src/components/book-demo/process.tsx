"use client";

import { Reveal } from "@/components/chrome/Reveal";
import { processSteps } from "@/lib/book-demo";

export function Process() {
  return (
    <section className="border-t border-border py-28 md:py-36">
      <div className="grid-page">
        <Reveal>
          <p className="label">05 — Next</p>
          <h2 className="display-md mt-8 max-w-[12ch]">What happens next</h2>
        </Reveal>

        <ol className="mt-20 divide-y divide-border border-y border-border">
          {processSteps.map((step, index) => (
            <li key={step.index}>
              <Reveal delay={index * 0.06}>
                <div className="grid gap-6 py-12 md:grid-cols-12 md:items-baseline">
                  <span className="label md:col-span-2">{step.index}</span>
                  <h3 className="text-3xl tracking-tight md:col-span-3">
                    {step.title}
                  </h3>
                  <p className="editorial md:col-span-7">{step.body}</p>
                </div>
              </Reveal>
            </li>
          ))}
        </ol>
      </div>
    </section>
  );
}
