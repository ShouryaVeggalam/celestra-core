"use client";

import { motion } from "framer-motion";
import type { DemoProductId } from "@/lib/book-demo";
import { demoProducts } from "@/lib/book-demo";
import { cn } from "@/lib/utils";

type ProductSelectorProps = {
  value: DemoProductId[];
  onChange: (next: DemoProductId[]) => void;
  error?: string;
};

export function ProductSelector({ value, onChange, error }: ProductSelectorProps) {
  function toggle(id: DemoProductId) {
    if (value.includes(id)) {
      onChange(value.filter((item) => item !== id));
      return;
    }
    onChange([...value, id]);
  }

  return (
    <div>
      <div className="grid gap-3 sm:grid-cols-2">
        {demoProducts.map((product, index) => {
          const selected = value.includes(product.id);
          return (
            <motion.button
              key={product.id}
              type="button"
              data-cursor="expand"
              onClick={() => toggle(product.id)}
              aria-pressed={selected}
              initial={{ opacity: 0, y: 12 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-8% 0px" }}
              transition={{
                duration: 0.55,
                delay: index * 0.03,
                ease: [0.22, 1, 0.36, 1],
              }}
              className={cn(
                "group flex items-center justify-between border px-5 py-5 text-left transition-[border-color,background-color,color] duration-500",
                selected
                  ? "border-foreground bg-foreground/[0.03] text-foreground"
                  : "border-border text-muted hover:border-foreground/50 hover:text-foreground",
              )}
            >
              <span className="text-[15px] tracking-tight">{product.label}</span>
              <span
                className={cn(
                  "flex h-4 w-4 items-center justify-center border transition-colors duration-500",
                  selected ? "border-foreground bg-foreground" : "border-border",
                )}
                aria-hidden
              >
                <span
                  className={cn(
                    "block h-1.5 w-1.5 bg-black transition-opacity duration-300",
                    selected ? "opacity-100" : "opacity-0",
                  )}
                />
              </span>
            </motion.button>
          );
        })}
      </div>
      {error ? <p className="mt-4 text-[13px] text-muted">{error}</p> : null}
    </div>
  );
}
