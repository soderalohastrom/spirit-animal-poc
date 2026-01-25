# Spirit Animal POC

Full-stack spirit animal generator with dual discovery modes: traditional form wizard or AI-guided conversation via Tambo.

## Stack

| Layer | Tech |
|-------|------|
| Frontend | React 18 + Vite + TypeScript + Tailwind + Radix UI |
| Conversational AI | Tambo SDK (@tambo-ai/react) |
| Backend | FastAPI + Python 3.11 + Pydantic v2 |
| LLM | GPT-4o (personality/interpretation) |
| Image Gen | Gemini (default) / DALL-E 3 / Ideogram |
| Image Hosting | imgBB (converts Gemini base64 to URLs) |

## Structure

```
spirit-animal-poc/
├── spirit-animal-app/          # React frontend
│   └── src/
│       ├── components/
│       │   ├── OnboardingForm.tsx      # 3-step wizard (form mode)
│       │   ├── SpiritAnimalCard.tsx    # Result display (form mode)
│       │   ├── TamboSpiritAnimalCard.tsx # Result display (chat mode)
│       │   ├── LoadingState.tsx        # Animated loading screen
│       │   └── chat/
│       │       ├── SpiritAnimalChat.tsx # Tambo chat UI
│       │       └── DebugPanel.tsx       # Dev visibility panel
│       ├── lib/
│       │   ├── tambo.ts               # Tambo config, tools, system prompt
│       │   └── utils.ts               # cn() helper
│       └── App.tsx                    # State manager (form/chat toggle)
├── spirit-animal-backend/      # FastAPI backend
│   ├── main.py                 # API endpoints (V1 + V2)
│   ├── llm/
│   │   └── pipeline.py         # LLM orchestration + image generation
│   └── fetchers/
│       └── social_fetcher.py   # Twitter, Reddit, Bluesky fetchers
└── assets/                     # Static demo files
```

## Key Files

| Task | File | Notes |
|------|------|-------|
| Tambo conversation flow | `spirit-animal-app/src/lib/tambo.ts` | System prompt, tools, component registration |
| V2 API endpoint | `spirit-animal-backend/main.py` | `POST /api/spirit-animal/v2` |
| Image generation | `spirit-animal-backend/llm/pipeline.py` | `step3_generate_image()`, imgBB upload |
| Result card (chat) | `TamboSpiritAnimalCard.tsx` | Flat props for LLM compatibility |

## API Flow

### V2 (Tambo Conversational) - Primary

```
Tambo 7-turn conversation
    │
    ▼
generateSpiritAnimal tool (tambo.ts)
    │ Assembles personality summary
    ▼
POST /api/spirit-animal/v2
    │
    ▼
interpret_spirit_animal() ──► GPT-4o JSON response
    │
    ▼
step3_generate_image() ──► Gemini ──► imgBB ──► URL
    │
    ▼
TamboSpiritAnimalCard renders with image
```

### V1 (Form Wizard) - Legacy

```
OnboardingForm (3 steps)
    │
    ▼
POST /api/spirit-animal
    │ + parallel social fetching
    ▼
step1_personality_summary() ──► GPT-4o
    │
    ▼
step2_spirit_animal() ──► GPT-4o JSON
    │
    ▼
step3_generate_image() ──► DALL-E 3 / Gemini
    │
    ▼
SpiritAnimalCard renders
```

## Running

```bash
# Backend (Terminal 1)
cd spirit-animal-backend
source .venv311/bin/activate
python main.py  # Port 8000

# Frontend (Terminal 2)
cd spirit-animal-app
pnpm dev  # Port 5173
```

## Environment Variables

```bash
# Backend (.env)
OPENAI_API_KEY=sk-...      # Required - GPT-4o
GEMINI_API_KEY=AIza...     # Required - Image generation
IMGBB_API_KEY=...          # Required - Gemini image hosting

# Optional
TWITTER_BEARER_TOKEN=...   # Twitter API
IDEOGRAM_API_KEY=...       # Alternative image provider

# Frontend
VITE_API_URL=http://localhost:8000
```

## Conventions

- **Tambo props**: Flat, not nested (LLMs struggle with nested objects)
- **Image URLs**: Gemini returns base64 → uploaded to imgBB → returned as URL
- **Timeouts**: GPT-4o 60s, Image generation 120s
- **CORS**: Explicit origins in `ALLOWED_ORIGINS`, no wildcards

## Gotchas

- Gemini image model is `gemini-2.0-flash-exp-image-generation` (experimental)
- imgBB images expire in 7 days
- Social fetchers: Only Twitter/Reddit/Bluesky work; LinkedIn/Instagram/TikTok are stubs
- DebugPanel: Press `Ctrl+Shift+D` or click bug icon (bottom-right)

---

## Dev Tools

Dependency analysis and large file tools are installed.

| Command | Description |
|---------|-------------|
| `/deps <file>` | What imports this file? |
| `/impact <file>` | What breaks if I change this? |
| `/circular` | Find circular dependencies |
| `/deadcode` | Find unused files |
| `/large-file <file>` | Read large file progressively |
