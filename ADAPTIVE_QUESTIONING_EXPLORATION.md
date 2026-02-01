# Adaptive Questioning Exploration

> **Living Document** — Created: January 2026  
> This document captures ideas, experiments, and evolving thoughts on making the Spirit Animal onboarding experience adaptive and dynamic using Tambo's conversational AI capabilities.

---

## Current State (Baseline)

The Tambo integration currently implements a **fixed 7-turn linear flow**:

```
Name → Energy Mode → Social Pattern → Self-Description → Joy Source → Aspirations → Element Affinity
```

Each turn presents multiple-choice options (A, B, C, D, E). The AI asks ONE question, waits, then proceeds to the next. No deviation, no branching.

**File:** `spirit-animal-app/src/lib/tambo.ts`  
**System Prompt:** `SPIRIT_ANIMAL_SYSTEM_PROMPT`

---

## Why Adaptive Questioning?

### The Problem with Linear Flows
- Feels like a form disguised as conversation
- Can't respond to rich answers with "oh, tell me more about that"
- Wastes user's time with redundant questions
- Misses opportunities to go deeper when user is engaged

### The Opportunity
Tambo isn't just a chat wrapper—it's a **Generative UI SDK**. The LLM can:
- Make routing decisions based on conversation context
- Dynamically adjust tone, depth, and direction
- Render different components at different stages
- Call tools that influence the flow

---

## Exploration Areas

### 1. Adaptive Tone & Personality ✅ IMPLEMENTED

**Idea:** The Spirit Animal Guide shifts its persona based on user's energy mode (Q2).

| Energy Mode | Guide Personality | Language Style |
|-------------|-------------------|----------------|
| Leader | Confident mentor | Direct, empowering, bold |
| Adapter | Wise trickster | Playful, clever, indirect |
| Observer | Gentle mystic | Contemplative, poetic, patient |

**Implementation:** Simple prompt instruction added to `SPIRIT_ANIMAL_SYSTEM_PROMPT` in `spirit-animal-app/src/lib/tambo.ts` (lines 303-322).

**Status:** ✅ **COMPLETE** - Merged to `feature/adaptive-tone` branch  
**Commit:** `c930573`  
**Complexity:** Low  
**Impact:** Medium (makes conversation feel more personal)

**Key Changes:**
- Added "Adaptive Tone (IMPORTANT)" section to system prompt
- Guide now shifts personality after Q2 (Energy Mode) response
- Updated example conversations showing all three tone variations
- Zero code changes—pure prompt engineering enhancement

---

### 2. Conditional Question Skipping

**Idea:** If a user already revealed something, don't ask again.

**Scenario:**
> **User:** "My name is Maya. I'm definitely someone who needs alone time to recharge—I get drained by crowds."

The AI could:
- Extract name: Maya
- Infer socialPattern: solitude
- Skip Q3 (Social Pattern) entirely

**Implementation Approaches:**

**A) Prompt-Based (Simple)**
```markdown
As you converse, watch for answers that cover multiple questions. 
If the user reveals their social pattern while answering about their name, 
acknowledge it: "I can already tell you value your solitude..." 
and skip the dedicated social pattern question.
```

**B) Tool-Assisted (Robust)**
Add a `analyzeResponse` tool that runs after each user message:
```typescript
{
  name: "analyzeResponse",
  tool: async (response, collectedSoFar) => {
    // LLM or regex extraction of implied answers
    return {
      inferredFields: { socialPattern: "solitude" },
      suggestedSkip: ["social_pattern_question"],
      confidence: 0.85
    };
  }
}
```

**Complexity:** Low to Medium  
**Impact:** High (respects user's time, feels intelligent)

---

### 3. Dynamic Follow-Up Probing

**Idea:** When answers are shallow, probe deeper. When rich, move on.

**Scenario A (Shallow):**
> **User:** "idk, i just like being alone"

**Response:** "Tell me more about that. When you're alone, what do you gravitate toward?"

**Scenario B (Rich):**
> **User:** "I seek solitude like a fox seeks its den—necessary, restorative, away from the noise. My best thinking happens in those quiet hours."

**Response:** "That's beautifully put. The fox metaphor tells me a lot. Let's move on—what brings you genuine joy?"

**Implementation:**
```markdown
Assess the depth of each response:
- SHORT (< 5 words) or VAGUE: Ask ONE gentle follow-up, then proceed
- MEDIUM (5-20 words): Accept and continue
- RICH (> 20 words, metaphorical, emotional): Acknowledge the depth, 
  capture their exact words, and consider skipping the next question 
  if they've already revealed enough
```

**Complexity:** Low  
**Impact:** Medium-High (adapts to user's engagement level)

---

### 4. Multi-Path Branching (The Big One)

**Idea:** After Q2+Q3, determine an "archetype path" and customize the remaining questions.

**Archetype Matrix:**

| | Solitude | Close Circle | Crowd |
|---|---|---|---|
| **Leader** | The Sovereign (eagle, wolf) | The Alpha (lion, orca) | The Commander (elephant, buffalo) |
| **Adapter** | The Trickster (fox, raven) | The Diplomat (dolphin, crow) | The Catalyst (monkey, parrot) |
| **Observer** | The Sage (owl, turtle) | The Counselor (elephant, deer) | The Visionary (eagle, peacock) |

**Path Structure:**

```
Q1: Name (universal)
Q2: Energy Mode (determines path flavor)
Q3: Social Pattern (determines path setting)
    ↓
[BRANCH]
    ↓
Path A: Sovereign/Trickster/Sage (solitude-focused questions)
  - "When you're alone with your thoughts..."
  - "In your private sanctuary..."
  
Path B: Alpha/Diplomat/Counselor (relationship-focused questions)
  - "With your closest person..."
  - "When someone truly sees you..."
  
Path C: Commander/Catalyst/Visionary (impact-focused questions)
  - "When all eyes are on you..."
  - "The mark you want to leave..."
```

**Implementation:**

This is too complex for prompt-only. Would need:

```typescript
// Tool that determines path and returns next question
{
  name: "determinePath",
  tool: async (energyMode, socialPattern) => {
    const archetype = getArchetype(energyMode, socialPattern);
    return {
      archetype,
      pathQuestions: questionSets[archetype],
      tone: toneProfiles[archetype]
    };
  }
}

// Then update system prompt dynamically OR
// Store path in component state and inject into context
```

**Complexity:** High  
**Impact:** Very High (feels like a truly personalized experience)

---

### 5. User-Initiated Compression

**Idea:** Let power users "skip to the good part."

**Scenario:**
> **User:** "I'm Alex. I lead a startup, I'm always adapting to market changes, I recharge by hiking alone, my friends say I'm relentlessly optimistic, and I'm drawn to fire."

The AI could:
1. Parse all 7 data points from that single message
2. Confirm: "Let me make sure I heard you right... [summary]"
3. Generate immediately or ask for confirmation

**Implementation:**
```markdown
If the user provides rich information unprompted, don't force them through 
the step-by-step flow. Extract what you can, confirm your understanding, 
and offer to proceed directly to the reveal.

Example:
"I hear a lot in that. Let me check my understanding:
- You lead boldly (leader energy)
- Solitude in nature restores you
- Optimism is your hallmark
- Fire speaks to you

Shall I consult the spirits with what you've shared, or is there more 
you'd like me to know first?"
```

**Complexity:** Medium (requires good extraction)  
**Impact:** High for engaged users, confusing for others (optional optimization)

---

### 6. Progressive Disclosure (Accordion Style)

**Idea:** Not every user needs the same depth. Offer "quick" vs "deep" paths.

**Opening:**
> "Welcome, seeker. Would you like a quick glimpse of your spirit animal (3 questions), or a deeper journey (7 questions)?"

**Quick Path:**
- Name
- One synthesis question: "In three words, how would someone who knows you best describe your essence?"
- Element affinity

**Deep Path:** Original 7-question flow

**Implementation:**
```typescript
// First interaction branches based on user choice
{
  name: "setPathDepth",
  tool: async (choice: "quick" | "deep") => {
    return { questionSet: choice === "quick" ? quickQuestions : deepQuestions };
  }
}
```

**Complexity:** Low  
**Impact:** Medium (caters to different user motivations)

---

### 7. Contextual Component Rendering

**Idea:** The conversation isn't just text—inject interactive UI at key moments.

**Examples:**
- After element affinity: Show a visual element picker (fire/water/earth/air icons) they can click
- During the reveal: Animated transition component before showing SpiritAnimalCard
- For joy source: A "mood board" component where they can select images that resonate

**Implementation:**
Tambo supports this natively—just register more components and instruct the AI when to render them.

```typescript
export const components: TamboComponent[] = [
  {
    name: "ElementPicker",
    description: "Render this when asking about element affinity. Shows 4 clickable element cards.",
    component: ElementPicker,
    propsSchema: z.object({ onSelect: z.function() })
  },
  {
    name: "RevealTransition",
    description: "Render this before the SpiritAnimalCard to build anticipation",
    component: RevealTransition,
    propsSchema: z.object({ userName: z.string(), delay: z.number() })
  }
];
```

**Complexity:** Medium (requires component development)  
**Impact:** High (differentiates from simple chatbots)

---

## Implementation Strategy Thoughts

### Phase 1: Low-Hanging Fruit (This Week)
- [x] ✅ **DONE** - Adaptive tone based on energy mode (implemented in `feature/adaptive-tone` branch, commit `c930573`)
- [ ] Dynamic follow-up probing for short answers
- [ ] Acknowledge+skip when users preemptively answer future questions

### Phase 2: Structured Branching (Next)
- [ ] Implement archetype paths (3 variants of Q4-Q7)
- [ ] Add path determination tool
- [ ] A/B test linear vs branched flows

### Phase 3: Advanced Features (Future)
- [ ] User-initiated compression (parse rich openers)
- [ ] Progressive disclosure (quick vs deep)
- [ ] Contextual component rendering

---

## Open Questions

1. **Do we want to maintain the 7-question structure as a "guaranteed minimum"?**
   - Some users might feel shortchanged with fewer questions
   - Or does it feel more respectful to not ask what they already told us?

2. **How do we handle the "Other" option consistently?**
   - Currently: Map to closest enum value
   - Alternative: Expand enum to include more granular options
   - Alternative: Allow freeform and let backend handle fuzziness

3. **Should the backend know about the path taken?**
   - Currently: Backend just receives final personality_summary
   - Option: Include `archetype` field in API request for potential different image generation styles

4. **What about "undo" or "go back"?**
   - Linear flows make backtracking easy
   - Branched flows: does "back" go to previous question or previous branch point?

5. **Analytics considerations:**
   - How do we track completion rates if paths have different lengths?
   - Should we log which path users took for optimization?

---

## Scratchpad / Recent Thoughts

> *Add timestamped notes here as ideas come up*

### 2026-01-31 — Initial Brainstorm
- The system prompt is essentially "programming" the LLM with natural language
- Could we have the LLM generate the NEXT system prompt based on answers?
  - Like, literally rewrite its own instructions mid-conversation
  - Probably too meta/unpredictable, but interesting thought

### 2026-01-31 — Archetype Expansion
- What if instead of 3×3=9 archetypes, we had more granular combinations?
- Leader + Solitude + Fire = The Exile King
- Observer + Crowd + Water = The Deep Current
- Adapter + Close Circle + Earth = The Garden Architect
- Could these be the actual spirit animals? (probably not, but fun naming)

### 2026-01-31 — The "Vibe Check" Idea
- What if Q2 (Energy Mode) was determined not by asking, but by analyzing HOW they answered Q1?
- Short, direct name: "Alex" → leader energy
- Long, meandering name: "I'm Alexandra but everyone calls me Alex except my grandma" → adapter or observer
- Probably too clever/unreliable, but fun ML thought

---

## Resources & References

- **Tambo Docs:** https://docs.tambo.co
- **Current System Prompt:** `spirit-animal-app/src/lib/tambo.ts` lines 295-451
- **Current Chat Component:** `spirit-animal-app/src/components/chat/SpiritAnimalChat.tsx`
- **Original Question Set:** `questions.txt` (16 questions, not currently used in Tambo flow)

---

## How to Edit This Document

This is a living document. Feel free to:
- Add new exploration areas
- Mark implementations as ✅ Done or 🚧 In Progress
- Update the scratchpad with new ideas
- Add lessons learned from experiments
- Strike through ideas that didn't work

**Last Updated:** 2026-01-31 (Adaptive Tone implemented)  
**Next Review:** After testing Phase 1 features
