export type Venture = {
  slug: string;
  title: string;
  category: string;
  layer: "Applications" | "Intelligence" | "Compute" | "Physical World";
  shortVision: string;
  dek: string;
  mission: string;
  missionTitle?: string;
  problem: string;
  vision: string;
  architecture: { title: string; body: string }[];
  architectureTitle?: string;
  architectureKicker?: string;
  useCases?: { title: string; body: string }[];
  orchestration?: "language" | "os";
  productName?: string;
  future: string;
  relatedResearch: string[];
};

export const ventures: Venture[] = [
  {
    slug: "ai-agents",
    title: "AI Agents",
    category: "Intelligence Layer",
    layer: "Intelligence",
    shortVision: "Software that works. Not software that waits.",
    dek: "Agents are the first application of the Intelligence Stack that can carry work across time.",
    mission:
      "To make capable, reliable agents a native layer of institutions — systems that can plan, act, and be held to account.",
    problem:
      "Most software still waits for a person to click. Knowledge work is fragmented across tools that cannot remember, cannot coordinate, and cannot finish. The result is not a shortage of intelligence, but a shortage of continuity: tasks die between tabs, decisions lose their context, and organizations pay for attention they should not have to spend.",
    vision:
      "Celestra builds agents as infrastructure. Not chat windows. Not novelty demos. Persistent workers with memory, tools, permissions, and an audit trail — the same seriousness we expect from payroll, custody, or clinical systems. An agent that cannot be governed is not a product. An agent that cannot finish the work is not yet intelligence.",
    architecture: [
      {
        title: "Runtime",
        body: "A controlled loop for perception, planning, tool use, and verification. Every step is inspectable. Every action is attributable.",
      },
      {
        title: "Memory",
        body: "Session, working, and institutional memory as separate instruments — so an agent can be fluent without being reckless with what it retains.",
      },
      {
        title: "Permissions",
        body: "Capability is bounded by policy. Agents inherit the authority of a role, not the privileges of a root user.",
      },
      {
        title: "Evaluation",
        body: "Work is measured against outcomes, not fluency. Completeness, fidelity, and cost sit beside latency as first-class metrics.",
      },
    ],
    future:
      "By 2028, a serious institution should be able to employ a digital workforce the way it employs a human one: with onboarding, supervision, and a record of what was done. Celestra intends to make that ordinary.",
    relatedResearch: ["agents-as-infrastructure", "from-models-to-institutions"],
  },
  {
    slug: "health-intelligence",
    title: "Health Intelligence",
    category: "Applications",
    layer: "Applications",
    shortVision: "Medicine as a continuous system, not a sequence of visits.",
    dek: "Health is the most intimate application of the stack — and the one that can least afford theatre.",
    mission:
      "To give clinicians, researchers, and patients a coherent intelligence layer across records, imaging, protocols, and time.",
    problem:
      "Care is still assembled from fragments: a note, a scan, a lab, a memory. The patient is continuous. The system is not. Errors hide in the gaps between visits, specialties, and institutions. Intelligence, where it exists, is bolted onto workflows designed for paper.",
    vision:
      "Health Intelligence is not a chatbot in a waiting room. It is a longitudinal model of a person and a population — evidence-aware, privacy-bound, and designed to assist judgment rather than replace it. The stack here must be quieter than the stakes: precise, conservative, and worthy of trust.",
    architecture: [
      {
        title: "Longitudinal record",
        body: "A unified, permissioned history that compounds. Care becomes a trajectory, not a stack of PDFs.",
      },
      {
        title: "Clinical reasoning",
        body: "Models that cite, defer, and surface uncertainty. Fluency without provenance is not medicine.",
      },
      {
        title: "Operational fabric",
        body: "Scheduling, triage, and capacity as intelligence problems — so the hospital can think at the speed of the ward.",
      },
      {
        title: "Research loop",
        body: "Anonymized signal feeding discovery without treating the patient as a dataset first.",
      },
    ],
    future:
      "The hospital of the next decades will not be defined by more software. It will be defined by a single intelligence that can hold a life in view — and know when to be silent.",
    relatedResearch: ["the-intelligence-stack", "from-models-to-institutions"],
  },
  {
    slug: "financial-intelligence",
    title: "Financial Intelligence",
    category: "Fintech",
    layer: "Applications",
    shortVision: "Markets that can see themselves in real time.",
    dek: "Finance already runs on models. It does not yet run on a coherent intelligence.",
    mission:
      "To build the intelligence layer for allocation, risk, custody, and institutional decision-making.",
    problem:
      "Capital moves through a lattice of systems that do not share a mind. Risk is reconstructed after the fact. Research is a document. Execution is a button. Governance is a committee. The delay between signal and structure is where losses hide — and where trust erodes.",
    vision:
      "Financial Intelligence is a continuous instrument: research that can act, risk that can speak, and operations that can explain themselves. Celestra approaches finance as a domain where intelligence must be conservative under uncertainty and radical in clarity.",
    architecture: [
      {
        title: "Signal",
        body: "A disciplined ingestion of markets, filings, and alternative structure — without confusing volume for insight.",
      },
      {
        title: "Judgment",
        body: "Models that separate forecast, narrative, and recommendation. Each is a different claim on the world.",
      },
      {
        title: "Control",
        body: "Limits, mandates, and audit as code. Intelligence without constraint is not an institution; it is an accident.",
      },
      {
        title: "Memory of decisions",
        body: "Every allocation leaves a record of belief, not only of price. Organizations should be able to learn from themselves.",
      },
    ],
    future:
      "The financial institution of 2035 will not have a research department and a trading desk as separate civilizations. It will have one intelligence, governed in public to itself.",
    relatedResearch: ["coordination-without-centralization", "the-long-horizon"],
  },
  {
    slug: "ai-operating-system",
    title: "AI Operating System",
    productName: "Celestra OS",
    category: "Intelligence Layer",
    layer: "Intelligence",
    shortVision:
      "The operating system that orchestrates agents, workflows, memory, tools, permissions, and enterprise execution.",
    dek: "The execution layer powering intelligent organizations through agent orchestration, operational intelligence, enterprise workflows, and governed AI execution.",
    missionTitle: "Why AI OS",
    mission:
      "Modern organizations don't need more dashboards. They need systems that can understand operations, coordinate intelligent agents, execute workflows, and continuously improve decision-making. Celestra OS becomes the operating layer between enterprise data and real-world execution.",
    problem:
      "Enterprises accumulate tools that observe and tools that chat. Few systems can take a decision from recommendation to governed execution across agents, people, and machines. Operational intelligence without an operating system remains a report.",
    vision:
      "Celestra OS is infrastructure — not automation theatre. It orchestrates agents, holds operational state, routes work through workflows, and records every action under enterprise governance. Operational intelligence is a capability of the OS, not a separate venture.",
    architectureKicker: "Capabilities",
    architectureTitle: "The execution layer.",
    architecture: [
      {
        title: "Workflow Orchestration",
        body: "Coordinate multiple AI agents across enterprise processes.",
      },
      {
        title: "Operational Intelligence",
        body: "Continuously observe, analyze, and optimize real-time business operations.",
      },
      {
        title: "Decision Engine",
        body: "Turn recommendations into executable workflows with human oversight.",
      },
      {
        title: "Enterprise Governance",
        body: "Permissions, audit logs, security, observability, and compliance.",
      },
    ],
    orchestration: "os",
    useCases: [
      {
        title: "Manufacturing",
        body: "Celestra OS coordinates capacity, exceptions, and agents across the plant — so operational intelligence becomes dispatch, not another dashboard.",
      },
      {
        title: "Healthcare",
        body: "Wards, scheduling, and clinical support run through one execution layer: agents under permission, workflows under audit, decisions under human oversight.",
      },
      {
        title: "Financial Operations",
        body: "Settlement, risk escalation, and institutional workflows execute through the OS — with operational intelligence sensing drift before it becomes loss.",
      },
      {
        title: "Autonomous Robotics",
        body: "Physical agents inherit the same runtime, memory, and governance as digital workers — so the operating system spans software and machines.",
      },
    ],
    future:
      "The advantage will not belong to the company with the most software. It will belong to the company whose operations run on an AI operating system.",
    relatedResearch: ["agents-as-infrastructure", "physical-ai-2035"],
  },
  {
    slug: "language-intelligence",
    title: "Language Intelligence",
    category: "Intelligence Layer",
    layer: "Intelligence",
    shortVision:
      "Enterprise language infrastructure for reasoning, memory, routing, and governed AI communication.",
    dek: "The language layer powering enterprise reasoning, AI agents, robotics, and future intelligent systems.",
    missionTitle: "Why Language Intelligence",
    mission:
      "Language is the interface between humans and intelligent systems. Rather than building another chatbot, Celestra develops the infrastructure that allows enterprises, agents, and machines to understand context, retain memory, reason across knowledge, and communicate reliably.",
    problem:
      "Enterprises do not need another model. They need a language layer that can hold institutional context, route work to the right foundation model, and remain auditable under real governance. Chat interfaces obscure that requirement. Infrastructure makes it explicit.",
    vision:
      "Language Intelligence is the orchestration layer of the stack. Foundation models remain interchangeable. Celestra owns the reasoning, memory, routing, and controls that sit above them — so every Celestra product can speak, remember, and decide under the same enterprise standard.",
    architectureKicker: "Capabilities",
    architectureTitle: "The language layer.",
    architecture: [
      {
        title: "Reasoning Engine",
        body: "Structured and unstructured understanding.",
      },
      {
        title: "Memory Layer",
        body: "Persistent contextual memory across enterprise workflows.",
      },
      {
        title: "Model Routing",
        body: "Intelligently select the optimal foundation model based on quality, latency, and cost.",
      },
      {
        title: "Governance",
        body: "Security, observability, permissions, audit logs, and enterprise controls.",
      },
    ],
    orchestration: "language",
    useCases: [
      {
        title: "Enterprise AI",
        body: "A governed language layer for institutional knowledge — so agents and applications share context without becoming a single uninspectable system.",
      },
      {
        title: "Healthcare",
        body: "Clinical and operational language under provenance: memory that does not invent a patient, and reasoning that can cite what it used.",
      },
      {
        title: "Financial Intelligence",
        body: "Research, risk, and operations speaking through one language infrastructure — with routing and audit as first-class controls.",
      },
      {
        title: "Robotics",
        body: "Natural language as an interface to physical systems, routed through the same memory and permission model as digital agents.",
      },
    ],
    future:
      "The institutions that endure will not be those locked to a single foundation model. They will be those that owned the language layer above it.",
    relatedResearch: ["the-intelligence-stack", "why-we-build-in-layers"],
  },
  {
    slug: "robotics",
    title: "Robotics",
    category: "Physical World",
    layer: "Physical World",
    shortVision: "Bodies for the intelligence we are building.",
    dek: "A mind without a body can write. A civilization needs machines that can move.",
    mission:
      "To develop robotic systems that can perceive, manipulate, and collaborate in unstructured environments — as a native layer of the stack.",
    problem:
      "Robotics has spent decades in cages: factories, labs, scripted cells. The world outside those cages is still largely untouched by machines that can generalize. Meanwhile, intelligence in software has leapt ahead of intelligence in matter. The gap is not only hardware. It is a missing architecture between model and motor.",
    vision:
      "Celestra builds robotics as the hands of the Intelligence Stack. Not a separate industry. Not a hardware sideline. The same agents, models, and compute that run institutions must be able to inhabit space — with safety as a structural property, not a sticker.",
    architecture: [
      {
        title: "Perception",
        body: "Vision, force, and proprioception fused into a state the rest of the stack can reason over.",
      },
      {
        title: "Control",
        body: "Policies that respect physics. Learned motion that can still be bounded by classical guarantees.",
      },
      {
        title: "Embodied agents",
        body: "The same agent runtime that files a report can command a manipulator — under a stricter permission set.",
      },
      {
        title: "Fleet",
        body: "Many bodies, one intelligence layer. Experience compounds across machines without turning every robot into an experiment.",
      },
    ],
    future:
      "The 2030s will not be remembered for humanoid demos. They will be remembered for the first decade in which machines became ordinary colleagues in the physical world.",
    relatedResearch: ["physical-ai-2035", "the-intelligence-stack"],
  },
  {
    slug: "physical-ai",
    title: "Physical AI",
    category: "Physical World",
    layer: "Physical World",
    shortVision: "Intelligence that understands gravity, friction, and time.",
    dek: "Physical AI is not robotics with a better model. It is a different claim: that the world itself is the training ground.",
    mission:
      "To unify perception, simulation, and control so that intelligence can act in the physical world with the same seriousness it now writes with.",
    problem:
      "Digital intelligence was trained on text and images of the world, not on the world. It can describe a cup. It cannot reliably pick one up, or know what it costs to drop it. Simulation helps, and then lies. Reality is the only full curriculum, and we have barely enrolled.",
    vision:
      "Physical AI is the long bridge between the intelligence layer and matter. Foundation models for motion. World models that can be queried. Safety that is geometric, not rhetorical. Celestra holds this as a decade-scale program, not a product line.",
    architecture: [
      {
        title: "World models",
        body: "Internal simulators good enough to plan against, humble enough to be corrected by contact.",
      },
      {
        title: "Foundation control",
        body: "Generalist policies that transfer across embodiments, then specialize without forgetting physics.",
      },
      {
        title: "Closed loop",
        body: "Every real action returns as data. The stack learns from the world the way a scientist learns from an experiment.",
      },
      {
        title: "Assurance",
        body: "Formal bounds where they exist; conservative fallback where they do not. Physical AI that cannot fail safely cannot ship.",
      },
    ],
    future:
      "By 2035, physical AI should be a named layer of industrial civilization — as obvious, and as regulated, as aviation software.",
    relatedResearch: ["physical-ai-2035", "the-long-horizon"],
  },
  {
    slug: "agi",
    title: "AGI Research",
    category: "Intelligence Layer",
    layer: "Intelligence",
    shortVision: "General intelligence as a research obligation, not a slogan.",
    dek: "If general intelligence is possible, it will not arrive as a press release. It will arrive as an architecture.",
    mission:
      "To pursue generally capable systems with the institutional seriousness the subject requires — including the willingness to stop.",
    problem:
      "AGI is discussed as destiny, as stock narrative, as fear. Rarely as an engineering and governance problem with intermediate states. Capability is scaling. Understanding is not. The gap between what a system can do and what its builders can explain is becoming a civilizational risk.",
    vision:
      "Celestra treats AGI as a layer that may one day sit above today’s models — and as a research program that must remain answerable. We do not perform certainty. We build evaluations, interpretability, and control into the stack so that if generality emerges, it emerges inside an architecture that can bear it.",
    architecture: [
      {
        title: "Capability with measurement",
        body: "No claim without a test. Breadth, reliability, and transfer are measured, not advertised.",
      },
      {
        title: "Interpretability",
        body: "A system we cannot inspect is a system we cannot govern. Transparency is a design constraint.",
      },
      {
        title: "Control",
        body: "Corrigibility, containment, and shutdown as features of the runtime — not policies taped to the side.",
      },
      {
        title: "Institutional form",
        body: "AGI research requires a company that can move slowly when the work demands it. That is a product decision.",
      },
    ],
    future:
      "The question is not whether someone will train a more general model. The question is whether the first general systems will be born inside a stack that was designed for them.",
    relatedResearch: ["the-long-horizon", "why-we-build-in-layers"],
  },
  {
    slug: "semiconductors",
    title: "Semiconductors",
    category: "Compute",
    layer: "Compute",
    shortVision: "Thought has a physics. We intend to design it.",
    dek: "The Intelligence Stack is a story about software until it is a story about wafers, wattage, and yield.",
    mission:
      "To treat compute as an architectural layer: devices, interconnect, and systems designed for intelligence rather than borrowed from it.",
    problem:
      "The last decade rented its intelligence from a handful of fabs and a handful of accelerators. That was rational. It is not a strategy. Energy, memory bandwidth, and supply concentration are now the binding constraints on thought. A company that builds intelligence without a point of view on silicon is building on someone else’s timetable.",
    vision:
      "Celestra approaches semiconductors as the floor of the stack. Not a vanity fab. A research and systems program: architectures matched to models, to agents, to physical AI. The aim is sovereignty of design — the ability to specify the machine that intelligence deserves.",
    architecture: [
      {
        title: "Workload truth",
        body: "Agents, training, and control have different shapes. Compute must stop pretending they are one benchmark.",
      },
      {
        title: "Systems",
        body: "From device to rack to facility. Intelligence is an energy story as much as a transistor story.",
      },
      {
        title: "Co-design",
        body: "Model and machine specified together. The stack is allowed to change both.",
      },
      {
        title: "Supply as strategy",
        body: "Partners, process, and geography treated as design inputs, not afterthoughts.",
      },
    ],
    future:
      "The civilizations that lead in intelligence will be the ones that can still make the substrate. Celestra intends to remain fluent in that fact.",
    relatedResearch: ["the-intelligence-stack", "quantum-intelligence"],
  },
  {
    slug: "quantum-computing",
    title: "Quantum Computing",
    category: "Compute",
    layer: "Compute",
    shortVision: "A second physics of computation, held without hype.",
    dek: "Quantum is not a product cycle. It is a scientific weather system. We are building for the climate.",
    mission:
      "To develop the algorithms, interfaces, and institutional literacy that will make quantum computation a layer of intelligence — when the machines can bear it.",
    problem:
      "Quantum computing is trapped between laboratory truth and market fiction. Qubit counts are treated as scoreboards. Useful algorithms are rare. Error correction is the actual mountain. Meanwhile, the intelligence stack is being poured in classical concrete, with no joint left for a different kind of compute.",
    vision:
      "Celestra’s quantum work is patient. Hybrid algorithms. Interfaces that let the intelligence layer call a quantum resource the way it now calls a GPU. Research that can survive a decade of disappointment and still be standing when the machines cross the threshold. We do not sell a quantum future. We leave a place for it in the architecture.",
    architecture: [
      {
        title: "Hybrid runtime",
        body: "Classical control with quantum subroutines. The stack must be able to ask a quantum question without becoming a quantum company overnight.",
      },
      {
        title: "Algorithms",
        body: "Chemistry, materials, optimization, and sampling — the few places where the physics is the point.",
      },
      {
        title: "Error as the product",
        body: "Logical qubits, not slogans. Progress is measured in reliable operations, not in press cycles.",
      },
      {
        title: "Literacy",
        body: "Builders in the rest of the stack must be able to reason about quantum without mythology.",
      },
    ],
    future:
      "By 2045, quantum intelligence should be a named capability in the stack — used where it is true, ignored where it is theatre.",
    relatedResearch: ["quantum-intelligence", "the-long-horizon"],
  },
  {
    slug: "motorsport-intelligence",
    title: "Motorsport Intelligence",
    category: "Applications",
    layer: "Applications",
    shortVision: "The racetrack as a laboratory for extreme intelligence.",
    dek: "Nowhere else does physics, decision, and consequence compress into two hours of public truth.",
    mission:
      "To use motorsport as a proving ground for physical AI, operational intelligence, and human–machine judgment at the limit.",
    problem:
      "Most industrial AI is evaluated in offices. Motorsport is evaluated in tyre degradation, dirty air, and a wall. The sport already runs on data. It does not yet run on a coherent intelligence that can perceive the race as a dynamical system and advise — or act — with the gravity the moment requires.",
    vision:
      "Motorsport Intelligence is not a dashboard for engineers. It is a closed-loop system: simulation, strategy, vehicle, and driver as one. Celestra treats the grid as a scientific instrument. What we learn at 300 kilometres an hour informs robots that walk at three, and operations that cannot afford to guess.",
    architecture: [
      {
        title: "Vehicle state",
        body: "A live model of platform, tyre, energy, and atmosphere — precise enough to bet a race on.",
      },
      {
        title: "Strategy",
        body: "Agents that search the tree of pit, pace, and weather under rules as strict as the sporting code.",
      },
      {
        title: "Driver interface",
        body: "Intelligence that speaks in the language of a lap, not the language of a notebook. Silence is a feature.",
      },
      {
        title: "Transfer",
        body: "Methods that leave the circuit and enter logistics, robotics, and any domain where time is the scarce resource.",
      },
    ],
    future:
      "The first intelligence that can truly race will not be a curiosity. It will be a demonstration that the stack can live inside physics — publicly, every Sunday.",
    relatedResearch: ["physical-ai-2035", "coordination-without-centralization"],
  },
];

export function getVenture(slug: string) {
  return ventures.find((venture) => venture.slug === slug);
}

export function getRelatedVentures(slug: string, limit = 3) {
  const current = getVenture(slug);
  if (!current) return ventures.slice(0, limit);
  const sameLayer = ventures.filter(
    (venture) => venture.slug !== slug && venture.layer === current.layer,
  );
  const rest = ventures.filter(
    (venture) => venture.slug !== slug && venture.layer !== current.layer,
  );
  return [...sameLayer, ...rest].slice(0, limit);
}
