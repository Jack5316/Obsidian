---
title: Building Your Personal AI Jarvis - A 5-Layer Architecture for Individual Sovereignty
author: "Jack"
digest: "Fan Bing's 5-layer framework for building personal AI infrastructure. Own your Jarvis."
---

# Building Your Personal AI Jarvis: A 5-Layer Architecture for Individual Sovereignty

*Lessons from Fan Bing's practical framework for constructing a personal AI infrastructure*

---

## The Problem Nobody Talks About

We are drowning in AI tools but starving for AI *systems*.

Every week brings a new chatbot, a new wrapper, a new "AI-powered" SaaS. Yet most knowledge workers still interact with AI the same way they did in 2023 — opening a browser tab, typing a prompt, copying the output, pasting it somewhere else, and repeating. This is the digital equivalent of carrying water in buckets when you could be building plumbing.

Fan Bing (范冰, @XDash), a Chinese growth hacker and AI practitioner, noticed this gap after becoming a father. Time became his scarcest resource. His response wasn't to find a better chatbot — it was to engineer an entire **Personal AI Infrastructure (PAI)**, a system he calls his "Jarvis," that runs 24/7, owns his data, writes in his voice, monitors his information feeds, and evolves over time. His methodology, laid out in a recent course titled *"How I Practiced Building a Personal AI Jarvis"*, offers a surprisingly disciplined architectural blueprint that deserves wider attention.

What follows is not a tool review. It is an analysis of a **design philosophy** — one that treats personal AI not as a product you subscribe to, but as infrastructure you build and own.

---

## The Core Insight: Infrastructure, Not Applications

The foundational distinction in Fan Bing's framework is between using AI *applications* and building AI *infrastructure*. He defines Personal AI Infrastructure as:

> A highly autonomous, programmable, and extensible AI runtime environment and toolchain designed and deployed for a single natural person — not a team or enterprise.

The key characteristics he identifies are:

- **Persistent operation** — running 7x24 on a home server, NAS, Mac mini, or cloud VPS
- **Complete sovereignty** — code, model weights, memory, tools, and API keys are all personally held, with zero dependency on centralized commercial platforms
- **Multi-agent/multi-model orchestration** — an LLM as a central controller dispatching specialist models, tools, skills, and memory systems
- **Strong execution capability** — not just conversation, but real action: reading/writing files, controlling browsers, calling APIs, managing calendars, sending emails, running workflows
- **Self-evolution** — the system learns your preferences, summarizes its own experience, develops custom skills, and iterates continuously

This is a radically different mental model from "which chatbot should I use?" It reframes the question as: *What operating system am I building for my cognitive life?*

---

## The 5-Layer Pyramid: An Architecture Worth Studying

The heart of Fan Bing's methodology is a **five-layer pyramid**, built bottom-up, with each layer independently optimizable and loosely coupled to the others. This is good systems thinking — the kind of layered abstraction that made the OSI model or the Unix philosophy so durable.

### Layer 1: Dev Tools (CLI-First Development)

The foundation is not a fancy GUI — it's the command line. Fan Bing makes a forceful argument for CLI over GUI as the primary interface to AI:

**GUI** — Manual intervention. Difficult to batch. Isolated. Reconfigure every time.

**CLI** — Programmable. Automated. Seamless integration. Configure once, use forever.

His recommended tools are Claude Code, CodeBuddy Code (Tencent's alternative with better China accessibility), and OpenCode (free, open-source). But the specific tool matters less than the principle: **if your AI interaction isn't scriptable, it isn't infrastructure.**

There's an elegant power move here too: CLI + SSH means you can control your entire Jarvis system from a phone in bed, from a holiday resort, from anywhere — with less bandwidth than a remote desktop session.

### Layer 2: Data Layer (Obsidian as the Knowledge Substrate)

For the data layer, Fan Bing chose Obsidian — and his reasoning reveals deep architectural thinking:

- **Local-first**: your data lives on your machine, not someone else's server
- **Markdown format**: the most AI-friendly, universally portable text format
- **Bidirectional links**: knowledge becomes a graph, not a filing cabinet

His Obsidian vault is structured with explicit LLM context directories:

> **LLM Context/**
> - **Personal Profile/** — Who am I?
> - **My Writing Style/** — How do I speak?
> - **Dynamic Activities/** — What am I doing right now?
> - **My Flavor/** — What are my preferences?
> - **Basic Rules/** — System rules and configurations

This is the directory structure of a *self-model* — a machine-readable representation of the user's identity, style, current state, and preferences. Every time the AI runs a task, it can load the relevant context slices. The AI doesn't need to "know" you because you've been chatting for months; it knows you because your self-model is explicitly engineered and maintained.

### Layer 3: Skills Layer (Reusable Workflow Units)

This is where Fan Bing draws a critical distinction:

> **Prompt** = a one-off instruction. **Skill** = a codified, reusable workflow.

A Skill is a packaged unit of work — a combination of prompts, scripts, API calls, and data references that can be invoked repeatedly. Skills are:

- **Reusable** — run the same workflow tomorrow without rebuilding it
- **Composable** — Skill A + Skill B = Complex Workflow
- **Extensible** — add new capabilities without rewriting the system

He advocates a "Small File Philosophy" inspired by Unix: each skill does one thing well, is easy to understand and maintain, and gains power through composition.

The practical implication is profound: **every time you solve a problem with AI, you should ask whether the solution can be extracted into a reusable skill.** If yes, you've turned a one-time effort into permanent infrastructure.

### Layer 4: Scenarios Layer (40+ Automated Daily Tasks)

With tools, data, and skills in place, Layer 4 is where the system *does work*. Fan Bing runs 40+ automated tasks spanning three categories:

**Information Collection** — pulling from Flomo, Bilibili, YouTube, Jike, RSS feeds

**Knowledge Management** — daily reviews, diary archiving, automatic tagging

**Content Creation** — subtitle extraction, material recommendation, script generation

His practical cases illustrate the range:

1. **Blog writing in his personal voice** — the system loads his writing style profile and historical articles, generates a draft via Claude, and writes it directly into Obsidian. What took 2 hours now takes 10 minutes — a 12x efficiency gain.
2. **Video script generation** — automatically scrapes trending topics from aggregators, then applies in-context learning from his style to produce scripts.
3. **Bilibili video summarization** — monitors saved long-form videos, extracts key points, and emails him the summaries.
4. **Voice-controlled Jarvis** — using voice assistants as a natural language front-end, he can issue complex commands verbally and have his infrastructure execute them.

### Layer 5: Review Layer (The System That Watches Itself)

The final layer is meta-cognitive — the system reflecting on its own performance:

- **Daily**: aggregate email summaries, check system health
- **Weekly**: adjust information sources, filter noise
- **Monthly**: optimize the system, upgrade skills

This is what separates a collection of automations from true infrastructure. Without a review layer, entropy wins — information sources go stale, skills drift out of relevance, and the system slowly becomes a liability instead of an asset. The review layer ensures the system is, as Fan Bing puts it, *"alive and continuously evolving."*

---

## The Deeper Lessons

### 1. Scripts Before Prompts

One of Fan Bing's most counterintuitive cost-control insights: **if you can codify a task as a Python script, don't burn tokens on it.** Prompts are for judgment, creativity, and ambiguity. Deterministic operations — file manipulation, API calls, data formatting — should be handled by traditional code. This keeps costs down and reliability up.

### 2. Context Is the Moat

The real competitive advantage of a personal AI system isn't the model — it's the context. Your writing samples, your preferences, your current projects, your information diet — this is what transforms a generic LLM into *your* assistant. Fan Bing's advice: you don't need to build the perfect context library on day one. Accumulate gradually. But *do* accumulate.

### 3. Loose Coupling Is Non-Negotiable

Each layer of the pyramid can be swapped independently. Don't like Claude Code? Switch to CodeBuddy. Want to move from Obsidian to Logseq? The skills layer doesn't care. This architectural discipline prevents vendor lock-in and allows each component to evolve at its own pace.

### 4. Don't Chase Hype — Solve Real Problems

Fan Bing's closing reminder is sobering in an era of daily AI breakthroughs:

> "Don't get addicted to chasing hot trends. Stay focused. Solve real problems."

And perhaps more importantly:

> *"Digital for Efficiency, Analog for Clarity."*

The goal of building a Jarvis isn't to live inside the machine. It's to **buy back time for the physical world** — for raising children, for thinking deeply, for being present.

---

## What This Means for You

You don't need to replicate Fan Bing's exact stack. The value of this framework isn't in the specific tools — it's in the **architectural thinking**:

1. **Start with Layer 1**: Get comfortable with a CLI AI tool. Make your AI interactions scriptable.
2. **Build Layer 2**: Create a structured, local-first knowledge base. Begin documenting who you are in a format AI can read.
3. **Extract Layer 3**: Every time you do something twice with AI, turn it into a skill.
4. **Automate Layer 4**: Identify your 5 most repetitive information tasks and automate them.
5. **Institute Layer 5**: Set a weekly calendar reminder to review and prune your system.

The progression is deliberately bottom-up. You can't automate scenarios (L4) without skills (L3). You can't build skills without data (L2). You can't work with data effectively without proper tooling (L1). And none of it stays healthy without review (L5).

---

## The Bigger Picture

We are at an inflection point. The gap between people who *use* AI and people who *build AI infrastructure for themselves* is about to become the most consequential digital divide since the gap between internet users and non-users in the late 1990s.

Fan Bing's framework suggests that personal AI infrastructure isn't a luxury for engineers — it's becoming a literacy. The 5-layer pyramid gives us a vocabulary and a blueprint. The rest is practice.

And practice, as the title of his course reminds us, is the point. Not theory. Not hype. Practice.

*Build your Jarvis. One layer at a time.*