import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import { ArticleBody } from "@/components/research/ArticleBody";
import { ReadingProgress } from "@/components/research/ReadingProgress";
import {
  articleText,
  getArticle,
  getRelatedArticles,
  research,
} from "@/lib/research";
import { getVenture } from "@/lib/ventures";
import { readingTime } from "@/lib/utils";

export function generateStaticParams() {
  return research.map((article) => ({ slug: article.slug }));
}

export const dynamicParams = false;

export async function generateMetadata({
  params,
}: PageProps<"/research/[slug]">): Promise<Metadata> {
  const { slug } = await params;
  const article = getArticle(slug);
  if (!article) return { title: "Research" };
  return {
    title: article.title,
    description: article.dek,
  };
}

export default async function ResearchArticlePage({
  params,
}: PageProps<"/research/[slug]">) {
  const { slug } = await params;
  const article = getArticle(slug);
  if (!article) notFound();

  const minutes = readingTime(articleText(article));
  const related = getRelatedArticles(article.slug);

  return (
    <div className="bg-black">
      <ReadingProgress />
      <article data-article className="pb-32">
        <header className="grid-page pt-36 pb-16 md:pt-44 md:pb-24">
          <p className="label">{article.category}</p>
          <h1 className="display mt-8 max-w-[16ch]">{article.title}</h1>
          <p className="editorial mt-8 max-w-[36rem]">{article.dek}</p>
          <div className="mt-12 flex flex-wrap gap-8 text-[12px] tracking-[0.16em] text-muted uppercase">
            <span>{article.author}</span>
            <span>{article.date}</span>
            <span>{minutes} minute read</span>
          </div>
        </header>

        <div className="mx-auto w-[min(680px,calc(100%-3rem))] md:w-[min(680px,calc(100%-8rem))]">
          <ArticleBody article={article} />
        </div>

        {article.relatedVentures.length ? (
          <aside className="grid-page mt-28 border-t border-border pt-16">
            <p className="label mb-8">Related ventures</p>
            <div className="flex flex-wrap gap-3">
              {article.relatedVentures.map((ventureSlug) => {
                const venture = getVenture(ventureSlug);
                if (!venture) return null;
                return (
                  <Link
                    key={venture.slug}
                    href={`/ventures/${venture.slug}`}
                    data-cursor="expand"
                    className="border border-border px-4 py-3 text-[12px] tracking-[0.16em] uppercase text-muted transition-colors hover:border-foreground hover:text-foreground"
                  >
                    {venture.title}
                  </Link>
                );
              })}
            </div>
          </aside>
        ) : null}

        <aside className="grid-page mt-20">
          <p className="label mb-8">Continue</p>
          <div className="divide-y divide-border border-y border-border">
            {related.map((item) => (
              <Link
                key={item.slug}
                href={`/research/${item.slug}`}
                data-cursor="expand"
                className="flex flex-col gap-2 py-8 md:flex-row md:items-baseline md:justify-between"
              >
                <span className="label">{item.category}</span>
                <span className="text-2xl tracking-tight">{item.title}</span>
              </Link>
            ))}
          </div>
        </aside>
      </article>
    </div>
  );
}
