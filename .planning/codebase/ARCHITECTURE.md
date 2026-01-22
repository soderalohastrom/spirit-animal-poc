# Architecture

**Analysis Date:** 2026-01-21

## Pattern Overview

**Overall:** Dual-mode full-stack application with conversational AI-driven frontend and multi-step LLM pipeline backend.

**Key Characteristics:**
- Mode-switchable frontend: Conversational chat (Tambo-powered) and traditional form-based flows
- Layered backend: Data fetching → personality synthesis → LLM interpretation → image generation
- Stateless REST API with async processing
- Rich personality context passed between layers

## Layers

**Frontend (React + Vite):**
- Purpose: Collect user personality data, display results, manage app modes
- Location: `spirit-animal-app/src/`
- Contains: React components, hooks, Tambo SDK integration, styling
- Depends on: Tambo SDK, Radix UI, Tailwind CSS
- Used by: End users via web browser

**Tambo Conversational Layer:**
- Purpose: Orchestrate multi-turn conversation flow (7 questions) and map responses to structured data
- Location: `spirit-animal-app/src/lib/tambo.ts`
- Contains: System prompt, tool definitions, response schemas (Zod), component registry
- Depends on: Tambo SDK (@tambo-ai/react), OpenAI (via Tambo), backend API
- Used by: App.tsx and SpiritAnimalChat.tsx

**Chat UI Component:**
- Purpose: Render conversational interface with message history and input field
- Location: `spirit-animal-app/src/components/chat/SpiritAnimalChat.tsx`
- Contains: Message rendering, scroll behavior, loading states, Tambo hooks
- Depends on: Tambo hooks (useTamboThread, useTamboThreadInput), Lucide icons
- Used by: App.tsx in chat mode

**Form UI Components:**
- Purpose: Traditional onboarding flow (name, interests, values, social handles)
- Location: `spirit-animal-app/src/components/OnboardingForm.tsx`
- Contains: Multi-step form with dropdown selectors, social handle management
- Depends on: React hook-form, Zod validation
- Used by: App.tsx in form mode

**Result Display Components:**
- Purpose: Present the generated spirit animal with image and reasoning
- Location: `spirit-animal-app/src/components/SpiritAnimalCard.tsx`, `TamboSpiritAnimalCard.tsx`
- Contains: Image rendering, share/download actions, styling
- Depends on: Lucide icons, native Web APIs (navigator.share, clipboard)
- Used by: App.tsx after successful generation

**Backend API (FastAPI):**
- Purpose: Interpret personality → determine spirit animal → generate image
- Location: `spirit-animal-backend/main.py`
- Contains: REST endpoints, CORS middleware, request/response validation
- Depends on: FastAPI, Pydantic, Python async/await
- Used by: Frontend via HTTP POST

**LLM Pipeline:**
- Purpose: Orchestrate multi-step LLM processing (summarize → interpret → generate image)
- Location: `spirit-animal-backend/llm/pipeline.py`
- Contains: OpenAI client calls, interpretation prompts, image generation with multiple providers
- Depends on: OpenAI SDK, httpx for async requests
- Used by: Backend API endpoints

**Social Data Fetcher:**
- Purpose: Fetch public social media data for V1 flow (optional, form mode)
- Location: `spirit-animal-backend/fetchers/social_fetcher.py`
- Contains: Twitter API integration, data aggregation
- Depends on: Twitter API, httpx
- Used by: V1 endpoint only (legacy)

## Data Flow

**Conversational V2 Flow (Tambo) - Primary:**

1. **User opens app** → `App.tsx` renders with mode toggle (default: chat)
2. **Chat mode selected** → `TamboProvider` initializes with context helpers
3. **User sees welcome message** → Tambo renders initial message: "What's your name?"
4. **User answers Question 1-7** → Tambo calls `generateSpiritAnimal` tool after collecting all data
5. **Tool extracts and structures data** → `tambo.ts` assembles personality summary with hints
6. **POST to `/api/spirit-animal/v2`** with:
   ```
   {
     personality_summary: "Rich narrative profile",
     pronouns: "he/him|she/her|they/them|unspecified",
     energy_mode: "leader|adapter|observer",
     social_pattern: "solitude|close_circle|crowd",
     element_affinity: "fire|water|earth|air",
     image_provider: "gemini|openai|ideogram|none"
   }
   ```
7. **Backend processes** → `generate_spirit_animal_v2()` calls:
   - `interpret_spirit_animal()` with rich system prompt
   - OpenAI interprets personality → spirit animal + art medium
   - Image generation (Gemini by default, configurable)
8. **Response flows back** with:
   ```
   {
     spirit_animal: "Arctic Fox",
     animal_reasoning: "Why...",
     art_medium: "Oil paint with impasto texture",
     medium_reasoning: "Why...",
     image_prompt: "Generated prompt used",
     image_url: "https://..."
   }
   ```
9. **Tambo renders SpiritAnimalCard** component with result
10. **User can share or generate another** → App resets

**Legacy Form Flow (V1) - Fallback:**

1. User switches to "Form" mode
2. OnboardingForm collects: name, interests, values, social handles, image provider
3. POST to `/api/spirit-animal` with form data
4. Backend fetches social data (Twitter, Reddit, etc.) if handles provided
5. Personality synthesized from form + social data
6. Image generated
7. SpiritAnimalCard displays result

**State Management:**

- Frontend: React component state (App.tsx holds mode, appState, result)
- Conversation: Tambo SDK manages thread state and message history
- Backend: Stateless; each request is independent

## Key Abstractions

**TamboProvider + Hooks (Conversation Management):**
- Purpose: Bridge between Tambo AI engine and React UI
- Examples: `useTamboThread`, `useTamboThreadInput` hooks
- Pattern: Tambo manages the LLM conversation; React renders UI; tools call backend

**Personality Summary Assembly:**
- Purpose: Convert 7 conversation answers into rich, coherent text for LLM interpretation
- Examples: `assemblePersonalitySummary()` in `tambo.ts`
- Pattern: Maps enum choices → human-readable text; embeds context hints for spirit animal matching

**Image Generation Abstraction:**
- Purpose: Support multiple image providers with unified interface
- Examples: Gemini, OpenAI (DALL-E 3), Ideogram
- Pattern: Backend determines provider from `image_provider` param; calls appropriate SDK

**Interpretation System Prompt:**
- Purpose: Codify spirit animal matching rules and artistic style mapping
- Examples: `INTERPRETATION_SYSTEM_PROMPT` in `pipeline.py`
- Pattern: LLM-as-judge framework; extensive guidance on animal categories, medium selection, reasoning

**Tool-Based Interaction:**
- Purpose: Allow Tambo LLM to call structured backend operations
- Examples: `generateSpiritAnimal` tool with Zod schema validation
- Pattern: Tools define the interface between LLM and backend; schemas ensure type safety

## Entry Points

**Frontend:**
- Location: `spirit-animal-app/src/main.tsx` → mounts App in DOM
- Triggers: Browser navigates to localhost:5173 or deployed URL
- Responsibilities: Bootstrap React, render App root component

**App Root:**
- Location: `spirit-animal-app/src/App.tsx`
- Triggers: Rendered by main.tsx
- Responsibilities: Manage mode toggle (chat/form), render active flow, handle app state

**Chat Entry:**
- Location: `spirit-animal-app/src/components/chat/SpiritAnimalChat.tsx`
- Triggers: When mode === "chat"
- Responsibilities: Render conversation UI, manage input/submit, call Tambo hooks

**Form Entry:**
- Location: `spirit-animal-app/src/components/OnboardingForm.tsx`
- Triggers: When mode === "form"
- Responsibilities: Collect user input, validate, submit to V1 endpoint

**Backend Entry:**
- Location: `spirit-animal-backend/main.py`
- Triggers: FastAPI server startup (uvicorn)
- Responsibilities: Initialize app, load environment, set up middleware

**API Endpoints:**
- `POST /api/spirit-animal` — V1 form-based flow
- `POST /api/spirit-animal/v2` — V2 conversational flow (Tambo)
- `GET /api/health` — Health check with provider status
- `GET /` — Root health check

## Error Handling

**Strategy:** Try-catch at API level; return 500 HTTPException with detail message.

**Patterns:**
- Frontend: Catch fetch errors, display user-friendly error message, allow retry
- Backend: Log full error to console; return 500 with wrapped error detail
- Tambo: Tool errors bubble up to LLM; LLM can retry or explain to user

**Example (Frontend):**
```typescript
catch (err) {
  console.error("Error:", err);
  setError(err instanceof Error ? err.message : "Something went wrong");
  setAppState("form");
}
```

**Example (Backend):**
```python
except Exception as e:
    print(f"Error generating spirit animal: {e}")
    raise HTTPException(
        status_code=500,
        detail=f"Failed to generate spirit animal: {str(e)}"
    )
```

## Cross-Cutting Concerns

**Logging:**
- Frontend: `console.log` with `[Tambo Tool V2]` prefix for tool calls; `console.error` for failures
- Backend: Print statements for startup/shutdown; error logging on exceptions

**Validation:**
- Frontend: Zod schemas for tool params and component props; React hook-form for form validation
- Backend: Pydantic BaseModel for all request/response models; env var validation at startup

**Authentication:**
- Not implemented; API is open (CORS-restricted to known frontend origins)
- Environment: API keys (OpenAI, Gemini, Twitter, etc.) stored in `.env`, loaded via `dotenv`

**API Versioning:**
- V1: `/api/spirit-animal` — form-based, fetches social data, basic LLM pipeline
- V2: `/api/spirit-animal/v2` — conversational, rich personality context, extended interpretation

**Image Caching:**
- Not implemented; images generated fresh on each request
- Providers: Gemini (default), OpenAI, Ideogram, or skip entirely

---

*Architecture analysis: 2026-01-21*
