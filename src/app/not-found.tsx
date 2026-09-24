import Link from "next/link";
import { Magnetic } from "@/components/chrome/Magnetic";
import { Button } from "@/components/ui/button";

export default function NotFound() {
  return (
    <div className="grid-page flex min-h-[100svh] flex-col justify-center py-32">
      <p className="label">404</p>
      <h1 className="display mt-8 max-w-[12ch]">This room does not exist.</h1>
      <p className="editorial mt-8 max-w-md">
        The stack is finite. Return to the headquarters.
      </p>
      <div className="mt-12">
        <Magnetic>
          <Button asChild>
            <Link href="/">Celestra</Link>
          </Button>
        </Magnetic>
      </div>
    </div>
  );
}
