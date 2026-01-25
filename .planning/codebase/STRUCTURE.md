# Codebase Structure

**Analysis Date:** 2026-01-21

## Directory Layout

```
spirit-animal-poc/
├── spirit-animal-app/              # Frontend: React + Vite + Tambo
│   ├── src/
│   │   ├── App.tsx                 # Root app, mode toggle, state management
│   │   ├── main.tsx                # React DOM entry point
│   │   ├── components/
│   │   │   ├── chat/
│   │   │   │   ├── SpiritAnimalChat.tsx   # Conversation UI
│   │   │   │   ├── DebugPanel.tsx         # Dev debug panel
│   │   │   │   └── index.ts               # Barrel export
│   │   │   ├── OnboardingForm.tsx         # V1 form mode
│   │   │   ├── SpiritAnimalCard.tsx       # V1 result card
│   │   │   ├── TamboSpiritAnimalCard.tsx  # V2 result card
│   │   │   ├── ErrorBoundary.tsx          # React error boundary
│   │   │   └── LoadingState.tsx           # Loading spinner UI
│   │   ├── hooks/
│   │   │   └── use-mobile.tsx             # Mobile detection hook
│   │   ├── lib/
│   │   │   ├── tambo.ts                   # Tambo config, tools, prompts
│   │   │   └── utils.ts                   # Shared utilities
│   │   ├── vite-env.d.ts            # Vite type definitions
│   │   ├── App.css                  # App-level styles
│   │   └── index.css                # Global styles + Tailwind
│   ├── public/                      # Static assets
│   ├── dist/                        # Build output
│   ├── package.json                 # Dependencies: React, Vite, Tambo, Radix, Tailwind
│   ├── tsconfig.json                # TypeScript config (alias: @/src)
│   ├── tsconfig.app.json            # App-specific TS config
│   ├── tsconfig.node.json           # Node-specific TS config
│   ├── vite.config.ts               # Vite config with React plugin
│   ├── eslint.config.js             # ESLint rules
│   ├── tailwind.config.js           # Tailwind CSS config
│   └── postcss.config.js            # PostCSS + autoprefixer
│
├── spirit-animal-backend/           # Backend: FastAPI + Python 3.11
│   ├── main.py                      # FastAPI app, endpoints, CORS config
│   ├── llm/
│   │   ├── __init__.py              # Exports: pipeline functions
│   │   └── pipeline.py              # LLM orchestration, interpretation, image gen
│   ├── fetchers/
│   │   ├── __init__.py              # Exports: fetch_all
│   │   └── social_fetcher.py        # Twitter, Reddit data fetching (V1 only)
│   ├── test_*.py                    # Test files for interpretation, image generation
│   ├── requirements.txt             # Python dependencies: FastAPI, OpenAI, httpx
│   ├── .env                         # Environment variables (not committed)
│   └── .venv, .venv311/             # Python virtual environments
│
├── .planning/
│   ├── codebase/
│   │   ├── ARCHITECTURE.md          # This file tree
│   │   ├── STRUCTURE.md             # (you are here)
│   │   ├── STACK.md                 # Technologies and versions
│   │   └── INTEGRATIONS.md          # External APIs and services
│   └── ...                          # Other planning docs
│
├── .claude/
│   ├── CLAUDE.md                    # Project-specific instructions
│   ├── bin/                         # Dev tools
│   └── plugins/                     # LSP server configs
│
├── STATUS.md                        # Session handoff (last updated 2024-12-30)
├── CLAUDE.md                        # Quick dev tools reference
├── FRONTEND_ONBOARDING_PLAN.md      # Implementation notes
├── BACKEND_HANDOFF.md               # Backend architecture notes
├── TAMBO_INTEGRATION_GUIDE.md       # Tambo SDK integration details
├── AGENTS.md                        # Agent definitions for spirit animal traits
├── make_spirit_animals.py           # Data generation script (legacy)
├── generate_spirit_image.py         # Image generation utility (legacy)
├── latest_prompt_claude_spirit_animals_oct.txt  # Historical prompt
└── ideogram_info_no_credits.txt     # Image provider info
```

## Directory Purposes

**`spirit-animal-app/src/`:**
- Purpose: All React source code
- Contains: Components, hooks, utilities, styling, type definitions
- Key files: `App.tsx` (root), `lib/tambo.ts` (Tambo config), `components/*` (UI)

**`spirit-animal-app/src/components/`:**
- Purpose: Reusable React components
- Contains: UI components for chat, forms, results, error handling
- Naming: PascalCase for component files (e.g., `OnboardingForm.tsx`)

**`spirit-animal-app/src/components/chat/`:**
- Purpose: Conversational UI components
- Contains: Chat message renderer, input field, debug panel
- Key file: `SpiritAnimalChat.tsx` (main chat interface)

**`spirit-animal-app/src/lib/`:**
- Purpose: Non-React utilities and configuration
- Contains: Tambo SDK setup, type schemas, helper functions
- Key file: `tambo.ts` (conversational flow, tools, system prompt)

**`spirit-animal-app/src/hooks/`:**
- Purpose: Custom React hooks
- Contains: Mobile detection, form hooks (from react-hook-form)
- Key file: `use-mobile.tsx` (responsive layout detection)

**`spirit-animal-backend/`:**
- Purpose: FastAPI backend
- Contains: API endpoints, LLM pipeline, social data fetching
- Key file: `main.py` (FastAPI app definition)

**`spirit-animal-backend/llm/`:**
- Purpose: LLM orchestration and image generation
- Contains: OpenAI client calls, interpretation prompts, multi-provider image generation
- Key file: `pipeline.py` (core logic)

**`spirit-animal-backend/fetchers/`:**
- Purpose: External data collection (V1 form mode only)
- Contains: Twitter API integration, data aggregation
- Key file: `social_fetcher.py` (social media API calls)

**`.planning/codebase/`:**
- Purpose: Architecture and codebase documentation (this directory)
- Contains: ARCHITECTURE.md, STRUCTURE.md, STACK.md, INTEGRATIONS.md

## Key File Locations

**Entry Points:**
- `spirit-animal-app/src/main.tsx` — React DOM bootstrap
- `spirit-animal-app/src/App.tsx` — App root component
- `spirit-animal-backend/main.py` — FastAPI app server

**Configuration:**
- `spirit-animal-app/tsconfig.json` — TypeScript path aliases (@/)
- `spirit-animal-app/vite.config.ts` — Build config, React plugin
- `spirit-animal-backend/main.py` — CORS, environment validation
- `.env` — API keys, database URLs (not committed)

**Core Logic:**
- `spirit-animal-app/src/lib/tambo.ts` — Conversation flow, tools, prompts (900+ lines)
- `spirit-animal-backend/llm/pipeline.py` — LLM interpretation and image generation
- `spirit-animal-app/src/components/chat/SpiritAnimalChat.tsx` — Chat UI
- `spirit-animal-app/src/components/OnboardingForm.tsx` — Form UI

**Testing:**
- `spirit-animal-backend/test_interpretation.py` — Test spirit animal interpretation
- `spirit-animal-backend/test_image_generation.py` — Test image generation endpoints

**Utilities:**
- `spirit-animal-app/src/lib/utils.ts` — Shared helpers (formatting, validation)
- `spirit-animal-app/src/hooks/use-mobile.tsx` — Responsive design hook

## Naming Conventions

**Files:**
- React components: PascalCase (e.g., `SpiritAnimalChat.tsx`, `OnboardingForm.tsx`)
- Utilities/helpers: camelCase (e.g., `tambo.ts`, `utils.ts`)
- Hooks: `use-` prefix, kebab-case (e.g., `use-mobile.tsx`)
- Python modules: snake_case (e.g., `social_fetcher.py`, `pipeline.py`)

**Directories:**
- Component subdirs: lowercase plural (e.g., `components/`, `hooks/`, `lib/`)
- Backend modules: lowercase (e.g., `llm/`, `fetchers/`)
- Feature dirs: kebab-case (e.g., `spirit-animal-app/`, `spirit-animal-backend/`)

**Variables & Functions:**
- React: camelCase (e.g., `handleSubmit`, `isPending`, `messageEndRef`)
- Python: snake_case (e.g., `personality_summary`, `fetch_all`, `generate_spirit_animal`)
- Constants: UPPER_SNAKE_CASE (e.g., `SPIRIT_ANIMAL_SYSTEM_PROMPT`, `API_BASE`)
- Types/Interfaces: PascalCase (e.g., `UserProfile`, `SpiritResult`, `TamboSpiritAnimalCardProps`)

## Where to Add New Code

**New Feature (Conversational Flow Enhancement):**
- Prompt changes: `spirit-animal-app/src/lib/tambo.ts` → `SPIRIT_ANIMAL_SYSTEM_PROMPT`
- Tool logic: `spirit-animal-app/src/lib/tambo.ts` → tools array
- Component rendering: `spirit-animal-app/src/components/chat/SpiritAnimalChat.tsx` or new component in `chat/`
- Styling: Tailwind classes in component files (no separate CSS files)

**New Component:**
- Location: `spirit-animal-app/src/components/[name].tsx` or `spirit-animal-app/src/components/chat/[name].tsx` if conversation-related
- Pattern: Named export function, interfaces at top, JSX at bottom
- Example structure:
  ```typescript
  // @file NewComponent.tsx
  interface NewComponentProps { /* ... */ }

  export function NewComponent(props: NewComponentProps) {
    // hooks
    // handlers
    return ( /* JSX */ )
  }
  ```

**New API Endpoint:**
- Location: `spirit-animal-backend/main.py` → add @app.post() or @app.get() decorator
- Pattern: Async function, Pydantic models for req/response, try-catch with HTTPException
- Example:
  ```python
  @app.post("/api/new-endpoint", response_model=ResponseModel)
  async def new_endpoint(req: RequestModel):
      try:
          result = await some_operation(req)
          return ResponseModel(**result)
      except Exception as e:
          raise HTTPException(status_code=500, detail=str(e))
  ```

**Backend Utility/Helper:**
- Location: `spirit-animal-backend/llm/pipeline.py` (if interpretation-related) or new `spirit-animal-backend/utils.py`
- Pattern: Async functions, proper error handling, descriptive docstrings
- Exports: Add to `spirit-animal-backend/llm/__init__.py` if utility is LLM-related

**New Hook:**
- Location: `spirit-animal-app/src/hooks/use-[name].tsx`
- Pattern: Hook function with `use` prefix, export named export
- Example: `use-auth.tsx`, `use-form-state.tsx`

**Test File:**
- Location: `spirit-animal-backend/test_[feature].py` (pytest-compatible)
- Pattern: Async test functions with `async def test_*()` signature
- Run: `pytest test_[feature].py`

## Special Directories

**`spirit-animal-app/dist/`:**
- Purpose: Built frontend (Vite output)
- Generated: Yes (by `npm run build`)
- Committed: No (in `.gitignore`)

**`spirit-animal-app/node_modules/`:**
- Purpose: JavaScript dependencies
- Generated: Yes (by `pnpm install`)
- Committed: No (in `.gitignore`)

**`spirit-animal-backend/.venv` and `.venv311/`:**
- Purpose: Python virtual environments
- Generated: Yes (by `python -m venv`)
- Committed: No (in `.gitignore`)

**`.env` and `.env.local`:**
- Purpose: Environment variables (API keys, URLs)
- Generated: No (created manually)
- Committed: No (in `.gitignore`)

**`.claude/`:**
- Purpose: Claude AI tools and plugins
- Generated: Partially (plugins auto-cached)
- Committed: Some files (CLAUDE.md, bin/)

---

*Structure analysis: 2026-01-21*
