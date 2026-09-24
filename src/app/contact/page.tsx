import type { Metadata } from "next";
import { Magnetic } from "@/components/chrome/Magnetic";
import { PageHero } from "@/components/chrome/PageHero";
import { site } from "@/lib/site";

export const metadata: Metadata = {
  title: "Contact",
  description: "Write to Celestra. Correspondence worldwide.",
};

export default function ContactPage() {
  return (
    <div className="bg-black">
      <PageHero
        kicker="Contact"
        title="Write."
        dek="No forms. No funnel. If the work is serious, an email is enough."
      />

      <section className="border-t border-border py-28 md:py-40">
        <div className="grid-page grid gap-20 lg:grid-cols-12">
          <div className="lg:col-span-8">
            <p className="label mb-8">Email</p>
            <Magnetic strength={0.12}>
              <a
                href={`mailto:${site.email}`}
                data-cursor="expand"
                className="display-md block max-w-full break-all text-foreground transition-opacity hover:opacity-60"
              >
                {site.email}
              </a>
            </Magnetic>
          </div>
          <div className="space-y-16 lg:col-span-4 lg:pt-16">
            <div>
              <p className="label mb-4">LinkedIn</p>
              <a
                href={site.linkedin}
                data-cursor="expand"
                target="_blank"
                rel="noreferrer"
                className="text-xl tracking-tight text-foreground transition-opacity hover:opacity-60"
              >
                Celestra
              </a>
            </div>
            <div>
              <p className="label mb-4">X</p>
              <a
                href={site.x}
                data-cursor="expand"
                target="_blank"
                rel="noreferrer"
                className="text-xl tracking-tight text-foreground transition-opacity hover:opacity-60"
              >
                @TheCelestra
              </a>
            </div>
            <div>
              <p className="label mb-4">Location</p>
              <p className="text-xl tracking-tight">{site.location}</p>
              <p className="mt-3 text-muted">{site.locationDetail}</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
