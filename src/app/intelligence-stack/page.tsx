import type { Metadata } from "next";
import { IntelligenceStack } from "@/components/home/IntelligenceStack";
import { PageHero } from "@/components/chrome/PageHero";

export const metadata: Metadata = {
  title: "Intelligence Stack",
  description:
    "The Celestra Intelligence Stack: Applications, Intelligence, Compute, and the Physical World.",
};

export default function IntelligenceStackPage() {
  return (
    <div className="bg-black">
      <PageHero
        kicker="Intelligence Stack"
        title="Four layers. One machine."
        dek="Hover a layer. The stack opens. This is the company, drawn as an architecture rather than an org chart."
      />
      <IntelligenceStack kicker="Structure" compact />
    </div>
  );
}
