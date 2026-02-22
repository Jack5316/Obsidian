# Flomo Skill Analysis: Is it Worth Building?

## Overview

This analysis evaluates whether creating a flomo integration skill would be valuable for your personal AI infrastructure.

## What is flomo?

Flomo is a "floating notes" application designed for quick capture of ideas and thoughts. It emphasizes:
- Minimalist note-taking
- Quick capture via multiple channels (API, URL Scheme, WeChat, etc.)
- Tag-based organization
- Review and reflection features

## Your Current Workflow Analysis

### Existing Capture Methods

Your vault already has multiple capture mechanisms:

1. **/mem skill** ([`mem_capture.py`](_scripts/mem_capture.py))
   - Quick memory capture to `00 - Inbox/`
   - Timestamped notes with frontmatter
   - Supports custom titles and destinations

2. **/til skill** ([`til_capture.py`](_scripts/til_capture.py))
   - "Today I Learned" capture
   - Knowledge-focused notes

3. **/question skill** ([`question_capture.py`](_scripts/question_capture.py))
   - Question capture for later exploration

4. **Direct Obsidian editing**
   - Full-featured note editing

## Flomo API Capabilities

From the documentation, flomo provides:

1. **Incoming Webhook API** (POST only)
   - Send notes to flomo via HTTP POST
   - Format: `https://flomoapp.com/iwh/yoursecretkey/`
   - Content-type: `application/json`
   - Supports tags in content (e.g., `#tag`)

2. **URL Scheme**
   - `flomo://create` - Open flomo and pre-fill content
   - Useful for mobile/desktop integration

## Direction: Obsidian ← Flomo vs Obsidian → Flomo

The critical question is **direction of integration**:

### Option 1: Obsidian → Flomo (Push to flomo)

**What it would do:**
- Send notes from your vault to flomo
- Could be used for "flomo-only" ideas you want to keep separate

**Value Assessment: LOW**
- You already use Obsidian as your primary knowledge base
- Pushing to flomo would create information silos
- Redundant with your existing capture methods

### Option 2: Flomo → Obsidian (Pull from flomo)

**What it would do:**
- Import notes from flomo into your Obsidian vault
- Sync flomo captures to your `00 - Inbox/`
- Process and organize flomo notes within your existing system

**Value Assessment: MEDIUM-HIGH**
- Leverages flomo's excellent mobile capture experience
- Keeps your Obsidian vault as the single source of truth
- Could complement your workflow if you use flomo heavily on mobile

## Skill Design Options

### Option A: Flomo Capture Skill (Send to flomo)

```bash
python3 _scripts/flomo_send.py "Note content" --tag "idea"
```

**Pros:**
- Simple to implement
- Quick way to send things to flomo

**Cons:**
- Creates silo outside Obsidian
- Duplicates your existing /mem functionality
- You'd need to check two places for notes

### Option B: Flomo Import Skill (Pull from flomo)

```bash
python3 _scripts/flomo_import.py --since "2026-02-01"
```

**Pros:**
- Obsidian remains single source of truth
- Could import from flomo's mobile captures
- Integrates with your existing organization system

**Cons:**
- Requires flomo PRO (API access)
- flomo's API appears to be POST-only (no read API visible)
- Would need investigation into flomo's export capabilities

### Option C: Hybrid - Dual Capture

Create a skill that captures to **both** flomo and Obsidian simultaneously.

**Pros:**
- Best of both worlds
- Notes in both systems

**Cons:**
- Duplication
- Complexity
- Which one is canonical?

## Recommendation: NOT Worth Building Right Now

### Why?

1. **Your /mem skill already solves the quick capture problem**
   - [`mem_capture.py`](_scripts/mem_capture.py) is elegant and simple
   - Captures directly to Obsidian where you process notes
   - No silos, no sync issues

2. **flomo adds unnecessary complexity**
   - Another tool to manage
   - Potential information silos
   - API requires PRO subscription

3. **Direction mismatch**
   - flomo is good for quick capture, but you already have that
   - No clear read API to pull from flomo into Obsidian
   - Pushing to flomo would be counterproductive to your unified workflow

## Counterpoint: If You Use flomo Heavily on Mobile

**If** you currently use flomo as your primary mobile capture tool and want to integrate those notes into Obsidian, then **Option B (Import)** might be worth exploring. But this would require:

1. Investigating flomo's export capabilities
2. Building an import script that processes flomo exports
3. Potentially manual export/import workflow

## Alternative: Enhance Your Existing Capture Skills

Instead of building flomo integration, consider enhancing what you already have:

1. **Improve /mem skill**
   - Add better tagging support
   - Quick templates for different capture types

2. **Create better mobile capture for Obsidian**
   - Use Obsidian's own mobile app
   - Explore iOS Shortcuts / Android Tasker integrations
   - Consider voice-to-text capture enhancements

3. **Universal capture endpoint**
   - Create your own webhook endpoint that feeds directly into Obsidian
   - No middleman (flomo) needed

## Conclusion

**Building a flomo skill is not recommended at this time.**

Your current personal AI infrastructure already has excellent capture mechanisms via the `/mem` skill and Obsidian's native capabilities. Adding flomo would introduce unnecessary complexity without clear benefits.

If you're looking to improve your capture workflow, focus on enhancing your existing tools rather than adding new ones.

**If you still want to explore flomo integration despite this assessment, let me know and I can help design it.**
