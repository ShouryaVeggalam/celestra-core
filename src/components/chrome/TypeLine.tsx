"use client";

import { useEffect, useRef, useState } from "react";

type TypeLineProps = {
  text: string;
  started?: boolean;
  cursor?: boolean;
  hideCursorWhenDone?: boolean;
  interval?: number;
  className?: string;
  onComplete?: () => void;
};

export function TypeLine({
  text,
  started = true,
  cursor = true,
  hideCursorWhenDone = false,
  interval = 36,
  className,
  onComplete,
}: TypeLineProps) {
  const [count, setCount] = useState(0);
  const [reduced, setReduced] = useState(false);
  const completed = useRef(false);
  const onCompleteRef = useRef(onComplete);
  onCompleteRef.current = onComplete;

  useEffect(() => {
    setReduced(window.matchMedia("(prefers-reduced-motion: reduce)").matches);
  }, []);

  useEffect(() => {
    if (!started) return;

    if (reduced) {
      setCount(text.length);
      if (!completed.current) {
        completed.current = true;
        onCompleteRef.current?.();
      }
      return;
    }

    if (count >= text.length) {
      if (!completed.current) {
        completed.current = true;
        onCompleteRef.current?.();
      }
      return;
    }

    const id = window.setTimeout(() => setCount((value) => value + 1), interval);
    return () => window.clearTimeout(id);
  }, [count, started, text, interval, reduced]);

  const done = count >= text.length;
  const showCursor = cursor && !(hideCursorWhenDone && done);

  return (
    <span className={className}>
      {text.slice(0, count)}
      {showCursor ? <span className="cursor-blink" aria-hidden /> : null}
    </span>
  );
}
