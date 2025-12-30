"""
Spirit Animal API Server

FastAPI backend for the Spirit Animal generator app.
"""

import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# Import our modules
from fetchers import fetch_all
from llm import generate_spirit_animal, generate_spirit_animal_v2


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup: verify OpenAI key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set. Set it in .env file.")
    else:
        print("✅ OpenAI API key configured")

    # Check optional social API keys
    if os.getenv("TWITTER_BEARER_TOKEN"):
        print("✅ Twitter API configured")
    else:
        print("ℹ️  Twitter API not configured (optional)")

    yield

    # Shutdown
    print("Shutting down Spirit Animal API...")


app = FastAPI(
    title="Spirit Animal API",
    description="Discover your spirit animal based on your personality and social presence",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration - restrict to known frontend origins
ALLOWED_ORIGINS = [
    "http://localhost:5173",      # Vite dev server
    "http://localhost:3000",      # Alternative dev port
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

# Add production domain from environment if set
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    ALLOWED_ORIGINS.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


# Request/Response models
class SocialHandle(BaseModel):
    platform: str
    handle: str


class SpiritRequest(BaseModel):
    name: str
    interests: str = ""
    values: str = ""
    socialHandles: list[SocialHandle] = []
    image_provider: str = "gemini"


class SpiritResponse(BaseModel):
    personality_summary: str
    spirit_animal: str
    animal_reasoning: str
    art_medium: str
    medium_reasoning: str
    image_url: str
    image_provider: str


# V2 Request/Response models (Tambo conversational onboarding)
class SpiritRequestV2(BaseModel):
    """
    V2 Request schema for Tambo conversational onboarding flow.
    
    The frontend assembles a rich personality summary from the 7-turn
    conversation and sends it with structured metadata.
    """
    # The rich personality summary assembled by Tambo frontend
    personality_summary: str
    
    # Structured metadata from conversation choices
    pronouns: str = "unspecified"  # "he/him", "she/her", "they/them", "unspecified"
    energy_mode: str | None = None  # "leader", "adapter", "observer"
    social_pattern: str | None = None  # "solitude", "close_circle", "crowd"
    element_affinity: str | None = None  # "fire", "water", "earth", "air"
    
    # Image generation options
    image_provider: str = "gemini"  # "gemini" (default), "openai", "ideogram", "none"
    skip_image: bool = False  # For testing interpretation without image gen


class SpiritResponseV2(BaseModel):
    """V2 Response with additional image_prompt field."""
    personality_summary: str
    spirit_animal: str
    animal_reasoning: str
    art_medium: str
    medium_reasoning: str
    image_prompt: str
    image_url: str | None
    image_provider: str


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "Spirit Animal API is running"}


@app.post("/api/spirit-animal", response_model=SpiritResponse)
async def get_spirit_animal(req: SpiritRequest):
    """
    Generate a spirit animal based on user input and social media data.

    This endpoint:
    1. Fetches public social media data (if handles provided)
    2. Analyzes personality using LLM
    3. Determines spirit animal and art style
    4. Generates a unique image
    """
    try:
        # Fetch social media data in parallel
        social_handles = [{"platform": sh.platform, "handle": sh.handle}
                         for sh in req.socialHandles if sh.handle.strip()]

        social_data = await fetch_all(social_handles) if social_handles else []

        # Prepare form data
        form_data = {
            "name": req.name,
            "interests": req.interests,
            "values": req.values,
        }

        # Run the LLM pipeline
        result = await generate_spirit_animal(form_data, social_data, req.image_provider)

        return SpiritResponse(**result)

    except Exception as e:
        print(f"Error generating spirit animal: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate spirit animal: {str(e)}"
        )


@app.get("/api/health")
async def health_check():
    """Detailed health check with API status."""
    return {
        "status": "healthy",
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "twitter_configured": bool(os.getenv("TWITTER_BEARER_TOKEN")),
        "gemini_configured": bool(os.getenv("GEMINI_API_KEY")),
        "ideogram_configured": bool(os.getenv("IDEOGRAM_API_KEY")),
    }


@app.post("/api/spirit-animal/v2", response_model=SpiritResponseV2)
async def get_spirit_animal_v2(req: SpiritRequestV2):
    """
    V2 Endpoint: Generate spirit animal from Tambo conversational onboarding.
    
    This endpoint is designed for the Tambo-powered frontend flow:
    1. Frontend gathers personality via 7-turn conversation
    2. Frontend assembles rich personality summary
    3. Backend interprets → spirit animal + artistic medium
    4. Backend generates image (optional)
    
    The v2 flow skips the old personality summarization step since the
    Tambo conversation already captured rich personality signals.
    """
    try:
        result = await generate_spirit_animal_v2(
            personality_summary=req.personality_summary,
            pronouns=req.pronouns,
            energy_mode=req.energy_mode,
            social_pattern=req.social_pattern,
            element_affinity=req.element_affinity,
            image_provider=req.image_provider,
            skip_image=req.skip_image,
        )
        
        return SpiritResponseV2(**result)
    
    except Exception as e:
        print(f"Error in v2 spirit animal generation: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate spirit animal: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
