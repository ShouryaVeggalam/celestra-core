"use client";

import { useEffect, useState } from "react";

export function ReadingProgress() {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const onScroll = () => {
      const article = document.querySelector<HTMLElement>("[data-article]");
      if (!article) return;
      const rect = article.getBoundingClientRect();
      const start = window.scrollY + rect.top - 80;
      const height = article.offsetHeight - window.innerHeight * 0.45;
      const value = (window.scrollY - start) / height;
      setProgress(Math.min(1, Math.max(0, value)));
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);
    return () => {
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onScroll);
    };
  }, []);

  return (
    <div className="fixed top-16 right-0 left-0 z-[68] h-px bg-transparent md:top-20">
      <div
        className="h-px bg-foreground origin-left"
        style={{ transform: `scaleX(${progress})` }}
      />
    </div>
  );
}
