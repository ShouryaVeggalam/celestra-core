import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { VentureArticle } from "@/components/ventures/VentureArticle";
import { getVenture, ventures } from "@/lib/ventures";

export function generateStaticParams() {
  return ventures.map((venture) => ({ slug: venture.slug }));
}

export const dynamicParams = false;

export async function generateMetadata({
  params,
}: PageProps<"/ventures/[slug]">): Promise<Metadata> {
  const { slug } = await params;
  const venture = getVenture(slug);
  if (!venture) return { title: "Venture" };
  return {
    title: venture.title,
    description: venture.dek,
    openGraph: {
      title: `${venture.title} — Celestra`,
      description: venture.dek,
      url: `https://getcelestra.tech/ventures/${venture.slug}`,
      type: "article",
    },
    twitter: {
      card: "summary_large_image",
      title: `${venture.title} — Celestra`,
      description: venture.dek,
    },
    alternates: {
      canonical: `https://getcelestra.tech/ventures/${venture.slug}`,
    },
  };
}

export default async function VenturePage({
  params,
}: PageProps<"/ventures/[slug]">) {
  const { slug } = await params;
  if (!getVenture(slug)) notFound();
  return <VentureArticle slug={slug} />;
}
