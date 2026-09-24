import Link from "next/link";
import { notFound } from "next/navigation";
import { getArticle } from "@/lib/research";
import { getRelatedVentures, getVenture } from "@/lib/ventures";
import { Reveal } from "@/components/chrome/Reveal";
import { LanguageOrchestration } from "@/components/ventures/LanguageOrchestration";
import { OsOrchestration } from "@/components/ventures/OsOrchestration";
import { VentureVisual } from "@/components/ventures/VentureVisual";

export function VentureArticle({ slug }: { slug: string }) {
  const venture = getVenture(slug);
  if (!venture) notFound();

  const related = getRelatedVentures(venture.slug);
  const missionTitle = venture.missionTitle ?? "Why this layer exists.";
  const architectureKicker = venture.architectureKicker ?? "Architecture";
  const architectureTitle = venture.architectureTitle ?? "The system.";
  const hasOrchestration = Boolean(venture.orchestration);

  return (
    <article className="bg-black">
      <header className="relative min-h-[88svh] overflow-hidden bg-black">
        <VentureVisual
          slug={venture.slug}
          animated={false}
          className="absolute inset-0 h-full w-full opacity-40 [&_svg]:h-full [&_svg]:w-full [&_svg]:object-cover"
        />
        <div className="relative grid-page flex min-h-[88svh] flex-col justify-end pb-20 pt-36">
          <p className="label text-muted">{venture.category}</p>
          {venture.productName ? (
            <p className="mt-4 text-[12px] tracking-[0.2em] text-muted uppercase">
              {venture.productName}
            </p>
          ) : null}
          <h1 className="display mt-6 max-w-[14ch] text-foreground">
            {venture.title}
          </h1>
          <p className="editorial mt-8 max-w-[34rem]">{venture.dek}</p>
        </div>
      </header>

      <Section kicker="Mission" title={missionTitle}>
        <p className="editorial max-w-[38rem]">{venture.mission}</p>
      </Section>

      {!hasOrchestration ? (
        <>
          <Section kicker="Problem" title="What is unfinished.">
            <p className="editorial max-w-[38rem]">{venture.problem}</p>
          </Section>

          <Section kicker="Vision" title={venture.shortVision}>
            <p className="editorial max-w-[38rem]">{venture.vision}</p>
          </Section>
        </>
      ) : null}

      <section className="border-t border-border py-28 md:py-36">
        <div className="grid-page grid gap-16 lg:grid-cols-12">
          <div className="lg:col-span-4">
            <Reveal>
              <p className="label">{architectureKicker}</p>
              <h2 className="display-md mt-8 max-w-[12ch]">{architectureTitle}</h2>
            </Reveal>
          </div>
          <div className="lg:col-span-8">
            <ol className="divide-y divide-border border-y border-border">
              {venture.architecture.map((item, index) => (
                <li
                  key={item.title}
                  className="grid gap-6 py-10 md:grid-cols-[80px_1fr]"
                >
                  <span className="label mt-1">
                    {String(index + 1).padStart(2, "0")}
                  </span>
                  <div>
                    <h3 className="text-2xl tracking-tight text-foreground">
                      {item.title}
                    </h3>
                    <p className="mt-4 max-w-[36rem] text-[16px] leading-relaxed text-muted">
                      {item.body}
                    </p>
                  </div>
                </li>
              ))}
            </ol>
          </div>
        </div>
      </section>

      {venture.orchestration === "language" ? <LanguageOrchestration /> : null}
      {venture.orchestration === "os" ? <OsOrchestration /> : null}

      {venture.useCases?.length ? (
        <section className="border-t border-border py-28 md:py-36">
          <div className="grid-page">
            <Reveal>
              <p className="label">Use Cases</p>
              <h2 className="display-md mt-8 max-w-[12ch]">Where it lands.</h2>
            </Reveal>
            <div className="mt-20 divide-y divide-border border-y border-border">
              {venture.useCases.map((useCase, index) => (
                <Reveal key={useCase.title} delay={index * 0.05}>
                  <div className="grid gap-6 py-12 md:grid-cols-12 md:items-baseline">
                    <span className="label md:col-span-2">
                      {String(index + 1).padStart(2, "0")}
                    </span>
                    <h3 className="text-2xl tracking-tight md:col-span-3 md:text-3xl">
                      {useCase.title}
                    </h3>
                    <p className="editorial md:col-span-7">{useCase.body}</p>
                  </div>
                </Reveal>
              ))}
            </div>
          </div>
        </section>
      ) : null}

      {hasOrchestration ? (
        <Section kicker="Vision" title={venture.shortVision}>
          <p className="editorial max-w-[38rem]">{venture.vision}</p>
        </Section>
      ) : null}

      <Section kicker="Future" title="What this becomes.">
        <p className="editorial max-w-[38rem]">{venture.future}</p>
      </Section>

      <section className="border-t border-border py-28 md:py-36">
        <div className="grid-page">
          <p className="label">Related Research</p>
          <div className="mt-12 divide-y divide-border border-y border-border">
            {venture.relatedResearch.map((researchSlug) => {
              const article = getArticle(researchSlug);
              if (!article) return null;
              return (
                <Link
                  key={article.slug}
                  href={`/research/${article.slug}`}
                  data-cursor="expand"
                  className="flex flex-col gap-3 py-8 transition-opacity hover:opacity-70 md:flex-row md:items-baseline md:justify-between"
                >
                  <span className="label">{article.category}</span>
                  <span className="text-2xl tracking-tight md:text-right">
                    {article.title}
                  </span>
                </Link>
              );
            })}
          </div>

          <p className="label mt-24">Adjacent layers</p>
          <div className="mt-12 grid gap-px bg-border md:grid-cols-3">
            {related.map((item) => (
              <Link
                key={item.slug}
                href={`/ventures/${item.slug}`}
                data-cursor="expand"
                className="bg-black p-8 transition-colors hover:bg-surface"
              >
                <p className="label">{item.category}</p>
                <h3 className="mt-6 text-2xl tracking-tight">{item.title}</h3>
                <p className="mt-4 text-[15px] leading-relaxed text-muted">
                  {item.shortVision}
                </p>
              </Link>
            ))}
          </div>
        </div>
      </section>
    </article>
  );
}

function Section({
  kicker,
  title,
  children,
}: {
  kicker: string;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section className="border-t border-border py-28 md:py-36">
      <div className="grid-page grid gap-12 lg:grid-cols-12">
        <div className="lg:col-span-4">
          <Reveal>
            <p className="label">{kicker}</p>
          </Reveal>
        </div>
        <div className="lg:col-span-8">
          <Reveal>
            <h2 className="display-md max-w-[14ch]">{title}</h2>
            <div className="mt-10">{children}</div>
          </Reveal>
        </div>
      </div>
    </section>
  );
}
