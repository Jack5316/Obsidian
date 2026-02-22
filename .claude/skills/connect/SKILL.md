---
name: connect
description: Find and surface relationships between notes, ideas, and concepts across the knowledge base. Use when asked to connect, link, or find relationships between notes/ideas, or /connect.
---

# Connect Skill

Find and surface relationships between notes, ideas, and concepts across your Obsidian vault. Prioritizes surprising links over obvious ones. Use before writing essays or weekly reviews.

## Trigger

When asked to connect, link, or find relationships between notes/ideas.

## Process

1. **Identify the seed** — Note or concept to start from (user-provided or infer from context)
2. **Scan for related notes** by:
   - Shared concepts and recurring terms
   - Recurring names (people, projects)
   - Contradictions or opposing views
   - Cause-effect chains
   - Chronological threads
3. **Map connections** with a brief reason for each link
4. **Surface unexpected or non-obvious links** — prioritize these
5. **Suggest a synthesis note** if 3+ notes converge

## Output Format

```markdown
**Seed:** [[note-name]] or concept

**Direct connections:**
- [[note-a]] — shared concept: X
- [[note-b]] — contradicts on: Y

**Weak/unexpected connections:**
- [[note-c]] — tangentially related via Z

**Synthesis opportunity:** [optional — what these together suggest]
```

## Notes

- Prioritize surprising links over obvious ones
- Flag if a concept appears frequently but has no dedicated note yet
- Use this before writing essays or weekly reviews

## MOC Generation

If 5+ notes connect around a single concept, output a MOC note at `Maps/[Concept] MOC.md`:

```markdown
# [[Concept MOC]]

## Notes
- [[note-a]]
- [[note-b]]

## Patterns
[what they share]

## Open questions
[what's still unresolved]
```

## How to Execute

1. Use semantic search and grep to find notes mentioning the seed concept
2. Read candidate notes to verify relationships and discover non-obvious links
3. Check `Atlas/`, `Sources/`, `Maps/`, and `00 - Inbox/` for relevant content
4. Use exact Obsidian note titles (without .md) for [[wikilinks]]
