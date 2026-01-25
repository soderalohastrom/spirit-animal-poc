# External Integrations

**Analysis Date:** 2026-01-21

## APIs & External Services

**Language Models & Image Generation:**

| Service | Purpose | Implementation | Auth |
|---------|---------|-----------------|------|
| **OpenAI API** | GPT-4 text analysis, DALL-E 3 image generation | `openai` Python SDK (v1.50+) | `OPENAI_API_KEY` env var |
| **Google Generative AI (Gemini)** | Image generation with gemini-2.0-flash-exp-image-generation | Direct HTTP via `httpx` | `GEMINI_API_KEY` env var |
| **Ideogram API** | Alternative image generation service | Direct HTTP via `httpx` to `https://api.ideogram.ai/v1/generate` | `IDEOGRAM_API_KEY` (Bearer token) |

**Social Media Data Fetching:**

| Platform | Purpose | Implementation | Auth | Status |
|----------|---------|-----------------|------|--------|
| **Twitter/X API v2** | Fetch public tweets and user bio | `httpx` async client with Bearer token auth | `TWITTER_BEARER_TOKEN` env var | Optional (warned if missing) |
| **Reddit Public API** | Fetch public posts and comments | `httpx` with User-Agent header, no auth required | None | Always available |
| **Bluesky API** | Fetch public posts and profiles | `httpx` to `https://public.api.bsky.app/xrpc/*` endpoints | None | Always available |
| **LinkedIn** | Social data fetching | Not implemented (requires OAuth or paid API) | N/A | Placeholder function |
| **Instagram** | Social data fetching | Not implemented (requires Instagram Graph API) | N/A | Placeholder function |
| **TikTok** | Social data fetching | Not implemented (requires official API access) | N/A | Placeholder function |

**Implementations:**
- `spirit-animal-backend/fetchers/social_fetcher.py` - All social media integrations
- Async pattern: `fetch_all()` runs all fetchers in parallel via `asyncio.gather()`
- Graceful error handling: Failed fetches logged but don't block entire operation

## LLM Pipeline

**Three-Step Processing:**

1. **Step 1 - Personality Summary**
   - Model: `gpt-4o` via OpenAI API
   - Input: User form data + social media posts
   - Output: 2-3 paragraph personality profile
   - Endpoint: `openai_client.chat.completions.create()`
   - Timeout: 60 seconds

2. **Step 2 - Spirit Animal Determination**
   - Model: `gpt-4o` via OpenAI API
   - Response Format: JSON object with structured fields
   - Output Fields:
     - `animal`: Specific spirit animal name
     - `animal_reasoning`: 2-3 sentences explaining choice
     - `medium`: Art style/artistic medium
     - `medium_reasoning`: 2-3 sentences explaining choice
     - `image_prompt`: Detailed text-to-image prompt
   - Endpoint: `openai_client.chat.completions.create()` with `response_format={"type": "json_object"}`
   - Timeout: 60 seconds

3. **Step 3 - Image Generation**
   - Multiple provider options (configurable per request):
     - **OpenAI/DALL-E 3** (model: `dall-e-3`, 1024x1024)
     - **Google Gemini** (model: `gemini-2.0-flash-exp-image-generation`, base64 return)
     - **Ideogram** (POST to `https://api.ideogram.ai/v1/generate`, returns URL)
   - Function: `spirit-animal-backend/llm/pipeline.py::step3_generate_image()`
   - Timeout: 120 seconds for OpenAI/Gemini, 60 for Ideogram

**V2 Flow - Tambo Integration:**
- Personality summary assembled by Tambo frontend conversation (skips Step 1)
- Receives structured metadata from 7-turn conversation:
  - `pronouns`: "he/him", "she/her", "they/them", "unspecified"
  - `energy_mode`: "leader", "adapter", "observer"
  - `social_pattern`: "solitude", "close_circle", "crowd"
  - `element_affinity`: "fire", "water", "earth", "air"
- Endpoint: `spirit-animal-backend/main.py::get_spirit_animal_v2()`

## Frontend AI Integration

**Tambo Conversational AI:**
- Provider: Tambo AI (https://www.tambo.ai/)
- React Provider: `@tambo-ai/react` SDK (v0.68.0)
- Client Library: `@tambo-ai/typescript-sdk` (v0.80.0)
- Implementation: `spirit-animal-app/src/components/chat/`
- Auth: `VITE_TAMBO_API_KEY` environment variable
- Features:
  - 7-turn conversational flow for personality discovery
  - Custom components for UI integration
  - Tool calling for backend API invocation
  - System prompt: `spirit-animal-app/src/lib/tambo/` (SPIRIT_ANIMAL_SYSTEM_PROMPT)
  - Response includes: `components`, `tools`, context helpers

**MCP (Model Context Protocol):**
- SDK: `@modelcontextprotocol/sdk` (v1.25.1)
- Used for extending Claude's capabilities within Tambo

## REST API Endpoints

**Backend: spirit-animal-backend/main.py**

| Endpoint | Method | Version | Purpose | Request Body | Response |
|----------|--------|---------|---------|--------------|----------|
| `/` | GET | V0 | Health check | None | `{"status": "ok", "message": "..."}` |
| `/api/health` | GET | V0 | Detailed health with API status | None | `{"status": "healthy", "openai_configured": bool, ...}` |
| `/api/spirit-animal` | POST | V1 | Traditional form-based flow | `SpiritRequest` | `SpiritResponse` |
| `/api/spirit-animal/v2` | POST | V2 | Tambo conversational flow | `SpiritRequestV2` | `SpiritResponseV2` |

**Request Models:**

`SpiritRequest` (V1):
```typescript
{
  name: string
  interests?: string
  values?: string
  socialHandles?: Array<{platform: string, handle: string}>
  image_provider: string  // "openai", "ideogram", "gemini"
}
```

`SpiritRequestV2` (V2):
```typescript
{
  personality_summary: string  // Rich summary from Tambo
  pronouns?: string
  energy_mode?: string
  social_pattern?: string
  element_affinity?: string
  image_provider?: string
  skip_image?: boolean
}
```

**Response Models:**

`SpiritResponse` (V1):
```typescript
{
  personality_summary: string
  spirit_animal: string
  animal_reasoning: string
  art_medium: string
  medium_reasoning: string
  image_url: string
  image_provider: string
}
```

`SpiritResponseV2` (V2):
```typescript
{
  personality_summary: string
  spirit_animal: string
  animal_reasoning: string
  art_medium: string
  medium_reasoning: string
  image_prompt: string  // Added in V2
  image_url: string | null
  image_provider: string
}
```

**Frontend API Calls:**
- Base URL: `VITE_API_URL` (default: http://localhost:8000)
- Implementation: `spirit-animal-app/src/App.tsx::handleSubmit()` for V1 form endpoint
- V2 flow: Called by Tambo through configured tools

## Data Storage

**No Persistent Database:**
- No SQL or NoSQL database configured
- All processing is stateless and ephemeral
- Results are returned immediately and not persisted
- Form submission → API processing → Response (no storage)

**Session State:**
- Frontend: React component state
- Backend: In-memory during request processing only

## Authentication & Authorization

**API Key Management:**
- All external APIs use environment variable-based keys
- No user authentication system implemented
- No rate limiting or request quotas configured
- CORS configured to allow localhost:5173, localhost:3000, and configurable FRONTEND_URL

**Security Considerations:**
- `.env` files contain sensitive API keys (not committed to git)
- OPENAI_API_KEY, GEMINI_API_KEY, IDEOGRAM_API_KEY, TWITTER_BEARER_TOKEN all stored in `.env`
- VITE_ prefixed variables are safe to expose (used in frontend, only non-sensitive config)
- CORS whitelist prevents cross-origin misuse

## Monitoring & Observability

**Error Handling:**
- Backend: Try-catch blocks with HTTPException (status 500) returns
- Frontend: Error state management with user-facing messages
- Logging: Console.error/print() statements for debugging

**Health Checks:**
- Endpoint: `/api/health` returns configuration status
- Checks: OpenAI, Twitter, Gemini, Ideogram key availability
- Lifespan hooks: Startup verification of OPENAI_API_KEY

**No External Monitoring:**
- No Sentry, LogRocket, DataDog, or similar configured
- No structured logging service
- No error tracking dashboard

## Webhooks & Callbacks

**Incoming Webhooks:**
- None configured
- No webhook endpoints for external services

**Outgoing Webhooks:**
- None configured
- No callbacks to external services after image generation

## Environment Configuration

**Required Variables for Full Functionality:**

Backend (`.env` at root):
```
OPENAI_API_KEY=sk-...              # Required for GPT-4 and DALL-E
GEMINI_API_KEY=AIzaSy...           # Optional, for Gemini images
IDEOGRAM_API_KEY=e_qi...           # Optional, for Ideogram images
TWITTER_BEARER_TOKEN=AAAA...       # Optional, for Twitter data
FRONTEND_URL=https://...           # Optional, for production CORS
```

Frontend (`spirit-animal-app/.env`):
```
VITE_API_URL=http://localhost:8000
VITE_TAMBO_API_KEY=tambo_...
```

**Default Behavior:**
- If optional API key missing: Graceful fallback or warning message
- Image provider defaults to `gemini`
- Twitter API optional (warns if missing, continues without it)

## External Service Status

| Service | Criticality | Fallback | Notes |
|---------|-------------|----------|-------|
| OpenAI API | Critical (V1 flow) | None | V1 flow requires gpt-4o for personality + spirit determination |
| Gemini / DALL-E / Ideogram | High | Alternative providers | At least one needed for image generation; can skip with `skip_image=true` |
| Twitter API | Low | Continue without | Social data optional; form-based input used if unavailable |
| Reddit/Bluesky | Low | Continue without | Used for enrichment if available |

---

*Integration audit: 2026-01-21*
