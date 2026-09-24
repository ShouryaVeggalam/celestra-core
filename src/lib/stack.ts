export const stackLayers = [
  {
    id: "applications",
    index: "01",
    title: "Applications",
    statement: "Intelligence that acts inside institutions.",
    body: "The layer the world touches. Domain systems for health, finance, and the extreme laboratory of motorsport — where intelligence must prove itself in real institutions.",
    nodes: [
      { label: "Health Intelligence", href: "/ventures/health-intelligence" },
      { label: "Fintech", href: "/ventures/financial-intelligence" },
      { label: "Motorsport Intelligence", href: "/ventures/motorsport-intelligence" },
    ],
  },
  {
    id: "intelligence",
    index: "02",
    title: "Intelligence",
    statement: "The cognitive and execution core of the stack.",
    body: "Celestra OS, agents, language infrastructure, and research toward general systems — the layers that reason, orchestrate, and execute under enterprise control.",
    nodes: [
      { label: "AI Operating System", href: "/ventures/ai-operating-system" },
      { label: "AI Agents", href: "/ventures/ai-agents" },
      { label: "Language Intelligence", href: "/ventures/language-intelligence" },
      { label: "AGI Research", href: "/ventures/agi" },
    ],
  },
  {
    id: "compute",
    index: "03",
    title: "Compute",
    statement: "The physical substrate of thought.",
    body: "Intelligence is not immaterial. It runs on silicon, energy, interconnect — and, in time, quantum methods that sit beside classical computation.",
    nodes: [
      { label: "Semiconductors", href: "/ventures/semiconductors" },
      { label: "Quantum Computing", href: "/ventures/quantum-computing" },
    ],
  },
  {
    id: "physical",
    index: "04",
    title: "Physical World",
    statement: "Where intelligence meets matter, motion, and time.",
    body: "Robots and physical AI — machines that must perceive, decide, and act under real constraints.",
    nodes: [
      { label: "Robotics", href: "/ventures/robotics" },
      { label: "Physical AI", href: "/ventures/physical-ai" },
    ],
  },
] as const;

export type StackLayer = (typeof stackLayers)[number];
