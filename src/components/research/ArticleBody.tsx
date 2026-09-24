import type { ResearchArticle } from "@/lib/research";
import { cn } from "@/lib/utils";

export function ArticleBody({ article }: { article: ResearchArticle }) {
  return (
    <div className="space-y-8">
      {article.blocks.map((block, index) => {
        if (block.type === "h2") {
          return (
            <h2
              key={index}
              className="pt-8 text-3xl tracking-tight text-foreground md:text-4xl"
            >
              {block.text}
            </h2>
          );
        }
        if (block.type === "quote") {
          return (
            <blockquote
              key={index}
              className="display-md my-12 max-w-[18ch] text-foreground"
            >
              {block.text}
            </blockquote>
          );
        }
        if (block.type === "ul") {
          return (
            <ul key={index} className="space-y-3 pl-0">
              {block.items.map((item) => (
                <li
                  key={item}
                  className="flex gap-4 text-[17px] leading-[1.75] text-muted"
                >
                  <span className="mt-3 h-px w-6 shrink-0 bg-border" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          );
        }
        return (
          <p
            key={index}
            className={cn("text-[17.5px] leading-[1.8] text-[#d4d4d8] md:text-[18px]")}
          >
            {block.text}
          </p>
        );
      })}
    </div>
  );
}
