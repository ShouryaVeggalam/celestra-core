"use client";

import Link from "next/link";
import { ArrowUpRight } from "lucide-react";
import type { Venture } from "@/lib/ventures";
import { VentureVisual } from "@/components/ventures/VentureVisual";

export function VentureCard({ venture }: { venture: Venture }) {
  return (
    <Link
      href={`/ventures/${venture.slug}`}
      data-cursor="expand"
      className="group relative block overflow-hidden border-t border-border py-10 md:py-14"
    >
      <div className="pointer-events-none absolute inset-0 bg-black/0 backdrop-blur-0 transition-[background-color,backdrop-filter] duration-700 group-hover:bg-black/20 group-hover:backdrop-blur-[1px]" />
      <div className="relative grid items-center gap-10 lg:grid-cols-12">
        <div className="lg:col-span-6">
          <p className="label">{venture.category}</p>
          <h3 className="mt-5 text-4xl tracking-tight text-foreground md:text-6xl">
            {venture.title}
          </h3>
          <p className="mt-6 max-w-md text-[17px] leading-relaxed text-muted">
            {venture.shortVision}
          </p>
          <span className="mt-8 inline-flex items-center gap-2 text-[11px] tracking-[0.18em] text-muted uppercase transition-colors duration-500 group-hover:text-foreground">
            Open
            <ArrowUpRight className="h-3.5 w-3.5" strokeWidth={1.25} />
          </span>
        </div>
        <div className="overflow-hidden lg:col-span-6">
          <VentureVisual slug={venture.slug} className="aspect-[16/10] w-full" />
        </div>
      </div>
    </Link>
  );
}
