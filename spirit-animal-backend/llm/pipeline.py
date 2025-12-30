"""
LLM pipeline for Spirit Animal generation.

This module orchestrates the multi-step LLM process:
1. Aggregate all user data into raw text
2. Generate personality summary
3. Determine spirit animal + art medium
4. Generate the image
"""

import json
import os

import httpx
from fetchers.social_fetcher import SocialData
from openai import OpenAI

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# ============================================================================
# RICH INTERPRETATION SYSTEM PROMPT (for Tambo v2 flow)
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


# ============================================================================
# ELEMENT AFFINITY → ARTISTIC DIRECTION MAPPINGS
# ============================================================================

ELEMENT_ARTISTIC_HINTS = {
    "fire": {
        "palette": "warm oranges, reds, golds, dramatic lighting",
        "mood": "passionate, transformative, intense, dynamic",
        "medium_affinity": ["oil paint with heavy impasto", "charcoal with dramatic contrast", "mixed media with metallic accents"],
    },
    "water": {
        "palette": "blues, teals, silvers, flowing gradients",
        "mood": "deep, flowing, emotional, serene yet powerful",
        "medium_affinity": ["soft watercolor washes", "Japanese ink wash (sumi-e)", "fluid acrylics"],
    },
    "earth": {
        "palette": "browns, greens, ochre, natural earth tones",
        "mood": "grounded, stable, nurturing, ancient",
        "medium_affinity": ["earth-toned oil painting", "woodcut or linocut print", "naturalistic illustration"],
    },
    "air": {
        "palette": "light blues, whites, lavender, ethereal highlights",
        "mood": "free, light, intellectual, expansive",
        "medium_affinity": ["delicate pen and ink", "pastel with soft blending", "minimalist line art"],
    },
}

ENERGY_MODE_HINTS = {
    "leader": "Power & Leadership animals (Lion, Wolf, Eagle, Tiger, Bear)",
    "adapter": "Grace & Intuition animals (Fox, Dolphin, Cat, Butterfly, Crane)",
    "observer": "Wisdom & Contemplation animals (Owl, Elephant, Whale, Raven, Turtle)",
}

SOCIAL_PATTERN_HINTS = {
    "solitude": "solitary or independent animals",
    "close_circle": "animals known for close family/pack bonds",
    "crowd": "social or community-oriented animals",
}


# ============================================================================
# LEGACY V1 FUNCTIONS (for backwards compatibility)
# ============================================================================

def aggregate_raw_text(form_data: dict, social_data: list[SocialData]) -> str:
    """
    Combine form responses and social media data into a single text block.

    This raw text will be fed to the personality analysis LLM.
    """
    parts = [
        f"Name: {form_data.get('name', 'Anonymous')}",
        "",
        "=== SELF-DESCRIBED INFORMATION ===",
        f"Interests and hobbies: {form_data.get('interests', 'Not provided')}",
        f"Values: {form_data.get('values', 'Not provided')}",
    ]

    if social_data:
        parts.append("")
        parts.append("=== SOCIAL MEDIA DATA ===")

        for sd in social_data:
            parts.append(f"\n--- {sd.platform.upper()} ---")
            if sd.bio:
                parts.append(f"Bio: {sd.bio}")
            if sd.posts:
                parts.append("Recent posts/comments:")
                for i, post in enumerate(sd.posts[:10], 1):
                    # Truncate very long posts
                    truncated = post[:500] + "..." if len(post) > 500 else post
                    parts.append(f"  {i}. {truncated}")

    return "\n".join(parts)


def step1_personality_summary(raw_text: str) -> str:
    """
    LLM Step 1: Analyze the raw text and create a personality summary.

    This summary will be used by the next step to determine the spirit animal.
    """
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": """You are a warm, insightful personality analyst with a gift for
seeing the best in people. Given someone's self-description and social media presence,
create an engaging personality profile.

Your analysis should cover:
- Communication style (formal/casual, witty/sincere, etc.)
- Core interests and passions
- Values and what drives them
- Energy and social orientation (introvert/extrovert spectrum)
- Creative or analytical tendencies
- Sense of humor
- Unique quirks or standout traits

Guidelines:
- Be positive and celebratory - this is for fun!
- Be specific, not generic - find what makes them unique
- Write in second person ("You are..." / "You have...")
- Keep it to 2-3 paragraphs
- Avoid clichés and generic statements""",
            },
            {
                "role": "user",
                "content": f"Please analyze this person's personality:\n\n{raw_text}",
            },
        ],
        temperature=0.7,
        max_tokens=500,
        timeout=60.0,  # 60 second timeout for personality analysis
    )

    return response.choices[0].message.content


def step2_spirit_animal(personality_summary: str) -> dict:
    """
    LLM Step 2: Based on the personality, determine spirit animal and art style.

    Returns a structured response with animal, medium, and reasoning.
    """
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": """You are a creative spirit guide who matches personalities to
their perfect spirit animal and artistic representation.

Based on the personality summary, choose:
1. A SPECIFIC spirit animal (not just "wolf" but "arctic wolf" or "red fox")
2. An art medium/style that captures their essence

Be creative with art styles! Consider:
- Classical: watercolor, oil painting, ink wash, woodcut
- Modern: art nouveau, art deco, pop art, minimalist
- Digital: synthwave, vaporwave, pixel art, low-poly
- Cultural: ukiyo-e, Persian miniature, Aboriginal dot painting
- Whimsical: Studio Ghibli, storybook illustration, papercut

Return JSON in this exact format:
{
    "animal": "specific animal name",
    "animal_reasoning": "2-3 sentences explaining why this animal perfectly represents them",
    "medium": "art style/medium name",
    "medium_reasoning": "2-3 sentences explaining why this style captures their essence",
    "image_prompt": "A detailed, vivid prompt for the OpenAI image model (gpt-image-1) to generate the spirit animal portrait. Include the animal, the art style, mood, colors, and composition. Make it visually striking and unique."
}""",
            },
            {
                "role": "user",
                "content": f"Find the perfect spirit animal for this personality:\n\n{personality_summary}",
            },
        ],
        temperature=0.8,
        max_tokens=500,
        timeout=60.0,  # 60 second timeout for spirit animal determination
    )

    return json.loads(response.choices[0].message.content)


def step3_generate_image(image_prompt: str, provider: str = "openai") -> str:
    """
    Generate the spirit animal image using the specified provider.

    Args:
        image_prompt: The prompt for image generation
        provider: "openai", "ideogram", or "gemini"

    Returns the URL of the generated image.
    """
    if provider == "openai":
        # Add exclusions to prompt (DALL-E doesn't have negative_prompt param)
        enhanced_prompt = f"{image_prompt}. Important: Do not include any text, words, letters, or human faces in the image."
        
        response = openai_client.images.generate(
            model="dall-e-3",
            prompt=enhanced_prompt,
            size="1024x1024",
            quality="standard",
            n=1,
            timeout=120.0,
        )
        return response.data[0].url

    elif provider == "ideogram":
        # Ideogram API integration
        api_key = os.getenv("IDEOGRAM_API_KEY")
        if not api_key:
            raise ValueError("IDEOGRAM_API_KEY not configured")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        data = {"prompt": image_prompt, "style": "realistic", "aspect_ratio": "1:1"}

        response = httpx.post(
            "https://api.ideogram.ai/v1/generate",
            headers=headers,
            json=data,
            timeout=60.0,
        )
        response.raise_for_status()
        result = response.json()
        return result["images"][0]["url"]

    elif provider == "gemini":
        # Gemini 3 Pro Image Preview (Nano Banana) integration
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not configured")

        # Use the correct endpoint and model
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image-preview:generateContent?key={api_key}"

        # Gemini uses generateContent format
        data = {
            "contents": [{"parts": [{"text": image_prompt}]}],
            "generationConfig": {
                "temperature": 0.9,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 8192,
            },
        }

        response = httpx.post(endpoint, json=data, timeout=60.0)
        response.raise_for_status()
        result = response.json()

        # Extract image URL from Gemini response
        if "candidates" in result and len(result["candidates"]) > 0:
            content = result["candidates"][0]["content"]
            if "parts" in content and len(content["parts"]) > 0:
                part = content["parts"][0]
                # Check for inline data (base64 image)
                if "inlineData" in part:
                    mime_type = part["inlineData"]["mimeType"]
                    data = part["inlineData"]["data"]
                    return f"data:{mime_type};base64,{data}"

        raise ValueError("No image generated by Gemini")

    else:
        raise ValueError(f"Unknown image provider: {provider}")


async def generate_spirit_animal(
    form_data: dict, social_data: list[SocialData], image_provider: str = "openai"
) -> dict:
    """
    Main pipeline: orchestrate all steps to generate a spirit animal result.

    Args:
        form_data: Dict with 'name', 'interests', 'values' from the form
        social_data: List of SocialData objects from social fetchers
        image_provider: "openai", "ideogram", or "gemini"

    Returns:
        Complete result dict with personality, animal, reasoning, and image
    """
    # Step 1: Aggregate all text
    raw_text = aggregate_raw_text(form_data, social_data)

    # Step 2: Generate personality summary
    personality = step1_personality_summary(raw_text)

    # Step 3: Determine spirit animal and medium
    spirit = step2_spirit_animal(personality)

    # Step 4: Generate the image
    image_url = step3_generate_image(spirit["image_prompt"], image_provider)

    return {
        "personality_summary": personality,
        "spirit_animal": spirit["animal"],
        "animal_reasoning": spirit["animal_reasoning"],
        "art_medium": spirit["medium"],
        "medium_reasoning": spirit["medium_reasoning"],
        "image_url": image_url,
        "image_provider": image_provider,
    }


# ============================================================================
# V2 FUNCTIONS (Tambo conversational onboarding flow)
# ============================================================================

def _build_interpretation_context(
    personality_summary: str,
    pronouns: str | None = None,
    energy_mode: str | None = None,
    social_pattern: str | None = None,
    element_affinity: str | None = None,
) -> str:
    """
    Build enhanced context for interpretation by appending metadata hints.
    
    The personality_summary from Tambo is already rich. This adds subtle
    guidance from structured choices to help the LLM make better matches.
    """
    context_parts = [personality_summary]
    
    hints = []
    
    if energy_mode and energy_mode in ENERGY_MODE_HINTS:
        hints.append(f"Energy style suggests: {ENERGY_MODE_HINTS[energy_mode]}")
    
    if social_pattern and social_pattern in SOCIAL_PATTERN_HINTS:
        hints.append(f"Social preference suggests: {SOCIAL_PATTERN_HINTS[social_pattern]}")
    
    if element_affinity and element_affinity in ELEMENT_ARTISTIC_HINTS:
        elem = ELEMENT_ARTISTIC_HINTS[element_affinity]
        hints.append(f"Element affinity ({element_affinity}): palette of {elem['palette']}, mood is {elem['mood']}")
    
    if pronouns and pronouns != "unspecified":
        hints.append(f"Pronouns: {pronouns}")
    
    if hints:
        context_parts.append("\n\n--- Additional Context (for interpretation guidance) ---")
        context_parts.extend(hints)
    
    return "\n".join(context_parts)


def interpret_spirit_animal(
    personality_summary: str,
    pronouns: str | None = None,
    energy_mode: str | None = None,
    social_pattern: str | None = None,
    element_affinity: str | None = None,
) -> dict:
    """
    V2 Interpretation: Take a pre-assembled personality summary and return 
    spirit animal interpretation using the rich system prompt.
    
    Args:
        personality_summary: Rich text summary assembled by Tambo frontend
        pronouns: "he/him", "she/her", "they/them", or "unspecified"
        energy_mode: "leader", "adapter", or "observer"
        social_pattern: "solitude", "close_circle", or "crowd"
        element_affinity: "fire", "water", "earth", or "air"
        
    Returns:
        Dict with spiritAnimal, artisticMedium, and imagePrompt
    """
    # Build enhanced context with metadata hints
    enhanced_context = _build_interpretation_context(
        personality_summary=personality_summary,
        pronouns=pronouns,
        energy_mode=energy_mode,
        social_pattern=social_pattern,
        element_affinity=element_affinity,
    )
    
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": INTERPRETATION_SYSTEM_PROMPT},
            {"role": "user", "content": f"Interpret this personality and recommend a spirit animal:\n\n{enhanced_context}"}
        ],
        temperature=0.7,
        max_tokens=1000,
        timeout=60.0,
    )
    
    return json.loads(response.choices[0].message.content)


async def generate_spirit_animal_v2(
    personality_summary: str,
    pronouns: str | None = None,
    energy_mode: str | None = None,
    social_pattern: str | None = None,
    element_affinity: str | None = None,
    image_provider: str = "openai",
    skip_image: bool = False,
) -> dict:
    """
    V2 Pipeline: Generate spirit animal from pre-assembled Tambo summary.
    
    This skips the old aggregation and personality summary steps - the Tambo
    conversational flow has already gathered rich personality data.
    
    Args:
        personality_summary: Rich text summary assembled by Tambo frontend
        pronouns: "he/him", "she/her", "they/them", or "unspecified"
        energy_mode: "leader", "adapter", or "observer" (from Q2)
        social_pattern: "solitude", "close_circle", or "crowd" (from Q3)
        element_affinity: "fire", "water", "earth", or "air" (from Q7)
        image_provider: "openai", "gemini", "ideogram", or "none"
        skip_image: If True, skip image generation (for testing)
        
    Returns:
        Complete result dict with interpretation and image
    """
    # Step 1: Interpret personality → spirit animal + artistic medium
    interpretation = interpret_spirit_animal(
        personality_summary=personality_summary,
        pronouns=pronouns,
        energy_mode=energy_mode,
        social_pattern=social_pattern,
        element_affinity=element_affinity,
    )
    
    # Step 2: Generate image (unless skipped)
    image_url = None
    actual_provider = image_provider
    
    if not skip_image and image_provider != "none":
        image_url = step3_generate_image(interpretation["imagePrompt"], image_provider)
    else:
        actual_provider = "none"
    
    # Build response matching frontend expectations
    return {
        "personality_summary": personality_summary,  # Echo back the input
        "spirit_animal": interpretation["spiritAnimal"]["animal"],
        "animal_reasoning": interpretation["spiritAnimal"]["rationale"],
        "art_medium": interpretation["artisticMedium"]["medium"],
        "medium_reasoning": interpretation["artisticMedium"]["description"],
        "image_prompt": interpretation["imagePrompt"],
        "image_url": image_url,
        "image_provider": actual_provider,
    }
