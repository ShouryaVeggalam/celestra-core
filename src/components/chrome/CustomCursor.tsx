"use client";

import { useEffect, useRef } from "react";
import { useCursor } from "@/components/chrome/CursorProvider";

export function CustomCursor() {
  const { mode, setMode } = useCursor();
  const dotRef = useRef<HTMLDivElement>(null);
  const ringRef = useRef<HTMLDivElement>(null);
  const enabledRef = useRef(false);

  useEffect(() => {
    const fine = window.matchMedia("(pointer: fine)").matches;
    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (!fine || reduced) return;

    enabledRef.current = true;
    document.documentElement.classList.add("has-custom-cursor");

    const mouse = { x: window.innerWidth / 2, y: window.innerHeight / 2 };
    const ring = { x: mouse.x, y: mouse.y };
    const magnet = { x: 0, y: 0, active: false };
    let raf = 0;

    const onMove = (event: MouseEvent) => {
      mouse.x = event.clientX;
      mouse.y = event.clientY;

      const target = (event.target as HTMLElement | null)?.closest<HTMLElement>(
        "[data-cursor], a, button, input, textarea, [role='button']",
      );

      if (target) {
        const cursor = target.dataset.cursor;
        if (cursor === "hidden") {
          setMode("hidden");
        } else {
          setMode("expand");
        }

        if (target.dataset.magnetic === "true") {
          const rect = target.getBoundingClientRect();
          const cx = rect.left + rect.width / 2;
          const cy = rect.top + rect.height / 2;
          magnet.x = (cx - mouse.x) * 0.28;
          magnet.y = (cy - mouse.y) * 0.28;
          magnet.active = true;
        } else {
          magnet.active = false;
        }
      } else {
        magnet.active = false;
        setMode("default");
      }
    };

    const loop = () => {
      const pullX = magnet.active ? magnet.x : 0;
      const pullY = magnet.active ? magnet.y : 0;
      ring.x += (mouse.x + pullX - ring.x) * 0.18;
      ring.y += (mouse.y + pullY - ring.y) * 0.18;

      if (dotRef.current) {
        dotRef.current.style.transform = `translate3d(${mouse.x + pullX * 0.45}px, ${mouse.y + pullY * 0.45}px, 0)`;
      }
      if (ringRef.current) {
        ringRef.current.style.transform = `translate3d(${ring.x}px, ${ring.y}px, 0)`;
      }
      raf = requestAnimationFrame(loop);
    };

    window.addEventListener("mousemove", onMove, { passive: true });
    raf = requestAnimationFrame(loop);

    return () => {
      document.documentElement.classList.remove("has-custom-cursor");
      window.removeEventListener("mousemove", onMove);
      cancelAnimationFrame(raf);
    };
  }, [setMode]);

  return (
    <div
      aria-hidden
      className="pointer-events-none fixed inset-0 z-[80] hidden md:block"
    >
      <div
        ref={dotRef}
        className="absolute top-0 left-0 h-1.5 w-1.5 rounded-full bg-white will-change-transform"
        style={{
          marginLeft: -3,
          marginTop: -3,
          opacity: mode === "hidden" ? 0 : 1,
        }}
      />
      <div
        ref={ringRef}
        className="absolute top-0 left-0 rounded-full border border-white/70 will-change-transform"
        style={{
          width: mode === "expand" ? 44 : 28,
          height: mode === "expand" ? 44 : 28,
          marginLeft: mode === "expand" ? -22 : -14,
          marginTop: mode === "expand" ? -22 : -14,
          opacity: mode === "hidden" ? 0 : mode === "expand" ? 0.9 : 0.35,
          transition:
            "width 280ms cubic-bezier(0.22,1,0.36,1), height 280ms cubic-bezier(0.22,1,0.36,1), margin 280ms cubic-bezier(0.22,1,0.36,1), opacity 280ms",
        }}
      />
    </div>
  );
}
