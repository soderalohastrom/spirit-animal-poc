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
    "image_prompt": "A detailed, vivid prompt for DALL-E to generate the spirit animal portrait. Include the animal, the art style, mood, colors, and composition. Make it visually striking and unique."
}""",
            },
            {
                "role": "user",
                "content": f"Find the perfect spirit animal for this personality:\n\n{personality_summary}",
            },
        ],
        temperature=0.8,
        max_tokens=500,
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
        response = openai_client.images.generate(
            model="dall-e-3",
            prompt=image_prompt,
            size="1024x1024",
            quality="standard",
            n=1,
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
