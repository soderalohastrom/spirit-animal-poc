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
from llm import generate_spirit_animal


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

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    image_provider: str = "openai"


class SpiritResponse(BaseModel):
    personality_summary: str
    spirit_animal: str
    animal_reasoning: str
    art_medium: str
    medium_reasoning: str
    image_url: str
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
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
