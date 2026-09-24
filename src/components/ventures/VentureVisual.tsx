import { cn } from "@/lib/utils";

type VentureVisualProps = {
  slug: string;
  className?: string;
  animated?: boolean;
};

export function VentureVisual({ slug, className, animated = true }: VentureVisualProps) {
  return (
    <div
      className={cn(
        "relative overflow-hidden bg-surface",
        animated && "transition-transform duration-700 ease-[cubic-bezier(0.22,1,0.36,1)] group-hover:scale-[1.04]",
        className,
      )}
    >
      <svg
        viewBox="0 0 640 400"
        className="h-full w-full"
        aria-hidden
        fill="none"
      >
        <rect width="640" height="400" fill="#0A0A0A" />
        <Drawing slug={slug} />
      </svg>
    </div>
  );
}

function Drawing({ slug }: { slug: string }) {
  switch (slug) {
    case "ai-agents":
      return (
        <g stroke="#d4d4d8" strokeWidth="0.8">
          <circle cx="320" cy="200" r="28" />
          <circle cx="180" cy="110" r="16" />
          <circle cx="470" cy="120" r="16" />
          <circle cx="150" cy="280" r="16" />
          <circle cx="500" cy="270" r="16" />
          <circle cx="320" cy="70" r="12" />
          <circle cx="320" cy="330" r="12" />
          <path d="M294 190 L196 122 M346 190 L454 132 M300 220 L166 268 M340 220 L484 258 M320 172 V82 M320 228 V318" />
        </g>
      );
    case "health-intelligence":
      return (
        <g stroke="#d4d4d8" strokeWidth="0.8">
          <ellipse cx="320" cy="200" rx="180" ry="120" />
          <ellipse cx="320" cy="200" rx="120" ry="78" />
          <ellipse cx="320" cy="200" rx="60" ry="38" />
          <circle cx="320" cy="200" r="6" fill="#d4d4d8" stroke="none" />
          <path d="M320 80 V40 M320 320 V360 M140 200 H90 M500 200 H550" />
        </g>
      );
    case "financial-intelligence":
      return (
        <g stroke="#d4d4d8" strokeWidth="0.8">
          {Array.from({ length: 9 }).map((_, i) => (
            <path key={i} d={`M80 ${60 + i * 32} H560`} opacity={0.35 + (i % 3) * 0.15} />
          ))}
          <rect x="180" y="92" width="90" height="216" />
          <rect x="300" y="140" width="90" height="168" />
          <rect x="420" y="76" width="90" height="232" />
        </g>
      );
    case "ai-operating-system":
      return (
        <g stroke="#d4d4d8" strokeWidth="0.8">
          <rect x="200" y="48" width="240" height="44" />
          <path d="M320 92 V128" />
          <rect x="160" y="128" width="320" height="72" />
          <path d="M220 200 V236 M320 200 V236 M420 200 V236" />
          <rect x="140" y="236" width="120" height="40" />
          <rect x="260" y="236" width="120" height="40" />
          <rect x="380" y="236" width="120" height="40" />
          <path d="M320 276 V312" />
          <rect x="200" y="312" width="240" height="40" />
        </g>
      );
    case "language-intelligence":
    case "llms":
      return (
        <g stroke="#d4d4d8" strokeWidth="0.7">
          {Array.from({ length: 11 }).map((_, i) => (
            <path key={`h-${i}`} d={`M70 ${50 + i * 30} H570`} opacity="0.35" />
          ))}
          {Array.from({ length: 17 }).map((_, i) => (
            <path key={`v-${i}`} d={`M${70 + i * 30} 50 V350`} opacity="0.28" />
          ))}
          <rect x="220" y="140" width="200" height="120" />
        </g>
      );
    case "robotics":
      return (
        <g stroke="#d4d4d8" strokeWidth="0.9">
          <circle cx="320" cy="92" r="22" />
          <path d="M320 114 V180 M320 180 L250 260 M320 180 L390 260 M250 260 L230 330 M250 260 L280 330 M390 260 L370 330 M390 260 L420 330 M250 188 H390" />
          <circle cx="250" cy="260" r="5" fill="#d4d4d8" stroke="none" />
          <circle cx="390" cy="260" r="5" fill="#d4d4d8" stroke="none" />
        </g>
      );
    case "physical-ai":
      return (
        <g stroke="#d4d4d8" strokeWidth="0.8">
          <circle cx="320" cy="200" r="90" />
          <circle cx="320" cy="200" r="140" opacity="0.45" />
          <path d="M320 110 V60 M410 200 H460 M320 290 V340 M230 200 H180" />
          <path d="M260 160 L320 200 L380 240" />
          <circle cx="320" cy="200" r="4" fill="#d4d4d8" stroke="none" />
        </g>
      );
    case "agi":
      return (
        <g stroke="#d4d4d8" strokeWidth="0.8">
          <rect x="170" y="70" width="300" height="260" />
          <rect x="210" y="110" width="220" height="180" />
          <rect x="250" y="150" width="140" height="100" />
          <circle cx="320" cy="200" r="10" />
        </g>
      );
    case "semiconductors":
      return (
        <g stroke="#d4d4d8" strokeWidth="0.7">
          <rect x="160" y="80" width="320" height="240" />
          {Array.from({ length: 8 }).map((_, i) => (
            <rect key={i} x={180 + (i % 4) * 72} y={100 + Math.floor(i / 4) * 100} width="56" height="80" />
          ))}
          <path d="M160 80 L130 50 H510 L480 80 M160 320 L130 350 H510 L480 320" />
        </g>
      );
    case "quantum-computing":
      return (
        <g stroke="#d4d4d8" strokeWidth="0.8">
          <ellipse cx="320" cy="200" rx="200" ry="70" />
          <ellipse cx="320" cy="200" rx="200" ry="70" transform="rotate(60 320 200)" />
          <ellipse cx="320" cy="200" rx="200" ry="70" transform="rotate(120 320 200)" />
          <circle cx="320" cy="200" r="8" fill="#d4d4d8" stroke="none" />
        </g>
      );
    case "motorsport-intelligence":
      return (
        <g stroke="#d4d4d8" strokeWidth="0.9">
          <path d="M90 260 C 180 80, 260 80, 320 200 S 470 320, 560 140" />
          <path d="M110 270 C 190 100, 270 100, 328 210 S 468 318, 548 160" opacity="0.4" />
          <circle cx="320" cy="200" r="6" fill="#d4d4d8" stroke="none" />
          <path d="M90 300 H560" opacity="0.35" />
        </g>
      );
    default:
      return <path stroke="#27272A" d="M40 360 H600" />;
  }
}
