import type { Metadata } from "next";
import Link from "next/link";
import { DemoForm } from "@/components/book-demo/demo-form";
import { Magnetic } from "@/components/chrome/Magnetic";
import { Reveal } from "@/components/chrome/Reveal";
import { Button } from "@/components/ui/button";
import { briefingTopics } from "@/lib/book-demo";

export const metadata: Metadata = {
  title: "Book Enterprise Demo",
  description:
    "A private product briefing for enterprise teams exploring AI, intelligence infrastructure, robotics, and decision systems.",
};

export default function BookDemoPage() {
  return (
    <div className="bg-black pb-8">
      <header className="grid-page pt-32 pb-20 md:pt-44 md:pb-28">
        <p className="label mb-8">Enterprise</p>
        <h1 className="display max-w-[14ch] text-foreground">
          Book an Enterprise Demo
        </h1>
        <p className="editorial mt-10 max-w-[38rem] text-balance">
          A private product briefing for enterprise teams exploring AI,
          intelligence infrastructure, robotics, and decision systems.
        </p>
        <div className="mt-12 flex flex-col gap-4 sm:flex-row sm:items-center">
          <Magnetic>
            <Button asChild>
              <a href="#schedule">Schedule Demo</a>
            </Button>
          </Magnetic>
          <Magnetic>
            <Button asChild variant="ghost">
              <Link href="/ventures">Explore Products</Link>
            </Button>
          </Magnetic>
        </div>
      </header>

      <section className="border-t border-border py-28 md:py-36">
        <div className="grid-page">
          <Reveal>
            <p className="label">02 — Briefing</p>
            <h2 className="display-md mt-8 max-w-[12ch]">What you&apos;ll see</h2>
          </Reveal>

          <div className="mt-20 grid gap-px bg-border md:grid-cols-2">
            {briefingTopics.map((topic, index) => (
              <Reveal key={topic.title} delay={index * 0.05}>
                <article className="h-full bg-black p-10 md:p-14">
                  <p className="label">{topic.index}</p>
                  <h3 className="mt-8 text-2xl tracking-tight md:text-3xl">
                    {topic.title}
                  </h3>
                  <ul className="mt-8 space-y-3">
                    {topic.items.map((item) => (
                      <li
                        key={item}
                        className="flex gap-4 text-[15px] leading-relaxed text-muted"
                      >
                        <span className="mt-3 h-px w-5 shrink-0 bg-border" />
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </article>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      <DemoForm />
    </div>
  );
}
