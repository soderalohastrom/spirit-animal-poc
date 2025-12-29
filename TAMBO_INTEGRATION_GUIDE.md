# Tambo Integration Guide - Spirit Animal PoC

**Branch:** `feature/tambo-chat-ui`  
**Date:** December 2024  
**Status:** Scaffolded, needs debugging

## Overview

This guide documents the Tambo integration that adds a conversational AI interface to the Spirit Animal app. Instead of filling out a form, users chat with an AI "Spirit Animal Guide" who asks engaging questions and reveals their spirit animal through natural dialogue.

## What is Tambo?

Tambo is a **Generative UI SDK for React** that lets AI dynamically render React components based on conversation. Key concepts:

- **Components**: React components registered with Tambo that AI can render with props
- **Tools**: Functions the AI can call to fetch data or perform actions
- **System Prompt**: Instructions that shape the AI's personality and behavior

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        App.tsx                               │
│  ┌─────────────────────────────────────────────────────────┐│
│  │                   TamboProvider                          ││
│  │  - apiKey: Tambo API key                                ││
│  │  - components: [SpiritAnimalCard]                       ││
│  │  - tools: [generateSpiritAnimal]                        ││
│  │  - systemPrompt: Spirit Animal Guide persona            ││
│  │  ┌─────────────────────────────────────────────────────┐││
│  │  │              SpiritAnimalChat                        │││
│  │  │  - useTamboThread() → messages                      │││
│  │  │  - useTamboThreadInput() → input handling           │││
│  │  │  - Renders message.renderedComponent                │││
│  │  └─────────────────────────────────────────────────────┘││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Tambo Cloud API                           │
│  - Processes conversation                                    │
│  - Calls tools when needed                                   │
│  - Decides which components to render                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Spirit Animal Backend (FastAPI)                 │
│  POST /api/spirit-animal                                     │
│  - Receives: { name, interests, values, image_provider }    │
│  - Returns: { spirit_animal, animal_reasoning, image_url }  │
└─────────────────────────────────────────────────────────────┘
```

## File Structure

```
spirit-animal-app/src/
├── lib/
│   └── tambo.ts              # Tambo config: components, tools, system prompt
├── components/
│   ├── chat/
│   │   ├── index.ts
│   │   └── SpiritAnimalChat.tsx  # Chat UI component
│   └── TamboSpiritAnimalCard.tsx # Tambo-compatible result card
└── App.tsx                   # Mode toggle (Chat/Form), TamboProvider wrapper
```

## Key Files Explained

### `src/lib/tambo.ts`

Central configuration file containing:


#### 1. Tool Definition
```typescript
export const tools: TamboTool[] = [
  {
    name: "generateSpiritAnimal",
    description: "...",  // AI reads this to know when to call
    tool: async (params) => {
      // Called when AI decides to generate
      const response = await fetch(`${API_BASE}/api/spirit-animal`, {...});
      // Transform backend response to match component schema
      return transformedResult;
    },
    toolSchema: z.function().args(...).returns(...),  // Type safety
  },
];
```

#### 2. Component Registration
```typescript
export const components: TamboComponent[] = [
  {
    name: "SpiritAnimalCard",
    description: "...",  // AI reads this to know when to render
    component: TamboSpiritAnimalCard,
    propsSchema: z.object({...}),  // Props the AI will generate
  },
];
```

#### 3. System Prompt
```typescript
export const SPIRIT_ANIMAL_SYSTEM_PROMPT = `
You are a friendly Spirit Animal Guide...
## Conversation Flow
1. Greeting: Ask their name
2. Discovery: Ask 2-3 questions about interests/values
3. Reveal: Call generateSpiritAnimal, render SpiritAnimalCard
`;
```

### `src/components/chat/SpiritAnimalChat.tsx`

The chat interface using Tambo hooks:

```typescript
const { thread } = useTamboThread();           // Access messages
const { value, setValue, submit } = useTamboThreadInput();  // Handle input

// Render messages with AI-generated components
{thread.messages.map((message) => (
  <div>
    {/* Text content */}
    {message.content.map(part => part.type === "text" && <p>{part.text}</p>)}
    {/* AI-rendered component (e.g., SpiritAnimalCard) */}
    {message.renderedComponent}
  </div>
))}
```

### `src/components/TamboSpiritAnimalCard.tsx`

Simplified card component that receives props from AI:

```typescript
interface TamboSpiritResult {
  animal: string;
  traits: string[];
  explanation: string;
  image_url?: string;
}

function TamboSpiritAnimalCard({ result, userName }) {
  // Render the spirit animal result
}
```

## Current Issues & Debugging

### Issue: Tool calls fail with "Failed to generate spirit animal"

**Root Cause:** Schema mismatch between tool and backend

**Debug Steps:**
1. Check browser console for `[Tambo Tool]` logs
2. Verify backend is running: `curl http://localhost:8000/`
3. Check backend logs for incoming requests

**Console Logging Added:**
```typescript
console.log("[Tambo Tool] generateSpiritAnimal called with:", params);
console.log("[Tambo Tool] Sending to backend:", requestBody);
console.log("[Tambo Tool] Response status:", response.status);
console.log("[Tambo Tool] Backend response:", backendResult);
```

### Schema Mapping

| Tambo Tool Sends | Backend Expects | Notes |
|------------------|-----------------|-------|
| `name` | `name` | ✅ Match |
| `interests` | `interests` | ✅ Match |
| `values` | `values` | ✅ Match |
| `imageProvider` | `image_provider` | ✅ Mapped |

| Backend Returns | Component Expects | Transformation |
|-----------------|-------------------|----------------|
| `spirit_animal` | `animal` | ✅ Mapped |
| `animal_reasoning` | `explanation` | ✅ Mapped |
| `personality_summary` | `traits[]` | ✅ Split into array |
| `image_url` | `image_url` | ✅ Pass through |


## Environment Setup

### Required Environment Variables

**Frontend (`spirit-animal-app/.env`):**
```env
VITE_API_URL=http://localhost:8000
VITE_TAMBO_API_KEY=tambo_your_key_here
```

**Backend (`spirit-animal-backend/.env`):**
```env
OPENAI_API_KEY=sk-your_openai_key_here
TWITTER_BEARER_TOKEN=optional_for_social_analysis
```

### Running the App

**Terminal 1 - Backend:**
```bash
cd spirit-animal-backend
source .venv/bin/activate
uvicorn main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd spirit-animal-app
pnpm dev
```

## Tambo API Key

Get one at [tambo.co](https://tambo.co):
- **Free tier:** 10,000 messages/month
- **Growth:** $25/mo for 200k messages

The key handles LLM costs (GPT-4.1 by default). You can configure different models in the Tambo dashboard.

## Next Steps / TODO

### 1. Debug Backend Connection
- [ ] Verify backend is running and accessible
- [ ] Check console logs for `[Tambo Tool]` messages
- [ ] Ensure CORS allows localhost:5173

### 2. Refine System Prompt
- [ ] Adjust personality/tone
- [ ] Fine-tune question flow
- [ ] Add error recovery instructions

### 3. Enhance Components
- [ ] Add loading states during tool execution
- [ ] Create additional components (e.g., AnimalComparison, TraitExplorer)
- [ ] Add animations for reveal moment

### 4. Production Considerations
- [ ] Configure allowed domains in Tambo dashboard
- [ ] Set up proper error boundaries
- [ ] Add analytics/tracking

## Useful Tambo Hooks

| Hook | Purpose |
|------|---------|
| `useTamboThread()` | Access current thread and messages |
| `useTamboThreadInput()` | Manage input state, submit messages |
| `useTamboComponentState()` | Persist component state across re-renders |
| `useTamboStreamStatus()` | Track streaming state for props |
| `useTamboRegistry()` | Dynamically register components/tools |

## Resources

- Check your MCP Tools for 'Tambo ask' with direct access to Tambo API questions, as well as a condensed Github docs MCP reference.

- [Tambo Docs](https://docs.tambo.co)
- [Tambo API Reference](https://docs.tambo.co/api-reference)
- [React Hooks Reference](https://docs.tambo.co/api-reference/react-hooks)
- [MCP Integration](https://docs.tambo.co/concepts/mcp)

## Troubleshooting

### 403 Forbidden from Tambo API
- Check API key format (should start with `tambo_`)
- Verify domain is allowed in Tambo dashboard
- Ensure key hasn't expired

### Tool calls fail silently
- Add console.log in tool function
- Check browser Network tab for failed requests
- Verify backend is running

### Component doesn't render
- Check propsSchema matches what tool returns
- Verify component is registered in `components` array
- Check for React errors in console

---

**Ma ka hana ka ʻike** - In working, one learns 🌺
