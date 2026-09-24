import type { Metadata } from "next";
import { PageHero } from "@/components/chrome/PageHero";
import { Reveal } from "@/components/chrome/Reveal";

export const metadata: Metadata = {
  title: "Vision",
  description:
    "Celestra is building one system: the Intelligence Stack. From applications to the physical world.",
};

export default function VisionPage() {
  return (
    <div className="bg-black">
      <PageHero
        kicker="Vision"
        title="One stack. One company. One horizon."
        dek="Celestra is not a collection of businesses. It is an architecture for the next generation of intelligence — designed as layers that make each other possible."
      />

      <section className="border-t border-border py-28 md:py-36">
        <div className="grid-page grid gap-16 lg:grid-cols-12">
          <div className="lg:col-span-4">
            <Reveal>
              <p className="label">The claim</p>
            </Reveal>
          </div>
          <div className="lg:col-span-7">
            <Reveal>
              <p className="text-2xl leading-snug tracking-tight text-foreground md:text-3xl">
                Intelligence will become infrastructure. Infrastructure requires
                an architect. We are building the systems that power that
                infrastructure — from agents that can finish work, to machines
                that can inhabit physics, to the compute on which thought
                actually runs.
              </p>
            </Reveal>
          </div>
        </div>
      </section>

      <section className="border-t border-border py-28 md:py-36">
        <div className="grid-page grid gap-16 lg:grid-cols-12">
          <div className="lg:col-span-4">
            <Reveal>
              <p className="label">Mission</p>
            </Reveal>
          </div>
          <div className="lg:col-span-7 space-y-8">
            <Reveal>
              <p className="editorial">
                Create the systems that power the next generation of
                intelligence. Not a slogan for a launch. A sentence that has to
                survive 2026 and 2050 in the same mouth.
              </p>
            </Reveal>
            <Reveal delay={0.08}>
              <p className="editorial">
                The next generation will not live inside a single product. It
                will live in hospitals that never lose the thread of a life, in
                markets that can see themselves, in robots that can be employed,
                in models that can be inspected, and in machines whose physics
                we still understand.
              </p>
            </Reveal>
          </div>
        </div>
      </section>

      <section className="border-t border-border py-28 md:py-36">
        <div className="grid-page">
          <Reveal>
            <p className="label">The rooms of the stack</p>
            <h2 className="display-md mt-8 max-w-[14ch]">
              Many rooms. Not many companies.
            </h2>
          </Reveal>
          <div className="mt-20 grid gap-px bg-border md:grid-cols-2">
            {[
              {
                title: "Applications",
                body: "Health, fintech, and motorsport — intelligence that acts inside institutions and at the limit.",
              },
              {
                title: "Intelligence",
                body: "Celestra OS, agents, language intelligence, and AGI research — the cognitive and execution core of the stack.",
              },
              {
                title: "Compute",
                body: "Semiconductors and quantum methods as architecture — the substrate intelligence deserves.",
              },
              {
                title: "Physical World",
                body: "Robotics and physical AI — the laboratories where gravity still has the last word.",
              },
            ].map((room) => (
              <div key={room.title} className="bg-black p-10 md:p-14">
                <h3 className="text-2xl tracking-tight">{room.title}</h3>
                <p className="mt-5 max-w-md text-[16px] leading-relaxed text-muted">
                  {room.body}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="border-t border-border py-28 md:py-36">
        <div className="grid-page grid gap-16 lg:grid-cols-12">
          <div className="lg:col-span-4">
            <Reveal>
              <p className="label">Horizon</p>
            </Reveal>
          </div>
          <div className="lg:col-span-7">
            <Reveal>
              <p className="editorial">
                2050 is not a deliverable. It is a standard. If intelligence
                becomes a public assumption — the way electricity is a public
                assumption — then the architecture we pour now must be able to
                bear that weight. That is the vision. Everything else is a
                layer.
              </p>
            </Reveal>
          </div>
        </div>
      </section>
    </div>
  );
}
