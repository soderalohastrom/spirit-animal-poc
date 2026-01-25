# Spirit Animal POC - Status

**Last Updated:** 2025-01-24  
**Branch:** `master`

---

## Project Summary

Full-stack spirit animal generator with dual discovery modes:
- **Chat Mode:** AI-guided 7-turn conversation via Tambo SDK
- **Form Mode:** Traditional 3-step wizard (legacy)

**Stack:** React + Vite + Tambo | FastAPI + GPT-4o + Gemini

---

## Current State: Working E2E

The full conversational flow works end-to-end:
1. User chats with Spirit Animal Guide (7-turn conversation)
2. Tambo collects personality data via A/B/C/D/E choices
3. Backend interprets personality → selects spirit animal + art medium
4. Gemini generates image → uploads to imgBB → returns URL
5. TamboSpiritAnimalCard displays result with image

---

## Milestones Completed

### Phase 4: imgBB Integration (2025-01-24)
- **Problem:** Gemini returned base64 images (~500KB) that Tambo couldn't handle
- **Solution:** `upload_to_imgbb()` function uploads base64, returns ~40-char URL
- **Result:** Images display correctly in the result card

### Phase 3: Multiple Choice Format (2024-12-30)
- Changed from emoji-based options to A/B/C/D/E format
- Users can quickly type "a", "b", "c" + enter
- Added "Other" option for freeform on choice questions
- Created DebugPanel for development visibility

### Phase 2: Tambo Integration (2024-12-29)
- Replaced form with conversational UI using Tambo SDK
- Created 7-turn conversation flow (name, energy, social, self-description, joy, aspirations, element)
- Built V2 backend pipeline with rich interpretation prompts
- Added `TamboSpiritAnimalCard` component for results

### Phase 1: Original Implementation
- Traditional 3-step form wizard
- V1 backend pipeline with basic personality analysis
- DALL-E 3 for image generation

---

## Environment Variables

```bash
# Backend (required)
OPENAI_API_KEY=sk-...      # GPT-4o for personality interpretation
GEMINI_API_KEY=AIza...     # Image generation
IMGBB_API_KEY=...          # Uploads Gemini base64 to get URLs

# Backend (optional)
TWITTER_BEARER_TOKEN=...   # Social fetching
IDEOGRAM_API_KEY=...       # Alternative image provider

# Frontend
VITE_API_URL=http://localhost:8000
```

---

## How to Run

```bash
# Backend (Terminal 1)
cd spirit-animal-backend
source .venv311/bin/activate
python main.py  # Port 8000

# Frontend (Terminal 2)
cd spirit-animal-app
pnpm dev  # Port 5173
```

**Debug Panel:** `Ctrl+Shift+D` or bug icon (bottom-right)

---

## Key Files

| File | Purpose |
|------|---------|
| `spirit-animal-app/src/lib/tambo.ts` | Tambo config, tools, system prompt |
| `spirit-animal-app/src/components/TamboSpiritAnimalCard.tsx` | Result display (chat mode) |
| `spirit-animal-app/src/components/chat/DebugPanel.tsx` | Dev debug panel |
| `spirit-animal-backend/llm/pipeline.py` | LLM orchestration + imgBB upload |
| `spirit-animal-backend/main.py` | FastAPI endpoints (V1 + V2) |

---

## Known Issues

1. **LSP button warnings** - Missing `type` prop on buttons (non-blocking)
2. **imgBB expiration** - Images expire in 7 days
3. **Social stubs** - LinkedIn/Instagram/TikTok fetchers are placeholders

---

## Next Steps

- [ ] Expand to 10 questions for more nuanced profiling
- [ ] Add permanent image storage (S3 or similar)
- [ ] Share functionality with OG image generation
- [ ] Refine question options based on user feedback
- [ ] Deeper Tambo integration (memory, follow-up questions)
