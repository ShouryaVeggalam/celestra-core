import type { Metadata } from "next";
import { PageHero } from "@/components/chrome/PageHero";
import { CinematicTimeline } from "@/components/timeline/CinematicTimeline";

export const metadata: Metadata = {
  title: "Timeline",
  description:
    "From foundation in 2026 to an intelligence civilization in 2050.",
};

export default function TimelinePage() {
  return (
    <div className="bg-black">
      <PageHero
        kicker="Timeline"
        title="A century, drawn in decades."
        dek="Not a product roadmap. A sequence of architectural obligations — from foundation to a civilization that can assume intelligence."
        className="pb-12 md:pb-16"
      />
      <CinematicTimeline />
    </div>
  );
}
