---
name: personalization
description: Build and manage your self-model in the digital world - remembers preferences, avoids dislikes, and personalizes interactions (e.g., "I don't like crypto noise").
---

# Personalization Skill

Builds and maintains your digital self-model by tracking preferences, dislikes, interaction patterns, and personal boundaries. Enables personalized, context-aware conversations that respect your stated preferences over time.

## Core Capabilities

1. **Preference Tracking** - Remember what you like and dislike
2. **Content Filtering** - Automatically avoid topics you don't want (e.g., crypto noise)
3. **Interaction Personalization** - Adapt conversation style, depth, and focus
4. **Context Memory** - Recall past preferences in future conversations
5. **Self-Model Evolution** - Update the digital model as your preferences change

## Preference Categories

### Content Preferences
- **Topics to avoid**: Crypto noise, specific subjects, certain types of content
- **Topics of interest**: Favorite subjects, areas you want to explore
- **Content format**: Long-form, concise, technical, casual, etc.
- **Information sources**: Preferred publications, authors, domains

### Interaction Style
- **Tone**: Formal, casual, humorous, analytical, etc.
- **Detail level**: High-level summaries vs. deep technical dives
- **Communication style**: Direct, diplomatic, Socratic, etc.
- **Response length**: Short answers vs. comprehensive explanations

### Personal Boundaries
- **Sensitive topics**: Areas to approach carefully or avoid
- **Time considerations**: Best times for certain types of conversations
- **Cognitive load**: How much information to process at once
- **Privacy preferences**: What to remember vs. what to forget

## Usage Pattern

### When a Preference is Stated:
1. **Acknowledge** - Confirm understanding of the preference
2. **Record** - Update the self-model (in conversation context and files)
3. **Apply immediately** - Start respecting the preference right away
4. **Reference in future** - Recall and apply in subsequent conversations

### Examples of Preferences to Track:
```
"I don't like crypto noise"
→ Avoid cryptocurrency-related content, market updates, trading discussions

"I prefer concise summaries"
→ Keep responses focused, avoid unnecessary detail

"I'm interested in AI safety research"
→ Prioritize and proactively share AI safety content

"I find technical jargon overwhelming"
→ Explain concepts in plain language, define terms when necessary
```

## Self-Model Storage

The digital self-model is maintained in:

- **`LLM Context/Preferences/`** - Stated preferences and boundaries
- **`LLM Context/Personal Profile/`** - Core identity and values
- **`LLM Context/Writing Style/`** - Communication preferences
- **Conversation context** - Recent interactions and stated preferences

## Active Preference: Crypto Noise Avoidance

Currently tracked preference:
> "I don't like crypto noise"

**Implementation**:
- Avoid cryptocurrency market updates
- Skip crypto-related news and discussions
- Filter out NFT, blockchain, DeFi, Web3 content unless explicitly requested
- Focus on non-crypto topics when curating content
- If crypto must be mentioned, frame it minimally and contextually

## How to Update Preferences

Simply state your preferences naturally in conversation:
- "I'd prefer if we don't discuss X"
- "I'm really interested in learning more about Y"
- "Can you explain things in simpler terms?"
- "I prefer detailed technical explanations"

The personalization system will automatically track and apply these preferences.

## Checkpoints

- ✅ **Remembered**: User doesn't like crypto noise
- ⏳ **Waiting for**: Additional preferences to track
- 🔄 **Updates**: Will evolve the self-model as new preferences are stated
