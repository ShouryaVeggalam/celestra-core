import type { Metadata } from "next";
import { BookDemoCta } from "@/components/book-demo/book-demo-cta";
import { PageHero } from "@/components/chrome/PageHero";
import { Reveal } from "@/components/chrome/Reveal";
import { VentureCard } from "@/components/ventures/VentureCard";
import { ventures } from "@/lib/ventures";

export const metadata: Metadata = {
  title: "Ventures",
  description:
    "The rooms of the Intelligence Stack — from AI Agents to Quantum Computing.",
};

export default function VenturesPage() {
  return (
    <div className="bg-black pb-24">
      <PageHero
        kicker="Ventures"
        title="The rooms of the stack."
        dek="Each venture is a layer, not a sideline. Together they are Celestra."
      />
      <div className="grid-page border-b border-border">
        {ventures.map((venture) => (
          <VentureCard key={venture.slug} venture={venture} />
        ))}
      </div>
      <section className="grid-page border-t border-border py-20 md:py-28">
        <Reveal>
          <div className="flex flex-col gap-8 md:flex-row md:items-end md:justify-between">
            <div>
              <p className="label">Enterprise</p>
              <h2 className="mt-6 max-w-[14ch] text-3xl tracking-tight md:text-5xl">
                See the stack in a private briefing.
              </h2>
            </div>
            <BookDemoCta label="Book Demo" />
          </div>
        </Reveal>
      </section>
    </div>
  );
}
