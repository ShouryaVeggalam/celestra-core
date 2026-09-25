"use client";

import Link from "next/link";
import { Magnetic } from "@/components/chrome/Magnetic";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

type BookDemoCtaProps = {
  className?: string;
  variant?: "outline" | "ghost" | "underline";
  size?: "default" | "lg" | "sm";
  label?: string;
};

export function BookDemoCta({
  className,
  variant = "outline",
  size = "default",
  label = "Book Demo",
}: BookDemoCtaProps) {
  return (
    <Magnetic className={cn(className)}>
      <Button asChild variant={variant} size={size}>
        <Link href="/book-demo">{label}</Link>
      </Button>
    </Magnetic>
  );
}
