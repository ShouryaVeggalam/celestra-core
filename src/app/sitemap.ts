import type { MetadataRoute } from "next";
import { research } from "@/lib/research";
import { site } from "@/lib/site";
import { ventures } from "@/lib/ventures";

export default function sitemap(): MetadataRoute.Sitemap {
  const now = new Date();
  const staticRoutes = [
    "",
    "/vision",
    "/intelligence-stack",
    "/ventures",
    "/research",
    "/timeline",
    "/book-demo",
    "/contact",
  ].map((path) => ({
    url: `${site.url}${path}`,
    lastModified: now,
    changeFrequency: "monthly" as const,
    priority: path === "" ? 1 : 0.8,
  }));

  const ventureRoutes = ventures.map((venture) => ({
    url: `${site.url}/ventures/${venture.slug}`,
    lastModified: now,
    changeFrequency: "monthly" as const,
    priority: 0.7,
  }));

  const researchRoutes = research.map((article) => ({
    url: `${site.url}/research/${article.slug}`,
    lastModified: new Date(article.date),
    changeFrequency: "yearly" as const,
    priority: 0.6,
  }));

  return [...staticRoutes, ...ventureRoutes, ...researchRoutes];
}
