# SPIRIT ANIMAL POC

**Generated:** 2025-12-28
**Commit:** 680c772
**Branch:** master

## OVERVIEW

Full-stack spirit animal generator: React+Vite frontend, FastAPI backend, OpenAI GPT-4o for personality analysis, DALL-E 3/Gemini for image generation. User submits name + interests + optional social handles → 3-step LLM pipeline → personalized spirit animal portrait.

## STRUCTURE

```
spirit-animal-poc/
├── spirit-animal-app/       # React frontend (Vite, TypeScript, Tailwind, Radix UI)
│   └── src/
│       ├── components/      # OnboardingForm, SpiritAnimalCard, LoadingState, ErrorBoundary
│       ├── hooks/           # use-mobile.tsx
│       └── lib/             # utils.ts (cn helper)
├── spirit-animal-backend/   # FastAPI backend (Python 3.11+)
│   ├── fetchers/            # Social media data fetchers (Twitter, Reddit, Bluesky)
│   └── llm/                 # pipeline.py - 4-step LLM orchestration
└── assets/                  # Static demo files (not used in app)
```

## WHERE TO LOOK

| Task | Location | Notes |
|------|----------|-------|
| Add form field | `spirit-animal-app/src/components/OnboardingForm.tsx` | 3-step wizard, update UserProfile interface |
| Modify LLM prompts | `spirit-animal-backend/llm/pipeline.py` | step1_personality_summary, step2_spirit_animal |
| Add social platform | `spirit-animal-backend/fetchers/social_fetcher.py` | Add to FETCHERS dict |
| Change UI styling | `spirit-animal-app/tailwind.config.js` | Custom colors: primary #2B5D3A, secondary #4A90E2 |
| Add image provider | `spirit-animal-backend/llm/pipeline.py:step3_generate_image` | Add elif branch |
| Modify API response | `spirit-animal-backend/main.py` | Update SpiritResponse Pydantic model |
| Fix CORS | `spirit-animal-backend/main.py:ALLOWED_ORIGINS` | Add production domain |

## CODE MAP

### Backend Entry Points

| Symbol | Type | Location | Role |
|--------|------|----------|------|
| `get_spirit_animal` | Endpoint | `main.py:102` | POST /api/spirit-animal - main entry |
| `generate_spirit_animal` | Function | `llm/pipeline.py:231` | Orchestrates 4-step LLM pipeline |
| `fetch_all` | Function | `fetchers/social_fetcher.py:203` | Parallel social media fetching |
| `SpiritRequest` | Model | `main.py:78` | Request schema (name, interests, values, socialHandles, image_provider) |
| `SpiritResponse` | Model | `main.py:86` | Response schema (personality, animal, reasoning, image_url) |

### LLM Pipeline Flow

```
form_data + social_data
    │
    ▼
aggregate_raw_text() ─────► raw text blob
    │
    ▼
step1_personality_summary() ─► personality profile (GPT-4o, 60s timeout)
    │
    ▼
step2_spirit_animal() ─────► animal + medium + reasoning (GPT-4o JSON, 60s timeout)
    │
    ▼
step3_generate_image() ────► image URL (DALL-E 3 / Ideogram / Gemini, 120s timeout)
```

### Frontend State Machine

```
App.tsx: "form" ──submit──► "loading" ──success──► "result"
                               │                      │
                               └──error──► "form" ◄───┘ (reset)
```

## CONVENTIONS

### Deviations from Standard

- **Path alias**: `@/*` maps to `./src/*` (vite.config.ts + tsconfig.json)
- **pnpm scripts**: All include `pnpm install --prefer-offline` prefix
- **BUILD_MODE**: Set to `prod` for production builds (disables source-identifier plugin)
- **Pydantic v2**: Using v2 syntax (not v1 compat mode)
- **Image providers**: Selectable per-request via `image_provider` field

### Import Order (Frontend)

1. React imports
2. Third-party (lucide-react, etc.)
3. Local components (`@/components/*`)
4. Types/interfaces

### Naming

| Type | Style | Example |
|------|-------|---------|
| Components | PascalCase | `SpiritAnimalCard` |
| Functions | camelCase | `handleSubmit` |
| Variables | camelCase | `appState` |
| Constants | UPPER_SNAKE | `ALLOWED_ORIGINS` |
| Files (components) | PascalCase | `OnboardingForm.tsx` |
| Files (utilities) | kebab-case | `use-mobile.tsx` |

## ANTI-PATTERNS (THIS PROJECT)

- **No `as any`**: TypeScript strict mode, explicit types required
- **No OAuth stubs**: LinkedIn/Instagram/TikTok fetchers are placeholders, don't call them
- **No CORS wildcards**: ALLOWED_ORIGINS is explicit list, don't use `["*"]`
- **No blocking in async**: All I/O uses async/await
- **No hardcoded timeouts**: Use named constants or env vars

## UNIQUE STYLES

- **Vite source-identifier**: Adds `data-matrix-*` attributes in dev for debugging
- **Multi-provider images**: Single endpoint supports OpenAI, Ideogram, Gemini via `image_provider` param
- **3-step wizard**: OnboardingForm uses step state (1=name, 2=interests, 3=socials)
- **Tailwind custom colors**: Primary green, secondary blue, accent orange (spirit animal theme)
- **shadcn/ui config**: New York style, Lucide icons (`components.json`)

## COMMANDS

### Frontend

```bash
cd spirit-animal-app
pnpm dev              # Vite dev server on :5173
pnpm build            # Production build
pnpm build:prod       # Production with optimizations (no source-identifier)
pnpm lint             # ESLint check
pnpm preview          # Preview production build
```

### Backend

```bash
cd spirit-animal-backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python main.py        # Uvicorn on :8000
```

### Health Checks

```bash
curl http://localhost:8000/           # Basic health
curl http://localhost:8000/api/health # Detailed (shows API key status)
```

## ENV VARS

### Backend (required)

```bash
OPENAI_API_KEY=sk-...        # Required - GPT-4o + DALL-E 3
```

### Backend (optional)

```bash
TWITTER_BEARER_TOKEN=...     # Twitter API (graceful skip if missing)
IDEOGRAM_API_KEY=...         # Ideogram image generation
GEMINI_API_KEY=...           # Gemini image generation
FRONTEND_URL=https://...     # Production CORS origin
```

### Frontend

```bash
VITE_API_URL=http://localhost:8000  # Backend URL (defaults to localhost:8000)
```

## NOTES

### Gotchas

- **CORS**: Backend allows localhost:5173, localhost:3000, 127.0.0.1 variants. Production requires `FRONTEND_URL` env var
- **Social fetchers**: Only Twitter, Reddit, Bluesky work. LinkedIn/Instagram/TikTok are stubs (require OAuth)
- **Image timeouts**: DALL-E takes up to 120s, plan UX accordingly
- **No tests**: Neither frontend nor backend have test frameworks configured
- **No CI/CD**: No GitHub Actions, Docker, or deployment automation

### API Contract

```typescript
// Request
POST /api/spirit-animal
{
  name: string,
  interests?: string,
  values?: string,
  socialHandles?: { platform: string, handle: string }[],
  image_provider?: "openai" | "gemini" | "ideogram"
}

// Response
{
  personality_summary: string,
  spirit_animal: string,
  animal_reasoning: string,
  art_medium: string,
  medium_reasoning: string,
  image_url: string,
  image_provider: string
}
```

### Supported Social Platforms

| Platform | Status | Auth |
|----------|--------|------|
| Twitter/X | Working | Bearer token |
| Reddit | Working | None (public API) |
| Bluesky | Working | None (public API) |
| LinkedIn | Stub | Requires OAuth |
| Instagram | Stub | Requires OAuth |
| TikTok | Stub | Requires OAuth |
