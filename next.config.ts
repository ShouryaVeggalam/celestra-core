import path from "node:path";
import { fileURLToPath } from "node:url";
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  turbopack: {
    root: path.dirname(fileURLToPath(import.meta.url)),
  },
  transpilePackages: ["three", "@react-three/fiber", "@react-three/drei"],
  async redirects() {
    return [
      {
        source: "/ventures/llms",
        destination: "/ventures/language-intelligence",
        permanent: true,
      },
      {
        source: "/ventures/operational-intelligence",
        destination: "/ventures/ai-operating-system",
        permanent: true,
      },
    ];
  },
};

export default nextConfig;
