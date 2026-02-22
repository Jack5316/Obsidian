"""WeChat Moments Copywriting Generator - Create engaging WeChat Moments (朋友圈) posts with hackable templates.

Provides multiple pre-built templates for different scenarios (daily life, insights, work, etc.) that can be customized quickly.
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

# Add parent for config
sys.path.insert(0, str(Path(__file__).parent))
from config import summarize, save_note, VAULT_PATH

# Hackable templates - users can modify these directly
TEMPLATES = {
    "daily": {
        "name": "Daily Life",
        "description": "Everyday moments with a touch of warmth",
        "prompt": """You are a WeChat Moments copywriter. Create a warm, relatable daily life post.

**Requirements:**
- 2-4 sentences, conversational tone
- Include a small detail that makes it authentic (coffee, weather, a moment)
- Positive but not overly dramatic
- End with a gentle question or reflection to encourage engagement
- No hashtags unless natural
- Use emojis sparingly (1-3 max)

**Example structure:**
[Small observation] + [Personal feeling] + [Gentle question/reflection]

Generate only the copy, no explanations.
"""
    },
    "insight": {
        "name": "Thought/Insight",
        "description": "Share a realization or learning",
        "prompt": """You are a WeChat Moments copywriter. Create an insightful post sharing a realization.

**Requirements:**
- Start with a hook (contrarian take, surprising fact, or simple observation)
- Explain the insight clearly in 2-3 sentences
- Connect it to daily life (make it relatable)
- End with a takeaway or actionable thought
- Use emojis sparingly
- Keep it authentic, not preachy

Generate only the copy, no explanations.
"""
    },
    "gratitude": {
        "name": "Gratitude",
        "description": "Appreciate someone or something",
        "prompt": """You are a WeChat Moments copywriter. Create a sincere gratitude post.

**Requirements:**
- Specific, not generic (name the person/thing, what they did)
- Heartfelt but not overly sentimental
- Focus on the impact they had on you
- Keep it concise (2-3 sentences)
- Use warm emojis
- Privacy-friendly (avoid oversharing personal details without consent)

Generate only the copy, no explanations.
"""
    },
    "work": {
        "name": "Work Progress",
        "description": "Share work milestones without boasting",
        "prompt": """You are a WeChat Moments copywriter. Create a tasteful work update.

**Requirements:**
- Humble and authentic, not braggy
- Focus on the journey/learning, not just the outcome
- Thank others if applicable
- Keep it low-key
- 2-3 sentences
- Avoid jargon
- Use a simple emoji

Generate only the copy, no explanations.
"""
    },
    "book": {
        "name": "Book/Media",
        "description": "Share what you're reading/watching",
        "prompt": """You are a WeChat Moments copywriter. Create an engaging book/media post.

**Requirements:**
- Name the work (title, author if book)
- Share one specific insight or quote that resonated
- Explain why it matters to you personally
- Keep it concise (2-3 sentences)
- Recommend gently, not pushy
- End with a question to encourage conversation

Generate only the copy, no explanations.
"""
    },
    "photo": {
        "name": "Photo Caption",
        "description": "Short, evocative caption for photos",
        "prompt": """You are a WeChat Moments copywriter. Create a photo caption.

**Requirements:**
- Short and poetic (1-2 sentences or a phrase)
- Evocative, not literal
- Leaves room for imagination
- Can be slightly ambiguous in a beautiful way
- Use emojis that match the mood
- No explanations needed

Generate only the caption, no explanations.
"""
    },
    "weekend": {
        "name": "Weekend Vibe",
        "description": "Relaxed weekend mood",
        "prompt": """You are a WeChat Moments copywriter. Create a relaxed weekend post.

**Requirements:**
- Slow, peaceful vibe
- Specific small pleasures (coffee, sunlight, reading, walk)
- No need to be productive
- Warm and content tone
- 2-3 sentences
- Use cozy emojis

Generate only the copy, no explanations.
"""
    },
    "question": {
        "name": "Question/Poll",
        "description": "Engage friends with a question",
        "prompt": """You are a WeChat Moments copywriter. Create an engaging question post.

**Requirements:**
- Genuine question you actually wonder about
- Relatable to many people
- Not too personal or controversial
- Explains why you're asking (brief context)
- Invites answers in comments
- 2-3 sentences
- Friendly and open tone

Generate only the copy, no explanations.
"""
    }
}


def list_templates():
    """List all available templates."""
    result = "📝 Available WeChat Moments Templates:\n\n"
    for key, template in TEMPLATES.items():
        result += f"  {key:12} - {template['name']}: {template['description']}\n"
    return result


def generate_copy(template_key: str, topic: str = None) -> str:
    """Generate copy using specified template."""
    template = TEMPLATES.get(template_key)
    if not template:
        raise ValueError(f"Unknown template: {template_key}")
    
    prompt = template["prompt"]
    
    if topic:
        prompt += f"\n\n**Topic:** The user wants to post about: \"{topic}\". Incorporate this theme naturally."
    
    user_content = f"Generate a WeChat Moments post using the {template['name']} template."
    if topic:
        user_content += f" Topic: {topic}"
    
    return summarize(user_content, prompt)


def main():
    """Main function for the WeChat Moments skill."""
    parser = argparse.ArgumentParser(
        description="WeChat Moments Copywriting Generator - Create engaging 朋友圈 posts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  /skill pyq                          # List all templates
  /skill pyq --template daily         # Generate daily life post
  /skill pyq -t insight --topic "AI"  # Generate insight about AI
  /skill pyq --save                   # Save output to vault
"""
    )
    
    parser.add_argument(
        "-t", "--template",
        type=str,
        default=None,
        help="Template to use (use without --template to list all)",
    )
    
    parser.add_argument(
        "--topic",
        type=str,
        default=None,
        help="Topic or theme for the post",
    )
    
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available templates",
    )
    
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save output to vault",
    )
    
    args = parser.parse_args()
    
    # List templates if requested or no template specified
    if args.list or not args.template:
        print(list_templates())
        return
    
    # Generate copy
    try:
        print(f"Generating {TEMPLATES[args.template]['name']} post...")
        copy = generate_copy(args.template, args.topic)
        
        result = f"""# 朋友圈文案 - {TEMPLATES[args.template]['name']}

{copy}

---
Template: {args.template}
Topic: {args.topic or 'None'}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        print("\n" + "="*50)
        print("Generated Copy:")
        print("="*50)
        print(copy)
        print("="*50 + "\n")
        
        if args.save:
            date_str = datetime.now().strftime("%Y-%m-%d")
            safe_topic = args.topic.replace(" ", "_")[:30] if args.topic else args.template
            save_note(f"Sources/WeChat Moments - {safe_topic} - {date_str}.md", result)
            print(f"Saved to Sources/WeChat Moments - {safe_topic} - {date_str}.md")
        
    except KeyError:
        print(f"Error: Template '{args.template}' not found.")
        print("\nAvailable templates:")
        print(list_templates())
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
