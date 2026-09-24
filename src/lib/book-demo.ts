import { z } from "zod";

export const demoProducts = [
  { id: "ai-operating-system", label: "AI Operating System" },
  { id: "ai-agents", label: "AI Agents" },
  { id: "health-intelligence", label: "Health Intelligence" },
  { id: "fintech", label: "Fintech" },
  { id: "robotics", label: "Robotics" },
  { id: "language-intelligence", label: "Language Intelligence" },
  { id: "physical-ai", label: "Physical AI" },
  { id: "semiconductors", label: "Semiconductors" },
  { id: "quantum-computing", label: "Quantum Computing" },
  { id: "motorsport-intelligence", label: "Motorsport Intelligence" },
  { id: "agi-research", label: "AGI Research" },
] as const;

export type DemoProductId = (typeof demoProducts)[number]["id"];

export const companySizes = [
  "1–50",
  "51–200",
  "201–1,000",
  "1,001–5,000",
  "5,000+",
] as const;

export const industries = [
  "Healthcare",
  "Financial Services",
  "Manufacturing",
  "Technology",
  "Defense & Aerospace",
  "Energy",
  "Automotive / Motorsport",
  "Research & Academia",
  "Government",
  "Other",
] as const;

export const meetingLengths = ["30 min", "45 min", "60 min"] as const;

export const timezones = [
  "UTC−08:00 — Pacific Time (US)",
  "UTC−07:00 — Mountain Time (US)",
  "UTC−06:00 — Central Time (US)",
  "UTC−05:00 — Eastern Time (US)",
  "UTC±00:00 — London",
  "UTC+01:00 — Central Europe",
  "UTC+05:30 — India Standard Time",
  "UTC+08:00 — Singapore / Hong Kong",
  "UTC+09:00 — Tokyo / Seoul",
  "UTC+10:00 — Sydney",
] as const;

export const briefingTopics = [
  {
    index: "01",
    title: "Live Product Demonstrations",
    items: [
      "AI Operating System",
      "AI Agents",
      "Health Intelligence",
      "Language Intelligence",
    ],
  },
  {
    index: "02",
    title: "Technical Architecture",
    items: ["Intelligence Stack", "Simulation Engine", "Decision Intelligence"],
  },
  {
    index: "03",
    title: "Enterprise Use Cases",
    items: ["Manufacturing", "Healthcare", "Finance", "Autonomous Systems"],
  },
  {
    index: "04",
    title: "Private Q&A",
    items: [
      "Meet the founder",
      "Architecture discussion",
      "Implementation roadmap",
    ],
  },
] as const;

export const processSteps = [
  {
    index: "01",
    title: "Review",
    body: "We review your request within 24 hours.",
  },
  {
    index: "02",
    title: "Qualification",
    body: "We tailor the demo around your industry.",
  },
  {
    index: "03",
    title: "Private Briefing",
    body: "Live walkthrough with product discussion.",
  },
] as const;

const productIds = demoProducts.map((product) => product.id) as [
  DemoProductId,
  ...DemoProductId[],
];

export const demoRequestSchema = z.object({
  fullName: z.string().trim().min(2, "Enter your full name."),
  workEmail: z
    .string()
    .trim()
    .email("Enter a valid work email.")
    .refine((value) => {
      const domain = value.split("@")[1]?.toLowerCase() ?? "";
      return !["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "icloud.com"].includes(
        domain,
      );
    }, "Use a work email address."),
  company: z.string().trim().min(2, "Enter your company."),
  jobTitle: z.string().trim().min(2, "Enter your job title."),
  companySize: z.enum(companySizes, {
    message: "Select a company size.",
  }),
  industry: z.enum(industries, {
    message: "Select an industry.",
  }),
  products: z
    .array(z.enum(productIds))
    .min(1, "Select at least one product."),
  useCase: z
    .string()
    .trim()
    .min(40, "Describe the use case in a few sentences.")
    .max(4000),
  meetingLength: z.enum(meetingLengths, {
    message: "Select a meeting length.",
  }),
  timezone: z.enum(timezones, {
    message: "Select a timezone.",
  }),
  country: z.string().trim().min(2, "Enter your country."),
  linkedin: z
    .string()
    .trim()
    .refine(
      (value) => value === "" || z.string().url().safeParse(value).success,
      "Enter a valid URL.",
    ),
});

export type DemoRequestInput = z.infer<typeof demoRequestSchema>;

export type DemoRequestResult =
  | { ok: true; id: string }
  | { ok: false; error: string; fieldErrors?: Record<string, string[]> };
