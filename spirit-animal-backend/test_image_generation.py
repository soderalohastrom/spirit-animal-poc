#!/usr/bin/env python3
"""
Test Script: Spirit Animal Image Generation
============================================
Phase 2: Test image generation with multiple providers.

Providers:
- OpenAI (DALL-E 3) - Ready to use
- Gemini (Imagen) - Ready to use if GEMINI_API_KEY set
- Ideogram (V2/V3) - Needs credits, but structure ready

Usage:
    cd spirit-animal-backend
    
    # Generate with OpenAI (default)
    python test_image_generation.py
    
    # Generate with specific provider
    python test_image_generation.py --provider openai
    python test_image_generation.py --provider gemini
    python test_image_generation.py --provider ideogram
    
    # Use custom prompt
    python test_image_generation.py --prompt "Your image prompt here..."
    
    # Use interpretation result file
    python test_image_generation.py --from-file test_interpretation_result.json
"""

import os
import sys
import json
import argparse
import base64
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv()


# ============================================================================
# IMAGE GENERATION PROVIDERS
# ============================================================================

def generate_openai(prompt: str, save_path: str) -> dict:
    """
    Generate image using OpenAI DALL-E 3.
    
    Note: DALL-E 3 doesn't support negative prompts, so we bake exclusions
    into the prompt itself.
    """
    from openai import OpenAI
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Add exclusions to prompt (DALL-E doesn't have negative_prompt)
    enhanced_prompt = f"{prompt}. Important: Do not include any text, words, letters, or human faces in the image."
    
    print(f"📤 Sending to DALL-E 3...")
    print(f"   Prompt length: {len(enhanced_prompt)} chars")
    
    response = client.images.generate(
        model="dall-e-3",
        prompt=enhanced_prompt,
        size="1024x1024",
        quality="standard",
        n=1,
        timeout=120.0,
    )
    
    image_url = response.data[0].url
    revised_prompt = response.data[0].revised_prompt
    
    # Download and save the image
    import httpx
    img_response = httpx.get(image_url, timeout=60.0)
    with open(save_path, 'wb') as f:
        f.write(img_response.content)
    
    return {
        "provider": "openai",
        "model": "dall-e-3",
        "image_url": image_url,
        "revised_prompt": revised_prompt,
        "saved_to": save_path
    }


def generate_gemini(prompt: str, save_path: str) -> dict:
    """
    Generate image using Gemini native image generation.
    
    Models:
    - gemini-2.0-flash-preview-image-generation: Fast, efficient (Nano Banana)
    - gemini-2.0-flash-exp: Experimental with image output
    
    Returns base64 image data which we save directly.
    """
    import httpx
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set in environment")
    
    # Gemini native image generation endpoint
    # Available models (Dec 2024):
    # - gemini-2.0-flash-exp-image-generation (experimental)
    # - gemini-2.5-flash-image-preview / gemini-2.5-flash-image
    # - gemini-3-pro-image-preview / nano-banana-pro-preview (same model!)
    model = "gemini-2.0-flash-exp-image-generation"
    endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    
    # Enhanced prompt with exclusions
    enhanced_prompt = f"{prompt}. Do not include any text, words, or human faces."
    
    print(f"📤 Sending to Gemini ({model})...")
    print(f"   Prompt length: {len(enhanced_prompt)} chars")
    
    # Gemini generateContent format
    payload = {
        "contents": [{
            "parts": [{"text": enhanced_prompt}]
        }],
        "generationConfig": {
            "responseModalities": ["TEXT", "IMAGE"]
        }
    }
    
    response = httpx.post(endpoint, json=payload, timeout=120.0)
    
    if response.status_code != 200:
        print(f"   Response status: {response.status_code}")
        print(f"   Response body: {response.text[:500]}")
        response.raise_for_status()
    
    result = response.json()
    
    # Extract base64 image from Gemini response
    if "candidates" in result and len(result["candidates"]) > 0:
        content = result["candidates"][0].get("content", {})
        parts = content.get("parts", [])
        
        for part in parts:
            if "inlineData" in part:
                mime_type = part["inlineData"].get("mimeType", "image/png")
                image_b64 = part["inlineData"]["data"]
                image_bytes = base64.b64decode(image_b64)
                
                with open(save_path, 'wb') as f:
                    f.write(image_bytes)
                
                return {
                    "provider": "gemini",
                    "model": model,
                    "mime_type": mime_type,
                    "image_url": f"data:{mime_type};base64,{image_b64[:50]}...",  # Truncated
                    "saved_to": save_path
                }
        
        # If no image in parts, check for text response (might indicate an error)
        text_parts = [p.get("text", "") for p in parts if "text" in p]
        if text_parts:
            raise ValueError(f"Gemini returned text instead of image: {text_parts[0][:200]}")
    
    raise ValueError(f"No image in Gemini response: {json.dumps(result)[:500]}")


def generate_ideogram(prompt: str, save_path: str, version: str = "v2") -> dict:
    """
    Generate image using Ideogram API.
    
    Supports both V2 and V3 APIs.
    V2: JSON payload with image_request wrapper
    V3: Multipart form data with rendering_speed option
    """
    import httpx
    
    api_key = os.getenv("IDEOGRAM_API_KEY")
    if not api_key:
        raise ValueError("IDEOGRAM_API_KEY not set in environment")
    
    headers = {
        "Api-Key": api_key,
        "Accept": "application/json",
    }
    
    if version == "v2":
        # V2 API
        url = "https://api.ideogram.ai/generate"
        headers["Content-Type"] = "application/json"
        
        payload = {
            "image_request": {
                "model": "V_2",
                "magic_prompt_option": "AUTO",
                "aspect_ratio": "ASPECT_1_1",
                "prompt": prompt,
                "style_type": "GENERAL",
                "negative_prompt": "words, text, letters, human faces, negativity of tone"
            }
        }
        
        print(f"📤 Sending to Ideogram V2...")
        response = httpx.post(url, json=payload, headers=headers, timeout=120.0)
        
    else:
        # V3 API (multipart form)
        url = "https://api.ideogram.ai/v1/ideogram-v3/generate"
        
        print(f"📤 Sending to Ideogram V3...")
        response = httpx.post(
            url,
            headers=headers,
            data={
                "prompt": prompt,
                "rendering_speed": "DEFAULT",  # or "TURBO" for faster
                "aspect_ratio": "1:1",
            },
            timeout=120.0
        )
    
    print(f"   Response status: {response.status_code}")
    
    if response.status_code != 200:
        error_text = response.text
        raise ValueError(f"Ideogram API error ({response.status_code}): {error_text}")
    
    result = response.json()
    
    # Extract image URL
    if "data" in result and len(result["data"]) > 0:
        image_url = result["data"][0]["url"]
    elif "images" in result and len(result["images"]) > 0:
        image_url = result["images"][0]["url"]
    else:
        raise ValueError(f"No image in Ideogram response: {result}")
    
    # Download and save
    img_response = httpx.get(image_url, timeout=60.0)
    with open(save_path, 'wb') as f:
        f.write(img_response.content)
    
    return {
        "provider": "ideogram",
        "model": f"V{'2' if version == 'v2' else '3'}",
        "image_url": image_url,
        "saved_to": save_path
    }


# ============================================================================
# MAIN
# ============================================================================

PROVIDERS = {
    "openai": generate_openai,
    "gemini": generate_gemini,
    "ideogram": generate_ideogram,
}

# Default test prompt (from the elephant interpretation)
DEFAULT_PROMPT = """Create a serene watercolor portrait of an elephant, emphasizing its gentle and wise nature. Use soft washes of grays and gentle blues to convey a calming presence, with fine pen details to accentuate its expressive eyes and textured skin. The elephant should be depicted in a tranquil setting, perhaps under a large, leafy tree, symbolizing community and tranquility. Capture the essence of quiet strength and deep connection, with subtle highlights that suggest the animal's social and introspective qualities. The overall composition should exude warmth and understated wisdom, with an emphasis on the elephant's thoughtful gaze and serene environment, conceptual art"""


def main():
    parser = argparse.ArgumentParser(description="Test spirit animal image generation")
    parser.add_argument("--provider", choices=list(PROVIDERS.keys()), default="openai",
                       help="Image generation provider (default: openai)")
    parser.add_argument("--prompt", type=str, help="Custom image prompt")
    parser.add_argument("--from-file", type=str, help="Load prompt from interpretation result JSON")
    parser.add_argument("--output", type=str, help="Output image path")
    
    args = parser.parse_args()
    
    # Determine prompt
    if args.from_file:
        with open(args.from_file, 'r') as f:
            data = json.load(f)
            prompt = data.get("interpretation", {}).get("imagePrompt", DEFAULT_PROMPT)
            print(f"📂 Loaded prompt from: {args.from_file}")
    elif args.prompt:
        prompt = args.prompt
    else:
        prompt = DEFAULT_PROMPT
        print("📋 Using default test prompt (elephant)")
    
    # Determine output path
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if args.output:
        output_path = args.output
    else:
        output_path = f"test_image_{args.provider}_{timestamp}.png"
    
    print("\n" + "="*60)
    print(f"🖼️  SPIRIT ANIMAL IMAGE GENERATION")
    print("="*60)
    print(f"\n🎯 Provider: {args.provider.upper()}")
    print(f"📝 Prompt preview: {prompt[:100]}...")
    print(f"💾 Output: {output_path}")
    print("-"*60)
    
    try:
        generator = PROVIDERS[args.provider]
        result = generator(prompt, output_path)
        
        print("\n✅ SUCCESS!")
        print("-"*60)
        print(f"   Provider: {result['provider']}")
        print(f"   Model: {result['model']}")
        print(f"   Saved to: {result['saved_to']}")
        if "revised_prompt" in result:
            print(f"\n   📝 Revised prompt (by DALL-E):\n   {result['revised_prompt'][:200]}...")
        print("="*60 + "\n")
        
        # Save metadata
        meta_path = output_path.replace(".png", "_meta.json")
        with open(meta_path, 'w') as f:
            json.dump({
                "prompt": prompt,
                "result": result,
                "timestamp": timestamp
            }, f, indent=2)
        print(f"📋 Metadata saved to: {meta_path}")
        
        return result
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("="*60 + "\n")
        raise


if __name__ == "__main__":
    main()
