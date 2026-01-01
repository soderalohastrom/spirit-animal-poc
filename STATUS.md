# Spirit Animal POC - Project Status

**Last Updated:** 2024-12-30
**Current Branch:** `experiment/multiple-choice-flow`
**Base Branch:** `feature/tambo-onboarding`

---

## Project Summary

Full-stack spirit animal generator using conversational AI. Users chat with a "Spirit Animal Guide" that asks 7 questions to understand their personality, then generates a personalized spirit animal with AI-generated artwork.

**Stack:**
- Frontend: React + Vite + TypeScript + Tailwind + Tambo SDK
- Backend: FastAPI + Python 3.11 + OpenAI GPT-4o + Gemini (images)

---

## Where We've Been

### Phase 1: Original Implementation
- Traditional 3-step form wizard (name → interests → social handles)
- V1 backend pipeline with basic personality analysis
- DALL-E 3 for image generation

### Phase 2: Tambo Integration (`feature/tambo-onboarding`)
- Replaced form with conversational UI using Tambo SDK
- Created 7-turn conversation flow:
  1. Name
  2. Energy Mode (leader/adapter/observer)
  3. Social Pattern (solitude/close_circle/crowd)
  4. Self-Description (open-ended)
  5. Joy Source (open-ended)
  6. Aspirations (open-ended)
  7. Element Affinity (fire/water/earth/air)
- Built V2 backend pipeline with rich interpretation prompts
- Added `TamboSpiritAnimalCard` component for results
- Switched default image provider to Gemini (`gemini-2.0-flash-exp-image-generation`)
- Fixed props flattening issue (Tambo couldn't map nested props)

### Phase 3: Multiple Choice Experiment (`experiment/multiple-choice-flow`) ← CURRENT
- Changed from emoji-based options to A/B/C/D/E format
- Added "Other" option for freeform responses on choice questions
- Goal: Users can quickly type "a", "b", "c" + enter
- Added Joy Source starter options (was pure open-ended)
- Created DebugPanel for development visibility

---

## Current State

### What's Working
- Backend V2 endpoint (`POST /api/spirit-animal/v2`)
- Tambo conversation flow with system prompt
- `generateSpiritAnimal` tool integration
- `SpiritAnimalCard` component rendering
- DebugPanel for visibility into Tambo internals

### What Needs Testing/Debugging
- A/B/C/D/E format acceptance (does Tambo correctly interpret "a", "b", etc.?)
- Full conversation flow end-to-end
- Image URL handling (previously saw `ERR_INVALID_URL` with base64)
- Edge cases: "Other" option handling, short answers

### Key Files
| File | Purpose |
|------|---------|
| `spirit-animal-app/src/lib/tambo.ts` | Tambo config, tools, system prompt |
| `spirit-animal-app/src/components/chat/SpiritAnimalChat.tsx` | Main chat UI |
| `spirit-animal-app/src/components/chat/DebugPanel.tsx` | Dev debug panel |
| `spirit-animal-app/src/components/TamboSpiritAnimalCard.tsx` | Result display |
| `spirit-animal-backend/llm/pipeline.py` | V2 interpretation pipeline |
| `spirit-animal-backend/main.py` | FastAPI endpoints |

---

## Where We're Going

### Immediate Next Steps
1. **Test the A/B/C/D/E flow** — Use DebugPanel to see where it breaks
2. **Debug any issues** — Check tool call params, mapping logic
3. **Verify image display** — Ensure base64 URLs work correctly

### If Multiple Choice Works Well
1. **Expand to 10 questions** — More nuanced personality profiling
2. **Update backend schema** — Add new fields to V2 request/response
3. **Refine question options** — Based on testing feedback

### Future Ideas
- Add more element affinities or hybrid options
- Social media integration (fetch personality from Twitter/Bluesky)
- Save/share spirit animal results
- Multiple spirit animals (primary + secondary)

---

## How to Run

```bash
# Terminal 1 - Backend
cd spirit-animal-backend
source .venv311/bin/activate
python main.py  # Port 8000

# Terminal 2 - Frontend
cd spirit-animal-app
pnpm dev  # Port 5173
```

**Debug Panel:** Click bug icon (bottom-right) or press `Ctrl+Shift+D`

---

## Git State

```
experiment/multiple-choice-flow (HEAD)
├── 40659ef feat(debug): add DebugPanel for Tambo conversation visibility
├── 5e91e15 experiment(tambo): switch to A/B/C/D/E multiple choice format
└── ...feature/tambo-onboarding commits...

feature/tambo-onboarding
├── a7c3212 fix(frontend): flatten TamboSpiritAnimalCard props
├── 42f7d2e feat: switch default image provider to Gemini
├── cfbf9e7 feat(backend): add V2 pipeline with rich interpretation
└── 638144d feat(tambo): implement V2 conversational onboarding flow
```

---

## Environment Variables

```bash
# Backend (required)
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AIza...

# Backend (optional)
TWITTER_BEARER_TOKEN=...
IDEOGRAM_API_KEY=...

# Frontend
VITE_API_URL=http://localhost:8000
```

---

## Notes for Next Session

1. Start by running both servers and testing the conversation flow
2. Open DebugPanel to watch message flow and tool calls
3. If "tripped up" occurs, check:
   - What was the last user message?
   - Did the tool call fire with correct params?
   - Any ERROR badges in debug panel?
4. The system prompt is in `tambo.ts` — adjust mapping instructions if needed
