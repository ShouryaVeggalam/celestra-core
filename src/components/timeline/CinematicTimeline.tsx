"use client";

import { useRef } from "react";
import { useGSAP } from "@gsap/react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { CountUp } from "@/components/chrome/CountUp";
import { timeline } from "@/lib/timeline";

gsap.registerPlugin(ScrollTrigger, useGSAP);

export function CinematicTimeline() {
  const root = useRef<HTMLDivElement>(null);

  useGSAP(
    () => {
      const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      const desktop = window.matchMedia("(min-width: 768px)").matches;
      if (reduced || !desktop || !root.current) return;

      const track = root.current.querySelector<HTMLElement>("[data-track]");
      const pin = root.current.querySelector<HTMLElement>("[data-pin]");
      if (!track || !pin) return;

      const distance = () => track.scrollWidth - window.innerWidth;

      const tween = gsap.to(track, {
        x: () => -distance(),
        ease: "none",
        scrollTrigger: {
          trigger: pin,
          start: "top top",
          end: () => `+=${distance()}`,
          pin: true,
          scrub: 0.65,
          anticipatePin: 1,
          invalidateOnRefresh: true,
        },
      });

      return () => {
        tween.scrollTrigger?.kill();
        tween.kill();
      };
    },
    { scope: root },
  );

  return (
    <div ref={root} className="bg-black">
      <div data-pin className="relative overflow-hidden">
        <div
          data-track
          className="flex flex-col md:h-screen md:w-max md:flex-row md:flex-nowrap"
        >
          {timeline.map((event, index) => (
            <section
              key={event.year}
              className="relative flex min-h-[80vh] w-screen shrink-0 flex-col justify-end border-b border-border px-6 py-16 md:h-screen md:border-b-0 md:border-r md:px-20 md:py-24"
            >
              <p className="label">
                {String(index + 1).padStart(2, "0")} / {String(timeline.length).padStart(2, "0")}
              </p>
              <p className="mt-10 font-sans text-[18vw] leading-none tracking-[-0.06em] text-foreground md:text-[9vw]">
                <CountUp value={event.year} />
              </p>
              <h2 className="mt-6 max-w-[12ch] text-4xl tracking-tight md:text-6xl">
                {event.title}
              </h2>
              <p className="label mt-8 text-foreground">{event.kicker}</p>
              <p className="editorial mt-6 max-w-[32rem]">{event.body}</p>
              {index < timeline.length - 1 ? (
                <span className="label pointer-events-none absolute right-8 bottom-10 hidden md:block">
                  Continue →
                </span>
              ) : null}
            </section>
          ))}
        </div>
      </div>
    </div>
  );
}
