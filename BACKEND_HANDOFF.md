# Backend Handoff: V2 Spirit Animal Pipeline

**Date:** December 29, 2024  
**Branch:** `backend-img-gen`  
**Status:** Ready for Frontend Integration

---

## Summary

The backend now has a complete V2 pipeline designed for the Tambo conversational onboarding flow. The key change: **frontend gathers personality, backend interprets**.

### What Changed

| Component | Change |
|-----------|--------|
| `llm/pipeline.py` | Added rich `INTERPRETATION_SYSTEM_PROMPT`, element/energy mappings, `interpret_spirit_animal()`, `generate_spirit_animal_v2()` |
| `llm/__init__.py` | Exported new functions and constants |
| `main.py` | Added `SpiritRequestV2`, `SpiritResponseV2`, and `/api/spirit-animal/v2` endpoint |

---

## V2 API Contract

### Endpoint

```
POST /api/spirit-animal/v2
```

### Request Schema

```typescript
interface SpiritRequestV2 {
  // REQUIRED: Rich personality summary assembled by Tambo
  personality_summary: string;
  
  // OPTIONAL: Structured metadata from conversation choices
  pronouns?: "he/him" | "she/her" | "they/them" | "unspecified";
  energy_mode?: "leader" | "adapter" | "observer";
  social_pattern?: "solitude" | "close_circle" | "crowd";
  element_affinity?: "fire" | "water" | "earth" | "air";
  
  // OPTIONAL: Image generation options
  image_provider?: "openai" | "gemini" | "ideogram" | "none";
  skip_image?: boolean;  // true = skip image gen (for testing)
}
```

### Response Schema

```typescript
interface SpiritResponseV2 {
  personality_summary: string;      // Echoed back
  spirit_animal: string;            // e.g. "Arctic Fox"
  animal_reasoning: string;         // Why this animal
  art_medium: string;               // e.g. "Soft watercolor washes"
  medium_reasoning: string;         // Why this medium
  image_prompt: string;             // The prompt used for image gen
  image_url: string | null;         // Generated image URL (or null if skipped)
  image_provider: string;           // Which provider was used
}
```

---

## How the Metadata is Used

The structured fields (`energy_mode`, `social_pattern`, `element_affinity`, `pronouns`) are **hints**, not constraints. They're appended to the personality summary to guide the LLM's interpretation.

### Energy Mode → Animal Category Hints

| Value | Suggested Animals |
|-------|-------------------|
| `leader` | Power & Leadership (Lion, Wolf, Eagle, Tiger, Bear) |
| `adapter` | Grace & Intuition (Fox, Dolphin, Cat, Butterfly, Crane) |
| `observer` | Wisdom & Contemplation (Owl, Elephant, Whale, Raven, Turtle) |

### Element Affinity → Artistic Direction

| Element | Palette | Mood | Medium Affinity |
|---------|---------|------|-----------------|
| `fire` | Oranges, reds, golds | Passionate, intense | Oil impasto, charcoal, metallic |
| `water` | Blues, teals, silvers | Deep, flowing, serene | Watercolor, sumi-e, fluid acrylics |
| `earth` | Browns, greens, ochre | Grounded, stable | Earth-toned oil, woodcut, botanical |
| `air` | Light blues, whites, lavender | Free, ethereal, expansive | Pen/ink, pastel, minimalist |

### Social Pattern → Animal Personality Hints

| Value | Hint |
|-------|------|
| `solitude` | Solitary or independent animals |
| `close_circle` | Animals with close family/pack bonds |
| `crowd` | Social or community-oriented animals |

---

## Pipeline Flow (V2)

```
Tambo Conversation (7 turns)
         │
         ▼
Frontend assembles personality_summary + metadata
         │
         ▼
POST /api/spirit-animal/v2
         │
         ▼
┌────────────────────────────────────────────┐
│  Backend: _build_interpretation_context()  │
│  - Appends energy/element/social hints     │
│  - Creates enhanced context for LLM        │
└────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│  interpret_spirit_animal()                 │
│  - Uses INTERPRETATION_SYSTEM_PROMPT       │
│  - Returns: spiritAnimal, artisticMedium,  │
│             imagePrompt                    │
└────────────────────────────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│  step3_generate_image()                    │
│  - Supports: openai, gemini, ideogram      │
│  - Can be skipped with skip_image=true     │
└────────────────────────────────────────────┘
         │
         ▼
Return SpiritResponseV2
```

---

## Example Request

```bash
curl -X POST http://localhost:8000/api/spirit-animal/v2 \
  -H "Content-Type: application/json" \
  -d '{
    "personality_summary": "Maya (she/her) describes herself as \"curious, warm, and a bit stubborn when it matters.\"\n\nEnergy & Approach: She adapts and maneuvers through challenges, finding clever paths rather than forcing through. When she needs to recharge, she seeks her close circle of trusted people.\n\nWhat brings her joy: Long conversations over coffee, discovering new music, and the moment when a complex idea finally clicks.\n\nWhat she'\''s working toward: Building something meaningful that helps others learn.\n\nShe'\''s drawn to Water energy—depth, flow, and emotional resonance.",
    "pronouns": "she/her",
    "energy_mode": "adapter",
    "social_pattern": "close_circle",
    "element_affinity": "water",
    "image_provider": "openai"
  }'
```

---

## Testing Without Image Generation

For faster iteration during frontend development:

```bash
curl -X POST http://localhost:8000/api/spirit-animal/v2 \
  -H "Content-Type: application/json" \
  -d '{
    "personality_summary": "Your test summary...",
    "skip_image": true
  }'
```

This returns the full interpretation (animal, medium, reasoning, image_prompt) without waiting for image generation.

---

## File Changes Summary

### `spirit-animal-backend/llm/pipeline.py`

**New Constants:**
- `INTERPRETATION_SYSTEM_PROMPT` — The rich 150-line system prompt
- `ELEMENT_ARTISTIC_HINTS` — Element → palette/mood/medium mapping
- `ENERGY_MODE_HINTS` — Energy → animal category hints
- `SOCIAL_PATTERN_HINTS` — Social → animal trait hints

**New Functions:**
- `_build_interpretation_context()` — Appends metadata hints to summary
- `interpret_spirit_animal()` — Core interpretation using rich prompt
- `generate_spirit_animal_v2()` — V2 pipeline orchestrator

**Preserved (V1 Backwards Compatibility):**
- `aggregate_raw_text()` — Still available for legacy flow
- `step1_personality_summary()` — Still available
- `step2_spirit_animal()` — Still available (simpler prompt)
- `generate_spirit_animal()` — Original pipeline still works

### `spirit-animal-backend/main.py`

**New Models:**
- `SpiritRequestV2` — Request schema for Tambo flow
- `SpiritResponseV2` — Response with `image_prompt` field

**New Endpoint:**
- `POST /api/spirit-animal/v2` — V2 endpoint

**Updated:**
- `/api/health` — Now reports `gemini_configured` and `ideogram_configured`

---

## Frontend Integration Checklist

- [ ] Implement Tambo 7-turn conversational flow
- [ ] Assemble `personality_summary` in the format from `FRONTEND_ONBOARDING_PLAN.md`
- [ ] Capture structured choices (`energy_mode`, `social_pattern`, `element_affinity`, `pronouns`)
- [ ] Call `/api/spirit-animal/v2` with assembled data
- [ ] Handle `image_url: null` case (when `skip_image=true` or `image_provider="none"`)
- [ ] Display results: animal, reasoning, medium, image

---

## Image Provider Options

| Provider | Status | Notes |
|----------|--------|-------|
| `openai` | Ready | DALL-E 3 via gpt-image-1, returns URL |
| `gemini` | Ready | gemini-3-pro-image-preview, returns base64 data URL |
| `ideogram` | Ready | Requires credits on account |
| `none` | Ready | Skips image gen, returns `image_url: null` |

---

## Next Steps

1. **Frontend**: Implement Tambo conversational flow (branch: `feature/tambo-onboarding`)
2. **Frontend**: Build summary assembly logic per `FRONTEND_ONBOARDING_PLAN.md`
3. **Integration**: Test end-to-end with V2 endpoint
4. **Polish**: Loading states for image generation (can take 30-120s)

---

## Running the Backend

```bash
cd spirit-animal-backend
source .venv311/bin/activate  # or your venv
pip install -r requirements.txt
python main.py  # Uvicorn on :8000
```

**Required env vars:**
```
OPENAI_API_KEY=sk-...        # Required for interpretation + DALL-E
```

**Optional env vars:**
```
GEMINI_API_KEY=AIza...       # For Gemini image generation
IDEOGRAM_API_KEY=...         # For Ideogram image generation
FRONTEND_URL=https://...     # Production CORS origin
```

---

*Ma ka hana ka ʻike* — In working, one learns.
