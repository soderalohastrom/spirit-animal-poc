# Frontend Onboarding Plan

**For:** Backend LLM integration
**From:** Frontend Tambo implementation
**Date:** December 2024
**Branch:** Will be `feature/tambo-onboarding` (branching soon)

---

## Overview

We're replacing the generic form-based data gathering with a **conversational onboarding flow** using Tambo (Generative UI SDK). The goal is to capture rich personality signals through low-friction, engaging questions that feed directly into your excellent interpretation system prompt.

The backend's `INTERPRETATION_SYSTEM_PROMPT` expects:
- Key personality traits and emotional energy
- Life approach and core values
- Personal and professional aspirations
- Lifestyle preferences and interests
- Social dynamics and relationship style

Our frontend flow is designed to capture exactly this.

---

## The 7-Turn Conversational Flow

| Step | Question | Response Type | Signal Captured |
|------|----------|---------------|-----------------|
| 1 | Name + Pronouns | Text + Choice | Identity, image framing |
| 2 | Energy Mode | Triple choice | Maps to animal category |
| 3 | Social Pattern | Triple choice | Social dynamics |
| 4 | Self-Description | Open text | **Their exact words** |
| 5 | Joy Source | Open text | Lifestyle + interests |
| 6 | Aspirations | Open text | Values + direction |
| 7 | Element Affinity | Quad choice | Artistic setting + palette |

### Question Details

**1. Name + Identity**
> "What name shall I call you, and how do you identify?"
> Options: He/Him | She/Her | They/Them | Rather not say

**2. Energy Mode** *(maps to Power/Grace/Wisdom categories)*
> "When facing a challenge, do you typically..."
> - Lead from the front (take charge, make decisions)
> - Adapt and maneuver (find the clever path through)
> - Observe first (understand before acting)

**3. Social Pattern**
> "How do you recharge your energy?"
> - Solitude (quiet time alone)
> - Close circle (a few people I trust)
> - The crowd (energy from being around others)

**4. Self-Description** *(the heart of the summary)*
> "In just a few words, how would someone who truly knows you describe you?"

**5. Joy Source**
> "What activities or moments bring you the most genuine joy?"

**6. Aspirations**
> "What matters most to you right now? What are you working toward?"

**7. Element Affinity** *(guides artistic setting)*
> "Which element calls to you most?"
> - Fire (passion, transformation, intensity)
> - Water (depth, flow, emotion)
> - Earth (stability, growth, grounding)
> - Air (freedom, possibility, lightness)

---

## Output: The Rich Summary

The frontend will assemble responses into a **personality summary** that feeds your interpretation pipeline. Here's the format:

```
[Name] ([pronouns]) describes themselves as "[their exact words from Q4]".

Energy & Approach: They [energy mode description], showing a tendency to [inferred trait].
When they need to recharge, they seek [social pattern description].

What brings them joy: [Q5 response verbatim]

What they're working toward: [Q6 response verbatim]

They're drawn to [Element] energy—[element characteristics].
```

### Example Output

```
Maya (she/her) describes herself as "curious, warm, and a bit stubborn when it matters."

Energy & Approach: She adapts and maneuvers through challenges, finding clever paths
rather than forcing through. When she needs to recharge, she seeks her close circle
of trusted people.

What brings her joy: Long conversations over coffee, discovering new music, and
the moment when a complex idea finally clicks.

What she're working toward: Building something meaningful that helps others learn.

She's drawn to Water energy—depth, flow, and emotional resonance.
```

---

## Mapping to Backend Categories

### Energy Mode → Spirit Animal Categories

| Frontend Choice | Backend Animal Categories |
|-----------------|---------------------------|
| Lead from front | Power & Leadership (Lion, Wolf, Eagle, Tiger) |
| Adapt & maneuver | Grace & Intuition (Fox, Cat, Dolphin, Butterfly) |
| Observe first | Wisdom & Contemplation (Owl, Elephant, Whale, Raven) |

*Note: These are hints, not constraints. The full summary should guide final selection.*

### Element Affinity → Artistic Direction

| Element | Suggested Palette/Mood | Medium Affinity |
|---------|------------------------|-----------------|
| Fire | Warm oranges, reds, golds; dramatic | Bold/Dynamic mediums |
| Water | Blues, teals, silvers; flowing | Soft watercolor, ink wash |
| Earth | Browns, greens, ochre; grounded | Earth-toned oil, woodcut |
| Air | Light blues, whites, lavender; ethereal | Delicate, airy compositions |

### Pronouns → Subtle Image Guidance

- Can subtly influence animal portrayal (lioness vs lion, etc.)
- No human faces in images, but energy can be adjusted
- Included in summary for interpretation context

---

## Backend Integration Points

### Current Pipeline (pipeline.py)

```
form_data → aggregate_raw_text() → step1_personality_summary() → step2_spirit_animal() → step3_generate_image()
```

### Proposed Change

The frontend will send a **pre-assembled rich summary** instead of raw form fields. Options:

**Option A: Replace `aggregate_raw_text`**
- Frontend sends structured data
- Backend assembles into summary format
- Keeps existing pipeline steps

**Option B: Skip to interpretation**
- Frontend sends the assembled summary directly
- Backend skips `step1_personality_summary` (frontend did it)
- Goes straight to `step2_spirit_animal` (your rich interpretation prompt)

**Option C: New endpoint**
- New `/api/spirit-animal/v2` endpoint
- Accepts the rich summary directly
- Uses the production-ready interpretation system prompt

---

## Data Schema (Frontend → Backend)

```typescript
interface SpiritAnimalRequest {
  // Structured data
  name: string;
  pronouns: "he/him" | "she/her" | "they/them" | "unspecified";
  energyMode: "leader" | "adapter" | "observer";
  socialPattern: "solitude" | "close_circle" | "crowd";
  elementAffinity: "fire" | "water" | "earth" | "air";

  // Open responses (their words)
  selfDescription: string;
  joySource: string;
  aspirations: string;

  // Optional
  imageProvider?: "openai" | "gemini" | "none";
}
```

Or, if you prefer the assembled summary:

```typescript
interface SpiritAnimalRequest {
  personalitySummary: string;  // Pre-assembled rich summary
  pronouns: "he/him" | "she/her" | "they/them" | "unspecified";
  elementAffinity: "fire" | "water" | "earth" | "air";
  imageProvider?: "openai" | "gemini" | "none";
}
```

---

## Questions for Backend

1. **Which integration option do you prefer?** (A, B, or C above)
2. **Should pronouns influence animal selection?** Or just be metadata?
3. **Should element affinity be passed to the interpretation prompt?** It could help guide artistic medium selection.
4. **Any additional signals you'd want from the frontend?**

---

## Next Steps

1. Backend: Port rich interpretation prompt into `pipeline.py`
2. Backend: Decide on API schema (structured vs summary)
3. Frontend: Implement Tambo conversational flow
4. Frontend: Build summary assembly logic
5. Integration: Test end-to-end flow

---

## Reference: Backend's Interpretation Framework

Your `INTERPRETATION_SYSTEM_PROMPT` analyzes for:
- Key personality traits and emotional energy ← **Q2, Q4**
- Life approach and core values ← **Q2, Q6**
- Personal and professional aspirations ← **Q6**
- Lifestyle preferences and interests ← **Q5**
- Social dynamics and relationship style ← **Q3**

The frontend flow is purpose-built to feed this framework.

---

*Ma ka hana ka ʻike* — In working, one learns
