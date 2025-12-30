#!/usr/bin/env python3
"""
Test Script: Spirit Animal Interpretation
==========================================
Phase 1: Test the rich interpretation prompt with a personality summary.

This script takes a personality summary and returns:
- Spirit animal recommendation with rationale
- Artistic medium selection with description
- Complete text-to-image prompt

Usage:
    cd spirit-animal-backend
    python test_interpretation.py

Or with custom summary:
    python test_interpretation.py "Your personality summary here..."
"""

import os
import sys
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from parent directory .env
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
# Also try local .env
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ============================================================================
# THE RICH SYSTEM PROMPT (ported from make_spirit_animals.py)
# ============================================================================

INTERPRETATION_SYSTEM_PROMPT = """# Spirit Animal Profile Interpreter

## Purpose and Analysis
Interpret personality summaries to recommend a spirit animal that captures the essence of an individual, creating a text-to-image prompt that reflects their personality through both animal symbolism and artistic style.

## Profile Analysis Framework
Analyze the profile for:
- Key personality traits and emotional energy
- Life approach and core values
- Personal and professional aspirations
- Lifestyle preferences and interests
- Social dynamics and relationship style

## Spirit Animal Categories
Consider these carefully curated groupings based on personality energy:

### Power & Leadership
- Lion (courage, leadership), Wolf (loyalty, pack mentality), Bear (strength, introspection)
- Eagle (vision, freedom), Tiger (willpower, primal power), Stag/Buck (nobility, regeneration)
- Hawk (focus, perspective), Panther (stealth, power), Mountain Lion (leadership, territory)

### Grace & Intuition
- Doe (gentleness, intuition), Swan (grace, transformation), Butterfly (renewal, lightness)
- Cat (independence, mystery), Hummingbird (joy, presence), Dolphin (playfulness, harmony)
- Fox (cunning, adaptability), Crane (balance, grace), Dragonfly (transformation, light)

### Wisdom & Contemplation
- Owl (intuition, wisdom), Elephant (memory, strength), Turtle (patience, ancient knowledge)
- Octopus (intelligence, adaptability), Raven (mystery, transformation), Whale (emotional depths)

### Playful & Social
- Otter (playfulness, curiosity), Monkey (cleverness, social bonds), Penguin (community, resilience)
- Parrot (communication, color), Squirrel (preparation, energy), Rabbit (alertness, abundance)

### Mythological (Use sparingly, when personality warrants)
- Phoenix (rebirth, transformation), Dragon (power, magic), Unicorn (purity, wonder)

### Non-Animal Options (When appropriate)
- Ancient Redwood (longevity, community, quiet strength)
- Northern Star (guidance, constancy)
- Ocean Wave (flow, power, adaptability)
- Oak Tree (strength, stability, deep roots)

## Artistic Medium Selection
Match the artistic medium to the personality:

**Bold/Dynamic Personalities:**
- Oil paint with heavy impasto texture (thick, sculptural strokes)
- Charcoal with dramatic contrast
- Mixed media with metallic leaf accents

**Refined/Sophisticated Personalities:**
- Mixed media with gold leaf and ink
- Art nouveau style with flowing lines
- Detailed pen and ink with watercolor accents

**Gentle/Contemplative Personalities:**
- Soft watercolor washes with fine pen details
- Pastel with delicate blending
- Japanese ink wash (sumi-e) style

**Playful/Creative Personalities:**
- Paper cut-out art with bold colors
- Pop art style with graphic elements
- Whimsical illustration with patterns

**Grounded/Natural Personalities:**
- Earth-toned oil painting
- Woodcut or linocut print style
- Naturalistic botanical illustration style

---

## Example Interpretation

**Input Summary:**
"Sarah is intellectually sharp, values emotional strength, travels frequently, loves live music and cultural experiences."

**Output:**
Spirit Animal: Falcon
Rationale: The falcon represents precision, focus, and noble independence—qualities that align with Sarah's drive and clarity of purpose. The falcon's swift decision-making and graceful power fit someone balancing multiple life roles with precision.

Artistic Medium: Mixed Media with Gold Leaf and Ink
Description: Sharp ink detailing for precision with elegant gold leaf accents representing achievement. Dark blues and deep purples form the base, while dynamic brush strokes capture the falcon's swift nature.

Final Prompt: "Create a striking mixed media portrait of a falcon in flight, combining sharp ink detailing with elegant gold leaf accents. The bird should be rendered with precise lines and dynamic brushstrokes in deep blues and rich purples, embodying both power and grace. Include textural elements that suggest feathers and movement, with the falcon positioned in an upward trajectory against a dramatic sky. The gold leaf should catch light and create points of brilliance, particularly around the wings and eyes, suggesting both achievement and noble spirit. The overall composition should convey precision, focus, and elevated perspective, conceptual art"

---

## Output Format
Respond with a JSON object:

{
  "spiritAnimal": {
    "animal": "Chosen spirit animal",
    "rationale": "2-3 sentences explaining why this animal matches the personality"
  },
  "artisticMedium": {
    "medium": "Chosen artistic medium/style",
    "description": "2-3 sentences describing the artistic approach and color palette"
  },
  "imagePrompt": "The complete text-to-image prompt, ending with ', conceptual art'"
}

IMPORTANT: 
- The imagePrompt must be detailed (100-200 words) and ready for an image generator
- End the imagePrompt with ", conceptual art" (with leading comma)
- Do NOT include human faces or text/words in the image description
- Focus on the ANIMAL in an artistic style, not a person with an animal"""


def interpret_personality(summary: str, verbose: bool = True) -> dict:
    """
    Take a personality summary and return spirit animal interpretation.
    
    Args:
        summary: Text description of personality
        verbose: Print progress messages
        
    Returns:
        Dict with spiritAnimal, artisticMedium, and imagePrompt
    """
    if verbose:
        print("\n" + "="*60)
        print("🔮 SPIRIT ANIMAL INTERPRETATION")
        print("="*60)
        print(f"\n📝 Input Summary:\n{summary}\n")
        print("-"*60)
        print("🤔 Consulting the spirits (GPT-4o)...")
    
    response = client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": INTERPRETATION_SYSTEM_PROMPT},
            {"role": "user", "content": f"Interpret this personality and recommend a spirit animal:\n\n{summary}"}
        ],
        temperature=0.7,
        max_tokens=1000,
        timeout=60.0,
    )
    
    result = json.loads(response.choices[0].message.content)
    
    if verbose:
        print("\n✨ INTERPRETATION COMPLETE!\n")
        print("-"*60)
        print(f"🦊 Spirit Animal: {result['spiritAnimal']['animal']}")
        print(f"\n📖 Rationale:\n{result['spiritAnimal']['rationale']}")
        print("-"*60)
        print(f"🎨 Artistic Medium: {result['artisticMedium']['medium']}")
        print(f"\n📖 Description:\n{result['artisticMedium']['description']}")
        print("-"*60)
        print(f"🖼️  Image Prompt:\n{result['imagePrompt']}")
        print("="*60 + "\n")
    
    return result


# ============================================================================
# TEST DATA
# ============================================================================

TEST_SUMMARY = """I'm a mix of introspective and social. I enjoy quiet time with a good book or a game of chess, but I also value being around people I care about and genuinely enjoy getting to know others. My sense of humor is understated—more dry observations and well-timed comments than big performances. I appreciate simple things done well, like a good meal or an easy weekend with family, and I tend to bring a calm, thoughtful presence into the spaces I'm part of."""


def main():
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found in environment")
        print("   Make sure .env file exists with OPENAI_API_KEY=sk-...")
        sys.exit(1)
    
    # Use command line argument or default test summary
    if len(sys.argv) > 1:
        summary = " ".join(sys.argv[1:])
    else:
        summary = TEST_SUMMARY
        print("📋 Using default test summary (pass your own as argument)")
    
    # Run interpretation
    result = interpret_personality(summary)
    
    # Also save to file for reference
    output_file = "test_interpretation_result.json"
    with open(output_file, 'w') as f:
        json.dump({
            "input_summary": summary,
            "interpretation": result
        }, f, indent=2)
    print(f"💾 Full result saved to: {output_file}")
    
    return result


if __name__ == "__main__":
    main()
