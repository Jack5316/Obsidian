---
type: concept-digest
date: 2026-02-20
topic: all
note_count: 49
tags:
  - concept
  - extraction
---

# Concept Digest

## Personal AI Infrastructure (PAI)
Personal AI Infrastructure is a self-owned, programmable, and persistent system designed for a single individual, not a team or enterprise. It treats AI not as a collection of applications to use, but as sovereign infrastructure to build—characterized by 24/7 operation, full data ownership, multi-agent orchestration, strong execution capabilities, and self-evolution. The goal is to move beyond manual, ad-hoc AI interactions toward an automated "Jarvis" that learns your context, handles workflows, and ultimately buys back analog time for deep thinking and presence. This represents a fundamental shift from being a consumer of AI tools to being the architect of your own cognitive operating system.
Appears in: [[personal-ai-infra-bearblog]], [[Skill System Manifesto - 2026-02-19]], [[Article - Building Your Personal AI Jarvis A 5-Layer Architecture for Individual Sovereign]]

## 5-Layer Pyramid (PAI Architecture)
The 5-Layer Pyramid is a bottom-up, loosely coupled architectural framework for building a Personal AI Infrastructure. It consists of: 1) **Dev Tools** (CLI-first interface like Claude Code), 2) **Data** (local-first knowledge substrate like Obsidian), 3) **Skills** (reusable, codified workflow units), 4) **Scenarios** (automated daily tasks like content curation), and 5) **Review** (meta-cognitive oversight for system evolution). This structure ensures each layer is independently optimizable and swappable, preventing vendor lock-in and allowing the system to evolve sustainably over time. It's a blueprint for turning ad-hoc AI use into durable, personal infrastructure.
Appears in: [[personal-ai-infra-bearblog]], [[Skill System Manifesto - 2026-02-19]], [[Article - Building Your Personal AI Jarvis A 5-Layer Architecture for Individual Sovereign]]

## Inverse Problem (Life Decision Analogy)
The inverse problem, as applied to life decisions, is the practice of starting with a desired outcome (**b**) and reverse-engineering the sequence of choices or inputs (**x**) that would produce it, rather than the trivial "forward problem" of calculating outcomes from given inputs. This framing highlights why hard choices feel difficult: they mirror the mathematical pathologies of inverse problems, including non-existent solutions, infinitely many solutions (underdetermined systems), and ill-conditioning (small shifts in desired outcomes leading to completely different required inputs). The analogy draws directly from linear algebra, where the inverse problem is defined as finding **x** given **A** and **b = Ax**.
Appears in: [[inverse-problems-life-decisions]], [[Essay - inverse problems]], [[Flashcards - Essay - inverse problems]], [[Concept Digest - 2026-02-19]]

## Regularization (Decision Strategy)
Regularization is a mathematical technique for making ill-posed inverse problems solvable by adding constraints that prioritize stable, simple solutions—most famously Tikhonov regularization, which balances closeness to the desired outcome with simplicity. For life decisions, this translates to adding practical constraints like a simplicity bias (favoring paths with fewer moving parts), a "do no harm" rule (avoiding choices that close off future options), and values checks (ensuring solutions align with core desires). These constraints do not make the problem easier, but they make it *actable* by cutting through analysis paralysis and punishing imprecision in what we actually want.
Appears in: [[inverse-problems-life-decisions]], [[Essay - inverse problems]], [[Concept Digest - 2026-02-19]]

## Skills (AI Agent Workflow Units)
In the context of a Personal AI Infrastructure, a skill is a reusable, codified unit of work—distinct from a one-off prompt—that packages prompts, scripts, and APIs into a composable workflow. Skills follow a "Small File Philosophy," doing one thing well and gaining power through composition. They are the building blocks of the infrastructure, extracted from repetition: every time you solve a problem with AI twice, you turn it into a skill. This practice transforms transient solutions into permanent, scriptable infrastructure, reducing cognitive load and token burn by handling deterministic tasks with code and reserving AI for judgment and creativity.
Appears in: [[Skill System Manifesto - 2026-02-19]], [[Skills Digest - 2026-02-20]], [[Skills Digest - 2026-02-19]], [[AI Brief - 2026-02-20]]

## Context as Moat
"Context as the moat" is the principle that accumulated personal context—your writing style, preferences, projects, and information diet—is what transforms a generic, interchangeable LLM into a truly personal assistant. This context, built gradually in a machine-readable format (like an Obsidian "LLM Context" directory), becomes your competitive advantage and system's defensible value. It ensures your AI infrastructure works uniquely for you, as the model itself is a commodity. The moat isn't the AI model you use, but the rich, curated self-model you feed it.
Appears in: [[personal-ai-infra-bearblog]], [[Skill System Manifesto - 2026-02-19]], [[Article - Building Your Personal AI Jarvis A 5-Layer Architecture for Individual Sovereign]]

## Loose Coupling
Loose coupling is a core design principle for sustainable systems, especially in Personal AI Infrastructure. It means designing each layer or component (like the data layer or skills layer) to be independently optimizable and swappable without breaking the entire system. For example, the skills layer shouldn't care if the data layer moves from Obsidian to Logseq. This architecture embraces change as inevitable and prevents vendor lock-in, ensuring the system can evolve with new tools and technologies over the long term without requiring a full rebuild.
Appears in: [[Skill System Manifesto - 2026-02-19]], [[personal-ai-infra-bearblog]], [[Article - Building Your Personal AI Jarvis A 5-Layer Architecture for Individual Sovereign]]

## Scripts Before Prompts
"Scripts before prompts" is a practical heuristic for efficient AI infrastructure: if a task can be codified deterministically with traditional code (Python for API calls, file manipulation, data parsing), it should be a script, not a prompt. Use AI only for what requires judgment, creativity, or handling ambiguity. This dual-strategy pattern—Python for fetch/filter, AI for summarize/judge—conserves tokens, increases reliability, and makes workflows faster and more reproducible. It recognizes that burning LLM context on mechanical tasks is an inefficient use of both money and system capability.
Appears in: [[Skill System Manifesto - 2026-02-19]], [[Article - Building Your Personal AI Jarvis A 5-Layer Architecture for Individual Sovereign]]

---

## Notes Scanned

- [[Reddit Digest - 2026-02-20]] (Sources)
- [[Alpha Vantage Digest - 2026-02-20]] (Sources)
- [[ArXiv Digest - 2026-02-20]] (Sources)
- [[Skills Digest - 2026-02-20]] (Sources)
- [[Vault Analytics - Simple]] (Sources)
- [[HN Newsletter - 2026-02-20]] (Sources)
- [[AI Brief - 2026-02-20]] (Sources)
- [[personal-ai-infra-bearblog]] (Inbox)
- [[Skill System Manifesto - 2026-02-19]] (Sources)
- [[Concept Digest - 2026-02-19]] (Sources)
- [[Vault Analytics - 2026-02-19]] (Sources)
- [[Podcast Digest - 2026-02-19]] (Sources)
- [[Skill Package Analysis - 2026-02-19]] (Sources)
- [[GitHub Digest - 2026-02-19]] (Sources)
- [[Job Digest - 2026-02-19]] (Sources)
- [[Alpha Vantage Digest - 2026-02-19]] (Sources)
- [[Knowledge Graph - 2026-02-19]] (Sources)
- [[Agent News Digest - 2026-02-19]] (Sources)
- [[Skills Digest - 2026-02-19]] (Sources)
- [[Crypto Market Digest - 2026-02-19]] (Sources)
- [[Flashcards - Essay - inverse problems]] (Sources)
- [[Link Analyzer Report - 2026-02-19]] (Sources)
- [[Memory - 05:45 - 2026-02-19]] (Inbox)
- [[Bilibili - 人大教授聂辉华绝大多数中国人压根不懂权力怎么运作]] (Sources)
- [[Movie - Goodfellas]] (Sources)
- [[YT - The OFFICIAL Notion Second Brain Setup]] (Sources)
- [[Skills Digest - 2026-02-18]] (Sources)
- [[Article - Building Your Personal AI Jarvis A 5-Layer Architecture for Individual Sovereign]] (Sources)
- [[Movie - Guardians of the Galaxy Vol. 2]] (Sources)
- [[inverse-problems-life-decisions]] (Inbox)
- ... and 19 more
