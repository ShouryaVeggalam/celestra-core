import { cn } from "@/lib/utils";

type PageHeroProps = {
  kicker?: string;
  title: string;
  dek?: string;
  className?: string;
};

export function PageHero({ kicker, title, dek, className }: PageHeroProps) {
  return (
    <header className={cn("grid-page pt-32 pb-20 md:pt-44 md:pb-28", className)}>
      {kicker ? <p className="label mb-8">{kicker}</p> : null}
      <h1 className="display max-w-[18ch] text-foreground">{title}</h1>
      {dek ? (
        <p className="editorial mt-10 max-w-[38rem] text-balance">{dek}</p>
      ) : null}
    </header>
  );
}
