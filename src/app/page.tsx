import { Editorial } from "@/components/home/Editorial";
import { Hero } from "@/components/home/Hero";
import { IntelligenceStack } from "@/components/home/IntelligenceStack";
import { VenturesPreview } from "@/components/home/VenturesPreview";

export default function Home() {
  return (
    <>
      <Hero />
      <Editorial />
      <IntelligenceStack />
      <VenturesPreview />
    </>
  );
}
