import { Reveal } from "@/components/chrome/Reveal";

export function Editorial() {
  return (
    <section className="relative bg-black py-32 md:py-44">
      <div className="grid-page grid gap-16 lg:grid-cols-12 lg:gap-8">
        <div className="lg:col-span-4">
          <Reveal>
            <p className="label">02 — Statement</p>
          </Reveal>
        </div>
        <div className="lg:col-span-8">
          <Reveal>
            <h2 className="display-md max-w-[12ch] text-foreground">
              The future is being rebuilt.
            </h2>
          </Reveal>
          <Reveal delay={0.12}>
            <p className="editorial mt-12 max-w-[34rem]">
              Intelligence will not remain a feature inside software. It will
              become the substrate of institutions, markets, machines, and
              scientific discovery. Celestra exists to design that substrate as
              a coherent stack — from the physical world to the applications
              that run on it.
            </p>
          </Reveal>
          <Reveal delay={0.2}>
            <p className="editorial mt-8 max-w-[34rem]">
              We do not ship products in isolation. We build layers. Each layer
              makes the next one possible. Together they form a single system:
              the Intelligence Stack.
            </p>
          </Reveal>
        </div>
      </div>
    </section>
  );
}
