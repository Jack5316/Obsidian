---
type: essay
date: 2026-02-19
topic: Distinguish basic concept in AI Engineering, such as function call, tool call, skill, agent, memory, MCP, plugin etc.
note_count: 12
tags:
  - essay
  - synthesis
---

# Beyond the Chat Box: A Clear Lexicon for AI Engineering's Building Blocks

Last month, I spent an afternoon testing the `/mem` skill in Claude Code, watching it stitch a fleeting 5:45 AM thought into my personal AI infrastructure—an infrastructure that, as Fan Bing’s framework lays out, is less a collection of tools and more a persistent, self-owned "Jarvis" for my cognitive life. That small experiment drove home a problem I’ve been circling for months: as we move from ad-hoc AI chats to intentional agentic systems, we’re drowning in overlapping jargon. Function calls, tool calls, skills, agents, memory, MCP, plugins—these terms are often tossed around interchangeably, but they describe distinct, complementary pieces of the same puzzle. If we want to build robust, maintainable AI systems (not just flashy demos), we need a shared, precise lexicon to tell them apart.

Let’s start with the most basic building blocks: **function calls** and **tool calls**. These are the fine-grained, atomic operations that let LLMs do more than generate text. A function call is the narrowest of the two: it’s a structured API invocation, often defined by a JSON schema, where the LLM outputs parameters to trigger a specific piece of code—say, `get_weather(lat=40.7128, lon=-74.0060)` or `read_file(path="notes.md")`. Tool calls are a slightly broader superset: they encapsulate function calls but can also include more complex, stateful interactions, like controlling a browser session or querying a database with a multi-step workflow. Think of it this way: a function call is a single wrench turn; a tool call is the full process of tightening a bolt, which might involve multiple wrench turns and checking alignment along the way. Neither is intelligent on its own—they’re just ways for LLMs to act on the world.

Both function calls and tool calls become far more useful when packaged into **skills**. If function calls are verbs, skills are reusable *recipes*: bundles of prompts, tools, and optional scripts that solve a specific, recurring task. Unlike a one-off prompt, a skill is codified, composable, and shareable—you can add it to an agent with a single command, like `npx skills add obra/superpowers` for structured brainstorming or systematic debugging. The skills digests I’ve been curating are full of examples: `react-doctor` diagnoses and fixes React anti-patterns, `pdf` handles parsing and generating PDFs, `skill-creator` lets you build your own custom skills. The key insight here, borrowed from Fan Bing’s work, is that codifying deterministic work as skills (not prompts) saves tokens, reduces errors, and turns one-time solutions into permanent infrastructure.

To make these skills *do* anything, you need an **agent**—the core orchestrator that ties everything together. An agent is more than a chatbot; it’s a system that has a goal, maintains state, uses tools/skills, and iterates on its actions over time. It might use a ReAct framework (Reason + Act) to think through a problem, pick a skill to execute, and refine its approach based on the result. The OpenClaw framework, which blew up on GitHub last month, is a perfect example: it’s an open-source agent toolkit that lets developers build these orchestrators without being locked into closed corporate systems. Unlike a static plugin, an agent is autonomous—its behavior emerges from the interaction of its goals, tools, and context, rather than being hardcoded into a single feature.

None of this works without **memory**, the context layer that turns generic LLMs into personalized systems. Memory comes in a few flavors: short-term memory (the context window of the current chat), long-term memory (a structured store of past interactions, preferences, and knowledge), and explicit self-models (machine-readable definitions of your identity, writing style, and rules). Fan Bing’s personal AI infrastructure leans hard on this last one: he uses Obsidian as a substrate for a "LLM Context" directory that tells his agent *who he is*—no more relying on flimsy chat history for personalization. The `/mem` skill I tested earlier is a tiny piece of this: it captures fleeting thoughts and adds them to that long-term store, so the agent can build on them later.

Finally, we have **plugins** and **MCP** (Model Context Protocol), two related but distinct ways to extend an agent’s capabilities. Plugins are discrete, pre-packaged extensions that add specific functionality—think a plugin that lets an agent query your calendar or pull data from a SaaS app. They’re often tied to a specific platform (ChatGPT plugins, VSCode extensions) and are designed to be easy to install but limited in flexibility. MCP, by contrast, is an open protocol that standardizes how agents connect to external data sources and tools; it’s a *plumbing layer*, not a pre-built feature. Where a plugin is a single faucet you screw onto a sink, MCP is the pipe system that lets you connect any faucet, hose, or appliance to the water supply. This distinction matters: plugins are great for quick wins, but MCP is what lets you build the loose, interoperable infrastructure Fan Bing advocates for—no lock-in, no walled gardens.

When you put all these pieces together, a clear hierarchy emerges: function calls and tool calls are the atomic actions, skills bundle those actions into reusable recipes, agents orchestrate those skills toward goals, memory gives agents continuity and personalization, and plugins/MCP let them plug into the outside world. This isn’t just semantic nitpicking—it’s the difference between building a rickety pile of chatbot demos and building a real, persistent personal AI infrastructure that buys back your analog time. The underperforming 10x Distill System I analyzed last week is a case study in what happens when you skip this clarity: fragile scrapers, unlabeled content, and a 39% success rate, because we didn’t separate scripts from prompts from skills from agents.

The good news is that we don’t have to build these systems all at once. Fan Bing’s framework starts small: adopt a CLI-first AI tool, build a structured local knowledge base, codify one recurring task as a skill, automate five high-frequency workflows, and schedule regular reviews. The `/mem` skill was my first tiny step; next, I’m planning to formalize the inverse problems pipeline (essay → thread → concepts → flashcards → debate) into a reusable skill. The point isn’t to build a perfect Jarvis overnight—it’s to build a system that evolves with you, one clear, named piece at a time. And to do that, we first need to agree on what those pieces are called.

---

## Sources Referenced

- [[Podcast Digest - 2026-02-19]] (Sources)
- [[GitHub Digest - 2026-02-19]] (Sources)
- [[Skills Digest - 2026-02-19]] (Sources)
- [[Memory - 05:45 - 2026-02-19]] (Inbox)
- [[personal-ai-infra-bearblog]] (Inbox)
- [[Skills Digest - 2026-02-18]] (Sources)
- [[Article - Building Your Personal AI Jarvis A 5-Layer Architecture for Individual Sovereign]] (Sources)
- [[Tagging Convention]] (Atlas)
- [[AI MOC]] (Maps)
- [[AI Agents MOC]] (Maps)
- [[AI Papers MOC]] (Maps)
- [[Self Reflection - 2026-02-19]] (Sources)
