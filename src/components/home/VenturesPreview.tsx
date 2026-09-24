import Link from "next/link";
import { ventures } from "@/lib/ventures";
import { Reveal } from "@/components/chrome/Reveal";
import { Magnetic } from "@/components/chrome/Magnetic";
import { Button } from "@/components/ui/button";
import { VentureCard } from "@/components/ventures/VentureCard";

export function VenturesPreview() {
  return (
    <section className="bg-black pb-32 md:pb-40">
      <div className="grid-page">
        <Reveal>
          <div className="mb-16 flex flex-col gap-8 md:mb-24 md:flex-row md:items-end md:justify-between">
            <div>
              <p className="label">04 — Ventures</p>
              <h2 className="display-md mt-8 max-w-[12ch] text-foreground">
                One vision, many rooms.
              </h2>
            </div>
            <Magnetic>
              <Button asChild variant="outline">
                <Link href="/ventures">All ventures</Link>
              </Button>
            </Magnetic>
          </div>
        </Reveal>
        <div className="border-b border-border">
          {ventures.map((venture) => (
            <VentureCard key={venture.slug} venture={venture} />
          ))}
        </div>
      </div>
    </section>
  );
}
