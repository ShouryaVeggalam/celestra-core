"use client";

import { useState, useTransition } from "react";
import Link from "next/link";
import { zodResolver } from "@hookform/resolvers/zod";
import { AnimatePresence, motion } from "framer-motion";
import { Controller, useForm } from "react-hook-form";
import { LoaderCircle } from "lucide-react";
import { submitDemoRequest } from "@/app/book-demo/actions";
import { ProductSelector } from "@/components/book-demo/product-selector";
import { Process } from "@/components/book-demo/process";
import { Magnetic } from "@/components/chrome/Magnetic";
import { Reveal } from "@/components/chrome/Reveal";
import { Button } from "@/components/ui/button";
import {
  companySizes,
  demoProducts,
  demoRequestSchema,
  industries,
  meetingLengths,
  timezones,
  type DemoRequestInput,
} from "@/lib/book-demo";
import { cn } from "@/lib/utils";

const fieldClass =
  "h-12 w-full border border-border bg-transparent px-4 text-[15px] text-foreground outline-none transition-colors duration-500 placeholder:text-muted/50 focus:border-foreground";

const labelClass = "label mb-3 block text-muted";

const selectClass = `${fieldClass} appearance-none pr-10`;

function productLabel(id: string) {
  return demoProducts.find((product) => product.id === id)?.label ?? id;
}

export function DemoForm() {
  const [submittedId, setSubmittedId] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [pending, startTransition] = useTransition();

  const form = useForm<DemoRequestInput>({
    resolver: zodResolver(demoRequestSchema),
    defaultValues: {
      fullName: "",
      workEmail: "",
      company: "",
      jobTitle: "",
      companySize: undefined,
      industry: undefined,
      products: [],
      useCase: "",
      meetingLength: "45 min",
      timezone: undefined,
      country: "",
      linkedin: "",
    },
    mode: "onBlur",
  });

  const {
    register,
    control,
    handleSubmit,
    formState: { errors },
    watch,
  } = form;

  const products = watch("products");

  function onSubmit(values: DemoRequestInput) {
    setFormError(null);
    startTransition(async () => {
      const result = await submitDemoRequest(values);
      if (!result.ok) {
        setFormError(result.error);
        if (result.fieldErrors) {
          for (const [key, messages] of Object.entries(result.fieldErrors)) {
            if (messages?.[0]) {
              form.setError(key as keyof DemoRequestInput, {
                message: messages[0],
              });
            }
          }
        }
        return;
      }
      setSubmittedId(result.id);
    });
  }

  return (
    <AnimatePresence mode="wait">
      {submittedId ? (
        <motion.section
          key="success"
          initial={{ opacity: 0, y: 18 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
          className="border-t border-border py-28 md:py-40"
        >
          <div className="grid-page max-w-3xl">
            <p className="label">Confirmed</p>
            <h2 className="display-md mt-8">Request received.</h2>
            <p className="editorial mt-8 max-w-[34rem]">
              We&apos;ll reach out within 24 hours to schedule your private
              enterprise demo.
            </p>
            <p className="mt-6 text-[12px] tracking-[0.16em] text-muted uppercase">
              Reference {submittedId}
            </p>
            <div className="mt-14">
              <Magnetic>
                <Button asChild>
                  <Link href="/">Return Home</Link>
                </Button>
              </Magnetic>
            </div>
          </div>
        </motion.section>
      ) : (
        <motion.div
          key="form"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0, y: -12 }}
          transition={{ duration: 0.45 }}
        >
          <section id="products" className="border-t border-border py-28 md:py-36">
            <div className="grid-page grid gap-16 lg:grid-cols-12">
              <div className="lg:col-span-4">
                <Reveal>
                  <p className="label">03 — Focus</p>
                  <h2 className="display-md mt-8 max-w-[10ch]">
                    Choose products
                  </h2>
                  <p className="editorial mt-8 max-w-[24rem]">
                    Select the layers you want walked through. Multiple
                    selections are expected.
                  </p>
                </Reveal>
              </div>
              <div className="lg:col-span-8">
                <Controller
                  control={control}
                  name="products"
                  render={({ field }) => (
                    <ProductSelector
                      value={field.value}
                      onChange={field.onChange}
                      error={errors.products?.message}
                    />
                  )}
                />
              </div>
            </div>
          </section>

          <section id="schedule" className="border-t border-border py-28 md:py-36">
            <div className="grid-page">
              <Reveal>
                <p className="label">04 — Request</p>
                <h2 className="display-md mt-8 max-w-[14ch]">
                  Private briefing details
                </h2>
                <p className="editorial mt-8 max-w-[36rem]">
                  For enterprise teams. We use this only to prepare the session —
                  not for outbound marketing.
                </p>
              </Reveal>

              <form
                onSubmit={handleSubmit(onSubmit)}
                className="mt-20 space-y-10"
                noValidate
              >
                <div className="grid gap-8 md:grid-cols-2">
                  <Field label="Full Name" error={errors.fullName?.message}>
                    <input
                      {...register("fullName")}
                      className={fieldClass}
                      autoComplete="name"
                      placeholder="Alex Morgan"
                    />
                  </Field>
                  <Field label="Work Email" error={errors.workEmail?.message}>
                    <input
                      {...register("workEmail")}
                      type="email"
                      className={fieldClass}
                      autoComplete="email"
                      placeholder="alex@company.com"
                    />
                  </Field>
                  <Field label="Company" error={errors.company?.message}>
                    <input
                      {...register("company")}
                      className={fieldClass}
                      autoComplete="organization"
                      placeholder="Company name"
                    />
                  </Field>
                  <Field label="Job Title" error={errors.jobTitle?.message}>
                    <input
                      {...register("jobTitle")}
                      className={fieldClass}
                      autoComplete="organization-title"
                      placeholder="Head of AI / CTO / VP Ops"
                    />
                  </Field>
                  <Field label="Company Size" error={errors.companySize?.message}>
                    <select {...register("companySize")} className={selectClass} defaultValue="">
                      <option value="" disabled>
                        Select
                      </option>
                      {companySizes.map((size) => (
                        <option key={size} value={size}>
                          {size}
                        </option>
                      ))}
                    </select>
                  </Field>
                  <Field label="Industry" error={errors.industry?.message}>
                    <select {...register("industry")} className={selectClass} defaultValue="">
                      <option value="" disabled>
                        Select
                      </option>
                      {industries.map((industry) => (
                        <option key={industry} value={industry}>
                          {industry}
                        </option>
                      ))}
                    </select>
                  </Field>
                </div>

                <Field
                  label="Products of Interest"
                  hint={
                    products.length
                      ? products.map(productLabel).join(" · ")
                      : "Selected above"
                  }
                >
                  <div className="border border-border px-4 py-4 text-[15px] text-muted">
                    {products.length
                      ? products.map(productLabel).join(" · ")
                      : "None selected yet — choose products in the section above."}
                  </div>
                </Field>

                <Field label="Describe your use case" error={errors.useCase?.message}>
                  <textarea
                    {...register("useCase")}
                    rows={6}
                    className="w-full resize-y border border-border bg-transparent px-4 py-3 text-[15px] leading-relaxed text-foreground outline-none transition-colors duration-500 placeholder:text-muted/50 focus:border-foreground"
                    placeholder="What decision, workflow, or system are you evaluating? What constraints matter — regulation, latency, physical deployment, security?"
                  />
                </Field>

                <div>
                  <p className={labelClass}>Preferred Meeting Length</p>
                  <Controller
                    control={control}
                    name="meetingLength"
                    render={({ field }) => (
                      <div className="flex flex-wrap gap-3">
                        {meetingLengths.map((length) => {
                          const active = field.value === length;
                          return (
                            <button
                              key={length}
                              type="button"
                              data-cursor="expand"
                              onClick={() => field.onChange(length)}
                              className={cn(
                                "h-12 border px-6 text-[12px] tracking-[0.16em] uppercase transition-colors duration-500",
                                active
                                  ? "border-foreground text-foreground"
                                  : "border-border text-muted hover:border-foreground/50 hover:text-foreground",
                              )}
                            >
                              {length}
                            </button>
                          );
                        })}
                      </div>
                    )}
                  />
                  {errors.meetingLength ? (
                    <p className="mt-3 text-[13px] text-muted">
                      {errors.meetingLength.message}
                    </p>
                  ) : null}
                </div>

                <div className="grid gap-8 md:grid-cols-2">
                  <Field label="Preferred Timezone" error={errors.timezone?.message}>
                    <select {...register("timezone")} className={selectClass} defaultValue="">
                      <option value="" disabled>
                        Select
                      </option>
                      {timezones.map((zone) => (
                        <option key={zone} value={zone}>
                          {zone}
                        </option>
                      ))}
                    </select>
                  </Field>
                  <Field label="Country" error={errors.country?.message}>
                    <input
                      {...register("country")}
                      className={fieldClass}
                      autoComplete="country-name"
                      placeholder="United States"
                    />
                  </Field>
                </div>

                <Field
                  label="LinkedIn (optional)"
                  error={errors.linkedin?.message}
                >
                  <input
                    {...register("linkedin")}
                    className={fieldClass}
                    placeholder="https://www.linkedin.com/in/…"
                  />
                </Field>

                {formError ? (
                  <p className="text-[14px] text-muted">{formError}</p>
                ) : null}

                <div className="pt-4">
                  <Magnetic>
                    <Button type="submit" size="lg" disabled={pending}>
                      {pending ? (
                        <>
                          <LoaderCircle className="h-4 w-4 animate-spin" />
                          Submitting
                        </>
                      ) : (
                        "Request Private Demo"
                      )}
                    </Button>
                  </Magnetic>
                </div>
              </form>
            </div>
          </section>

          <Process />
        </motion.div>
      )}
    </AnimatePresence>
  );
}

function Field({
  label,
  error,
  hint,
  children,
}: {
  label: string;
  error?: string;
  hint?: string;
  children: React.ReactNode;
}) {
  return (
    <label className="block">
      <span className={labelClass}>{label}</span>
      {children}
      {hint && !error ? (
        <span className="mt-3 block text-[12px] tracking-[0.08em] text-muted">
          {hint}
        </span>
      ) : null}
      {error ? <span className="mt-3 block text-[13px] text-muted">{error}</span> : null}
    </label>
  );
}
