import Link from "next/link";
import { BookDemoCta } from "@/components/book-demo/book-demo-cta";
import { footerNav, site } from "@/lib/site";

export function Footer() {
  return (
    <footer className="border-t border-border bg-black">
      <div className="grid-page grid gap-16 py-16 md:grid-cols-[1.2fr_1fr] md:py-24">
        <div>
          <p className="label text-foreground">{site.name}</p>
          <p className="mt-5 max-w-sm text-lg leading-relaxed text-muted">
            {site.tagline}
          </p>
          <div className="mt-10">
            <BookDemoCta label="Book Demo" size="sm" />
          </div>
        </div>
        <nav className="flex flex-wrap content-start gap-x-10 gap-y-4 md:justify-end">
          {footerNav.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              data-cursor="expand"
              className="text-[12px] tracking-[0.16em] uppercase text-muted transition-colors hover:text-foreground"
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </div>
      <div className="grid-page flex items-center justify-between border-t border-border py-6">
        <p className="text-[11px] tracking-[0.14em] text-muted uppercase">
          © 2026 {site.legalName}. All rights reserved.
        </p>
      </div>
    </footer>
  );
}
