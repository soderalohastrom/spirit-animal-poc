/**
 * @file tambo.ts
 * @description Tambo configuration - components and tools for conversational UI
 * 
 * This transforms the Spirit Animal app from form-based to conversation-based.
 * The AI guides users through discovery via natural dialogue, rendering
 * appropriate components based on the conversation flow.
 */

import { TamboSpiritAnimalCard } from "@/components/TamboSpiritAnimalCard";
import type { TamboComponent, TamboTool } from "@tambo-ai/react";
import { z } from "zod";

// API base URL
const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

/**
 * Spirit Animal Result Schema
 */
const spiritResultSchema = z.object({
  animal: z.string().describe("The spirit animal name"),
  traits: z.array(z.string()).describe("Key personality traits that match this animal"),
  explanation: z.string().describe("Why this animal matches the user"),
  image_url: z.string().optional().describe("URL to the generated spirit animal image"),
});

/**
 * Tools - Functions the AI can call to fetch data or perform actions
 */
export const tools: TamboTool[] = [
  {
    name: "generateSpiritAnimal",
    description: `Generate a spirit animal based on user profile information. 
    Call this when you have gathered enough information about the user including:
    - Their name
    - Personality traits or self-description
    - Optionally their social media handle for deeper analysis
    The tool will analyze their profile and return a matching spirit animal.`,
    tool: async (params: {
      name: string;
      personality?: string;
      hobbies?: string;
      socialHandle?: string;
      imageProvider?: "none" | "dalle" | "replicate";
    }) => {
      const response = await fetch(`${API_BASE}/api/spirit-animal`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: params.name,
          personality: params.personality || "",
          hobbies: params.hobbies || "",
          social_handle: params.socialHandle || "",
          image_provider: params.imageProvider || "none",
        }),
      });
      
      if (!response.ok) {
        throw new Error("Failed to generate spirit animal");
      }
      
      return await response.json();
    },
    toolSchema: z
      .function()
      .args(
        z.object({
          name: z.string().describe("User's name"),
          personality: z.string().optional().describe("User's personality traits or self-description"),
          hobbies: z.string().optional().describe("User's hobbies and interests"),
          socialHandle: z.string().optional().describe("Social media handle (Twitter/X) for deeper analysis"),
          imageProvider: z.enum(["none", "dalle", "replicate"]).optional().describe("Image generation provider"),
        })
      )
      .returns(spiritResultSchema),
  },
];

/**
 * Components - React components the AI can render
 */
export const components: TamboComponent[] = [
  {
    name: "SpiritAnimalCard",
    description: `Displays a spirit animal result with the animal name, matching traits, 
    a personalized explanation of why this animal matches the user, and optionally 
    an AI-generated image. Use this component after calling generateSpiritAnimal 
    to show the user their result.`,
    component: TamboSpiritAnimalCard,
    propsSchema: z.object({
      result: spiritResultSchema,
      userName: z.string().describe("The user's name to personalize the card"),
    }),
  },
];

/**
 * System prompt for the Spirit Animal discovery conversation
 */
export const SPIRIT_ANIMAL_SYSTEM_PROMPT = `You are a friendly and intuitive Spirit Animal Guide. Your role is to help users discover their spirit animal through engaging conversation.

## Your Personality
- Warm, curious, and slightly mystical
- Ask thoughtful questions that reveal personality
- Be encouraging and make the experience fun
- Use occasional animal-related metaphors

## Conversation Flow
1. **Greeting**: Welcome the user warmly and ask their name
2. **Discovery**: Ask 2-3 engaging questions to understand them:
   - What energizes them vs drains them
   - How they approach challenges
   - What qualities they admire in others
   - Their favorite way to spend free time
3. **Optional Deep Dive**: If they mention social media, offer to analyze their profile for deeper insights
4. **Reveal**: When ready, call generateSpiritAnimal with gathered info, then render the SpiritAnimalCard

## Guidelines
- Keep questions conversational, not like a form
- Build on their answers naturally
- Don't ask more than 3 questions before generating
- Make the reveal moment feel special
- After showing results, invite them to explore or ask questions about their spirit animal

## Example Opening
"Welcome, seeker! 🌟 I'm here to help you discover your spirit animal. Before we begin this journey together, what name shall I call you?"
`;
