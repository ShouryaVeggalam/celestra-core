export type ResearchCategory =
  | "Whitepapers"
  | "Future Briefings"
  | "Founder Essays"
  | "Research Papers";

export type ResearchBlock =
  | { type: "p"; text: string }
  | { type: "h2"; text: string }
  | { type: "quote"; text: string }
  | { type: "ul"; items: string[] };

export type ResearchArticle = {
  slug: string;
  title: string;
  dek: string;
  category: ResearchCategory;
  date: string;
  author: string;
  relatedVentures: string[];
  blocks: ResearchBlock[];
};

export const research: ResearchArticle[] = [
  {
    slug: "the-intelligence-stack",
    title: "The Intelligence Stack",
    dek: "Why Celestra is one company, and why the work is a stack rather than a collection of products.",
    category: "Whitepapers",
    date: "2026-03-01",
    author: "Celestra Research",
    relatedVentures: ["language-intelligence", "ai-agents", "semiconductors"],
    blocks: [
      {
        type: "p",
        text: "A stack is not a metaphor we borrowed from software. It is a claim about how intelligence will actually exist in the world. Applications sit on models. Models sit on compute. Compute sits on physics. Physics, in the end, sits in factories, hospitals, markets, and machines. If those layers are designed by separate civilizations that do not speak, the result will not be intelligence. It will be a pile of tools.",
      },
      {
        type: "quote",
        text: "We are not assembling a portfolio. We are specifying a machine that happens to be a company.",
      },
      {
        type: "h2",
        text: "The mistake of the last decade",
      },
      {
        type: "p",
        text: "The last decade treated models as products and products as companies. That was a reasonable response to a sudden capability. It is a poor response to a civilizational one. When electricity arrived, the durable work was not the lamp. It was generation, transmission, standard, and the buildings that could assume the current would be there. Intelligence is entering the same kind of weather.",
      },
      {
        type: "p",
        text: "Celestra exists because we believe the next generation of intelligence will be infrastructural. It will not live in a single interface. It will live in a set of layers that institutions can depend on: agents that can finish work, models that can be evaluated, compute that can be specified, and machines that can act in the physical world without becoming a hazard.",
      },
      {
        type: "h2",
        text: "Four layers, one system",
      },
      {
        type: "p",
        text: "Applications are where intelligence meets a domain: health, fintech, and motorsport. Intelligence is the cognitive and execution core: the AI operating system, agents, language intelligence, and research toward general systems. Compute is the substrate — semiconductors and quantum methods as architectural concerns, not purchase orders. The physical world is the remainder that software culture keeps forgetting: robotics and physical AI.",
      },
      {
        type: "p",
        text: "The arrows between layers are the product. An agent that cannot call a model under policy is a toy. A model that cannot run on a machine we understand is a dependency. A robot that cannot inherit the same permission system as a digital worker is a second company pretending to be the first. The stack is the refusal of that fragmentation.",
      },
      {
        type: "h2",
        text: "What we will not do",
      },
      {
        type: "ul",
        items: [
          "We will not ship a layer that cannot be governed.",
          "We will not pretend a demo is a system.",
          "We will not treat time horizons as a branding exercise.",
          "We will not separate the physical and the digital into different moral universes.",
        ],
      },
      {
        type: "p",
        text: "This whitepaper is a charter more than a specification. The specification will take decades. The charter is simple: build the systems that power the next generation of intelligence as one architecture, or do not build them at all.",
      },
    ],
  },
  {
    slug: "agents-as-infrastructure",
    title: "Agents as Infrastructure",
    dek: "A theory of digital labor that can be employed, supervised, and retired.",
    category: "Whitepapers",
    date: "2026-05-18",
    author: "Celestra Research",
    relatedVentures: ["ai-agents", "ai-operating-system"],
    blocks: [
      {
        type: "p",
        text: "An agent is not a personality. It is a runtime with a job. The industry has spent several years trying to make software talk. The more interesting problem is to make software responsible: to give it a scope, a memory, a budget, and a way to be wrong that does not become a catastrophe.",
      },
      {
        type: "p",
        text: "Infrastructure is that which institutions forget until it fails. Electricity. Settlement. Identity. If agents are going to file the report, move the money, schedule the ward, or brief the pit wall, they must pass the same test. They must be boring in the right ways.",
      },
      {
        type: "h2",
        text: "Continuity is the product",
      },
      {
        type: "p",
        text: "A language model completes a prompt. An agent completes a week. The difference is memory, tool use, and a relationship to time. Most failures we call ‘hallucination’ are in fact failures of continuity: the system did not know what it had already promised, already seen, already been forbidden to do.",
      },
      {
        type: "quote",
        text: "Fluency is a surface. Continuity is a structure.",
      },
      {
        type: "h2",
        text: "The four instruments",
      },
      {
        type: "p",
        text: "We design agents with four instruments that must remain distinct. Runtime: the loop of perceive, plan, act, verify. Memory: session, working, and institutional, never collapsed into one slurry. Permissions: capability inherited from a role, not from the model’s appetite. Evaluation: outcomes, not vibes — completeness, fidelity, cost, and the ability to stop.",
      },
      {
        type: "p",
        text: "When these instruments are mixed, you get a chatbot with access to production. When they are held apart, you get something an institution can hire. That is the standard. Not cleverness. Employability.",
      },
      {
        type: "h2",
        text: "Labor, not magic",
      },
      {
        type: "p",
        text: "By 2028 we expect serious organizations to speak of a digital workforce without irony. That will only be humane — and only be safe — if the workforce has managers, logs, and a door. Celestra’s agent work is the doorframe.",
      },
    ],
  },
  {
    slug: "physical-ai-2035",
    title: "Physical AI, 2035",
    dek: "A briefing on the decade in which intelligence has to pick things up.",
    category: "Future Briefings",
    date: "2026-07-09",
    author: "Celestra Research",
    relatedVentures: ["physical-ai", "robotics", "motorsport-intelligence"],
    blocks: [
      {
        type: "p",
        text: "Between now and 2035, the centre of gravity in intelligence will move from tokens to contact. Not because language will become uninteresting, but because the remaining work of civilization is physical: care, construction, logistics, energy, and the machines that fail when a model is merely eloquent.",
      },
      {
        type: "p",
        text: "Physical AI is the name we give to systems that can perceive, predict, and act under gravity. It is not a humanoid. It is not a warehouse arm. It is a layer: world models, foundation control, closed-loop data, and assurance that can survive a lawyer and a physicist in the same room.",
      },
      {
        type: "h2",
        text: "The curriculum of reality",
      },
      {
        type: "p",
        text: "Text is a lossy compression of the world. Useful, cheap, infinitely copyable. Reality is expensive and unforgiving. The laboratories that will matter are factories, hospitals, farms, and circuits — places where a wrong action has a mass. Motorsport is one such laboratory. So is a ward at 3 a.m. So is a line that cannot stop.",
      },
      {
        type: "quote",
        text: "A system that cannot fail safely has not yet earned the right to move.",
      },
      {
        type: "h2",
        text: "What 2035 requires",
      },
      {
        type: "ul",
        items: [
          "Generalist control that transfers across embodiments without becoming a stunt.",
          "Simulation that knows it is lying, and a data loop that corrects it.",
          "Permission systems shared with digital agents, stricter by an order of magnitude.",
          "Public evaluation: not a video, a protocol.",
        ],
      },
      {
        type: "p",
        text: "Celestra’s physical program is paced to that decade. We will not hurry a body ahead of a brain that can be responsible for it. We will also not pretend that intelligence which cannot touch the world is finished.",
      },
    ],
  },
  {
    slug: "quantum-intelligence",
    title: "Quantum Intelligence",
    dek: "How to leave a joint in the stack for a different physics of thought.",
    category: "Future Briefings",
    date: "2026-09-02",
    author: "Celestra Research",
    relatedVentures: ["quantum-computing", "semiconductors", "agi"],
    blocks: [
      {
        type: "p",
        text: "Quantum computing will disappoint almost everyone who needs it to be a product this year. That is not an argument for ignoring it. It is an argument for placing it correctly: as a future tense of the intelligence layer, with a classical present that must remain excellent.",
      },
      {
        type: "p",
        text: "The error-corrected machine is the mountain. Logical qubits, not inventories of noisy ones, are the unit of progress. Until that mountain is climbed, the honest work is algorithms, interfaces, and literacy — so that the day the machine works, the stack already knows how to ask it a question.",
      },
      {
        type: "h2",
        text: "Hybrid, or nothing",
      },
      {
        type: "p",
        text: "There will be no quantum company that replaces the rest of intelligence. There will be quantum subroutines called by classical control, the way a GPU is called today by a training loop. Chemistry, materials, certain sampling and optimization regimes: these are the rooms in which the physics is the point. Everywhere else, mythology is a cost.",
      },
      {
        type: "quote",
        text: "We do not sell a quantum future. We leave a place for it in the architecture.",
      },
      {
        type: "p",
        text: "Celestra’s briefing to itself is simple. Fund the science. Refuse the theatre. Keep the joint open. By 2045, if the machines have crossed the threshold, quantum intelligence should be a named capability — used where it is true.",
      },
    ],
  },
  {
    slug: "why-we-build-in-layers",
    title: "Why We Build in Layers",
    dek: "A founder’s note on patience, refusal, and the shape of the company.",
    category: "Founder Essays",
    date: "2026-02-14",
    author: "Shourya Veggalam",
    relatedVentures: ["language-intelligence", "agi", "ai-agents"],
    blocks: [
      {
        type: "p",
        text: "I did not start Celestra because the world needed another application. I started it because the applications were about to become the least interesting part of the story. When intelligence becomes cheap to invoke and expensive to govern, the work moves down. Into models. Into machines. Into the physical world. Into the institutions that will have to live with all three.",
      },
      {
        type: "p",
        text: "Layers are how you stay honest. A layer has a job. It has interfaces. It can be tested without a keynote. If a company is only a collection of bets, it will sell whatever is fashionable in the layer that prints this year. If a company is a stack, it can decline a shortcut that would poison a layer above or below.",
      },
      {
        type: "h2",
        text: "One vision",
      },
      {
        type: "p",
        text: "Health, finance, operations, agents, models, robots, silicon, quantum, the racetrack — these are not ten startups in a trench coat. They are the places the same architecture must prove itself. A hospital is a real-time system. A market is a real-time system. A car at two hundred and ninety kilometres an hour is a real-time system. If our intelligence cannot inhabit those rooms, it is not yet the thing we claim to be building.",
      },
      {
        type: "quote",
        text: "The stack is a moral document. It says what we are willing to be responsible for.",
      },
      {
        type: "h2",
        text: "Time",
      },
      {
        type: "p",
        text: "The timeline we publish is not a promise of dates. It is a refusal to pretend that AGI, robots, and quantum machines live on a startup calendar. 2026 is a foundation. 2050 is a civilization that can assume intelligence the way it now assumes electricity. Everything between is work.",
      },
      {
        type: "p",
        text: "I am interested in builders who can hold that distance without becoming vague. Precision in the present. Ambition in the horizon. That is the whole method.",
      },
    ],
  },
  {
    slug: "the-long-horizon",
    title: "The Long Horizon",
    dek: "On 2050, and why a company should be able to speak about it without embarrassment.",
    category: "Founder Essays",
    date: "2026-08-21",
    author: "Shourya Veggalam",
    relatedVentures: ["agi", "quantum-computing", "physical-ai"],
    blocks: [
      {
        type: "p",
        text: "Most companies are allergic to the far future because the far future cannot close a quarter. That is a reasonable allergy if you are selling a tool. It is malpractice if you are building infrastructure. Nobody serious would fund a power grid that could only imagine five years. Intelligence is becoming a grid. We should be able to say the word 2050 without lowering our voice.",
      },
      {
        type: "p",
        text: "The long horizon is not a prophecy. It is a design constraint. If you believe that general systems may exist, you do not wait to invent governance in the week they arrive. If you believe that machines will move among us, you do not treat safety as a later module. If you believe quantum computation might matter, you do not pour the classical stack in a shape that cannot accept it.",
      },
      {
        type: "h2",
        text: "Civilization as a customer",
      },
      {
        type: "p",
        text: "By 2050 I do not mean a utopia of agents. I mean a condition: intelligence as a public assumption. Hospitals that never lose the thread of a life. Firms that can simulate themselves. Machines that can be employed. Models that can be inspected. Compute that a nation can reason about. That condition has a name in our timeline: Intelligence Civilization. It is a direction, not a deliverable.",
      },
      {
        type: "quote",
        text: "A horizon is useful when it makes today’s architecture stricter, not when it makes today’s language larger.",
      },
      {
        type: "p",
        text: "Celestra will be judged on the next system it ships, not on the year 2050. That is as it should be. The horizon is there to keep us from shipping a system that cannot live in that year.",
      },
    ],
  },
  {
    slug: "coordination-without-centralization",
    title: "Coordination Without Centralization",
    dek: "How intelligent systems should act together without becoming a single point of failure — or a single point of power.",
    category: "Research Papers",
    date: "2026-06-11",
    author: "Celestra Research",
    relatedVentures: ["ai-operating-system", "financial-intelligence", "motorsport-intelligence"],
    blocks: [
      {
        type: "p",
        text: "The temptation, once you can build an agent, is to build a sovereign: one model, one memory, one authority. It is an elegant temptation. It is also how institutions fail. A hospital, a market, a race team, a factory — these are already distributed systems. Intelligence that can only coordinate by becoming the centre is not an upgrade. It is a new fragility.",
      },
      {
        type: "h2",
        text: "Protocols over thrones",
      },
      {
        type: "p",
        text: "We argue for coordination as protocol. Agents, humans, and machines share state through interfaces that can be audited. Authority is local, inherited, and revocable. Plans can be proposed by a model and accepted by a role. No layer of the stack should require a god process.",
      },
      {
        type: "p",
        text: "This is not a political aesthetic. It is an engineering one. Centralized intelligence concentrates error the way centralized compute concentrates heat. When the error is a misallocated trade, a missed diagnosis, or a late pit call, concentration is not efficiency. It is blast radius.",
      },
      {
        type: "quote",
        text: "The stack should be able to think together without thinking as one.",
      },
      {
        type: "h2",
        text: "Implications",
      },
      {
        type: "ul",
        items: [
          "Memory is partitioned. Institutional memory is not a pool that every agent may drink from.",
          "Messages are typed. A recommendation is not an action. An action is not a policy change.",
          "Simulation is a shared commons; execution is permissioned.",
          "Human override is a first-class message type, not an exception path.",
        ],
      },
      {
        type: "p",
        text: "Motorsport makes the argument brutally small: many agents, one car, one evening, no replay that matters. Finance makes it large. The architecture should be the same shape at both scales.",
      },
    ],
  },
  {
    slug: "from-models-to-institutions",
    title: "From Models to Institutions",
    dek: "Evaluation, liability, and the unglamorous work of making intelligence fit for a hospital or a balance sheet.",
    category: "Research Papers",
    date: "2026-10-04",
    author: "Celestra Research",
    relatedVentures: ["health-intelligence", "ai-agents", "language-intelligence"],
    blocks: [
      {
        type: "p",
        text: "A model can be impressive and still be unemployable. Institutions do not hire impressive. They hire systems that can be insured, inspected, and interrupted. The distance between those two standards is the actual product surface of the Intelligence Stack.",
      },
      {
        type: "h2",
        text: "What an institution requires",
      },
      {
        type: "p",
        text: "Provenance: where did this answer come from. Uncertainty: how should a professional weight it. Authority: who was allowed to act. Memory: what is retained, for whom, for how long. Recourse: how is a mistake unwound. None of these are model tricks. They are institutional facts that must be implemented as software.",
      },
      {
        type: "p",
        text: "Health makes the list non-negotiable. Finance makes it expensive. Operations makes it constant. Agents make it unavoidable, because an agent that can act is already a kind of employee. We should stop designing for a user who clicks and start designing for an organization that can be sued.",
      },
      {
        type: "quote",
        text: "If a system cannot enter the record, it cannot enter the institution.",
      },
      {
        type: "h2",
        text: "Evaluation as architecture",
      },
      {
        type: "p",
        text: "We treat evaluation as a layer, not a ritual. Every application in the stack declares the claims it makes on the world and the tests those claims must survive. A clinical suggestion is a different claim from a drafting assistant. A trade is a different claim from a summary. The model may be shared. The claim is not.",
      },
      {
        type: "p",
        text: "This paper is a beginning. The work is to make the boring path the default path — so that the Intelligence Stack can live in rooms where theatre is unethical.",
      },
    ],
  },
];

export const researchCategories: ResearchCategory[] = [
  "Whitepapers",
  "Future Briefings",
  "Founder Essays",
  "Research Papers",
];

export function getArticle(slug: string) {
  return research.find((article) => article.slug === slug);
}

export function articleText(article: ResearchArticle) {
  return article.blocks
    .map((block) => {
      if (block.type === "p" || block.type === "h2" || block.type === "quote") {
        return block.text;
      }
      return block.items.join(" ");
    })
    .join(" ");
}

export function getRelatedArticles(slug: string, limit = 3) {
  const current = getArticle(slug);
  if (!current) return research.slice(0, limit);
  return research
    .filter((article) => article.slug !== slug)
    .sort((a, b) => {
      const aScore = a.category === current.category ? 1 : 0;
      const bScore = b.category === current.category ? 1 : 0;
      return bScore - aScore;
    })
    .slice(0, limit);
}
