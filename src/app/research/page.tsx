import type { Metadata } from "next";
import Link from "next/link";
import { BookDemoCta } from "@/components/book-demo/book-demo-cta";
import { PageHero } from "@/components/chrome/PageHero";
import { Reveal } from "@/components/chrome/Reveal";
import { articleText, research, researchCategories } from "@/lib/research";
import { readingTime } from "@/lib/utils";

export const metadata: Metadata = {
  title: "Research",
  description:
    "Whitepapers, future briefings, founder essays, and research papers from Celestra.",
};

export default function ResearchPage() {
  return (
    <div className="bg-black pb-32">
      <PageHero
        kicker="Research"
        title="Essays from the institute."
        dek="The Intelligence Stack is specified in public. Read slowly."
      />

      <div className="grid-page space-y-28">
        {researchCategories.map((category) => {
          const items = research.filter((article) => article.category === category);
          return (
            <section key={category}>
              <p className="label mb-10">{category}</p>
              <div className="divide-y divide-border border-y border-border">
                {items.map((article) => (
                  <Link
                    key={article.slug}
                    href={`/research/${article.slug}`}
                    data-cursor="expand"
                    className="group grid gap-4 py-10 md:grid-cols-12 md:items-baseline"
                  >
                    <span className="label md:col-span-2">
                      {article.date.slice(0, 4)}
                    </span>
                    <span className="text-3xl tracking-tight md:col-span-7 md:text-4xl">
                      {article.title}
                    </span>
                    <span className="text-[13px] tracking-[0.12em] text-muted uppercase md:col-span-3 md:text-right">
                      {readingTime(articleText(article))} min
                    </span>
                    <p className="editorial md:col-span-7 md:col-start-3">
                      {article.dek}
                    </p>
                  </Link>
                ))}
              </div>
            </section>
          );
        })}

        <Reveal>
          <section className="border-t border-border pt-20">
            <div className="flex flex-col gap-8 md:flex-row md:items-end md:justify-between">
              <div>
                <p className="label">Enterprise</p>
                <h2 className="mt-6 max-w-[16ch] text-3xl tracking-tight md:text-5xl">
                  Move from the essay to the briefing.
                </h2>
              </div>
              <BookDemoCta label="Book Demo" />
            </div>
          </section>
        </Reveal>
      </div>
    </div>
  );
}
