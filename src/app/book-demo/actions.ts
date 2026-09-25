"use server";

import { mkdir, appendFile } from "node:fs/promises";
import path from "node:path";
import {
  demoRequestSchema,
  type DemoRequestInput,
  type DemoRequestResult,
} from "@/lib/book-demo";

function createRequestId() {
  const stamp = new Date().toISOString().replace(/[-:.TZ]/g, "").slice(0, 14);
  const rand = Math.random().toString(36).slice(2, 8);
  return `demo_${stamp}_${rand}`;
}

async function persistSubmission(
  id: string,
  data: DemoRequestInput,
  receivedAt: string,
) {
  const payload = {
    id,
    receivedAt,
    source: "celestra-web/book-demo",
    ...data,
    linkedin: data.linkedin || null,
  };

  // Structured log for HubSpot / Notion / SIEM adapters later.
  console.info("[book-demo] submission", JSON.stringify(payload));

  try {
    const dir = path.join(process.cwd(), ".data");
    await mkdir(dir, { recursive: true });
    await appendFile(
      path.join(dir, "demo-requests.jsonl"),
      `${JSON.stringify(payload)}\n`,
      "utf8",
    );
  } catch (error) {
    // Vercel production FS may be read-only; logging remains the source of truth.
    console.warn("[book-demo] local persist skipped", error);
  }
}

export async function submitDemoRequest(
  input: DemoRequestInput,
): Promise<DemoRequestResult> {
  const parsed = demoRequestSchema.safeParse(input);

  if (!parsed.success) {
    return {
      ok: false,
      error: "Please correct the highlighted fields.",
      fieldErrors: parsed.error.flatten().fieldErrors,
    };
  }

  const id = createRequestId();
  const receivedAt = new Date().toISOString();

  await persistSubmission(id, parsed.data, receivedAt);

  return { ok: true, id };
}
