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
 * Spirit Animal Result Schema - matches what TamboSpiritAnimalCard expects
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
    - Their interests and hobbies
    - Their values and what matters to them
    The tool will analyze their profile and return a matching spirit animal.`,
    tool: async (params: {
      name: string;
      interests?: string;
      values?: string;
      imageProvider?: "none" | "openai" | "replicate";
    }) => {
      console.log("[Tambo Tool] generateSpiritAnimal called with:", params);
      
      const requestBody = {
        name: params.name,
        interests: params.interests || "",
        values: params.values || "",
        socialHandles: [],
        image_provider: params.imageProvider || "none",
      };
      
      console.log("[Tambo Tool] Sending to backend:", requestBody);
      console.log("[Tambo Tool] Backend URL:", `${API_BASE}/api/spirit-animal`);
      
      try {
        const response = await fetch(`${API_BASE}/api/spirit-animal`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(requestBody),
        });
        
        console.log("[Tambo Tool] Response status:", response.status);
        
        if (!response.ok) {
          const errorText = await response.text();
          console.error("[Tambo Tool] Backend error:", errorText);
          throw new Error(`Backend returned ${response.status}: ${errorText}`);
        }
        
        const backendResult = await response.json();
        console.log("[Tambo Tool] Backend response:", backendResult);
        
        // Transform backend response to match our schema
        const transformedResult = {
          animal: backendResult.spirit_animal,
          traits: [
            // Extract key traits from personality summary
            ...backendResult.personality_summary
              .split(/[.,]/)
              .slice(0, 3)
              .map((t: string) => t.trim())
              .filter((t: string) => t.length > 0 && t.length < 50),
          ],
          explanation: backendResult.animal_reasoning,
          image_url: backendResult.image_url || undefined,
        };
        
        console.log("[Tambo Tool] Transformed result:", transformedResult);
        return transformedResult;
        
      } catch (error) {
        console.error("[Tambo Tool] Error:", error);
        throw error;
      }
    },
    toolSchema: z
      .function()
      .args(
        z.object({
          name: z.string().describe("User's name"),
          interests: z.string().optional().describe("User's interests and hobbies"),
          values: z.string().optional().describe("User's values and what matters to them"),
          imageProvider: z.enum(["none", "openai", "replicate"]).optional().describe("Image generation provider - use 'none' for faster results"),
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
   - What are their interests and hobbies?
   - What values matter most to them?
   - What energizes them vs drains them?
3. **Reveal**: When ready, call generateSpiritAnimal with:
   - name: their name
   - interests: summary of their hobbies and interests
   - values: summary of what matters to them
   - imageProvider: "none" (for speed)

## Guidelines
- Keep questions conversational, not like a form
- Build on their answers naturally
- Don't ask more than 3 questions before generating
- Make the reveal moment feel special
- After showing results, invite them to explore or ask questions about their spirit animal

## Example Opening
"Welcome, seeker! 🌟 I'm here to help you discover your spirit animal. Before we begin this journey together, what name shall I call you?"
`;
