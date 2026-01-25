/**
 * @file tambo.ts
 * @description Tambo configuration for V2 conversational Spirit Animal discovery
 *
 * The 7-turn conversation flow gathers rich personality data that maps directly
 * to the backend's interpretation framework. Questions are designed to reveal:
 * - Energy mode (Power/Grace/Wisdom animal categories)
 * - Social dynamics (solitary vs social animals)
 * - Self-description (their exact words)
 * - Joy sources (lifestyle + interests)
 * - Aspirations (values + direction)
 * - Element affinity (artistic setting + palette)
 */

import { TamboSpiritAnimalCard } from "@/components/TamboSpiritAnimalCard";
import type { TamboComponent, TamboTool } from "@tambo-ai/react";
import { z } from "zod";

// API base URL
const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

// =============================================================================
// TYPES & SCHEMAS
// =============================================================================

/** Structured data gathered during conversation */
interface ConversationData {
  name: string;
  pronouns: "he/him" | "she/her" | "they/them" | "unspecified";
  energyMode: "leader" | "adapter" | "observer";
  socialPattern: "solitude" | "close_circle" | "crowd";
  selfDescription: string;
  joySource: string;
  aspirations: string;
  elementAffinity: "fire" | "water" | "earth" | "air";
}

/** V2 API request schema */
const spiritRequestV2Schema = z.object({
  personality_summary: z.string(),
  pronouns: z.enum(["he/him", "she/her", "they/them", "unspecified"]).optional(),
  energy_mode: z.enum(["leader", "adapter", "observer"]).optional(),
  social_pattern: z.enum(["solitude", "close_circle", "crowd"]).optional(),
  element_affinity: z.enum(["fire", "water", "earth", "air"]).optional(),
  image_provider: z.enum(["openai", "gemini", "ideogram", "none"]).optional(),
  skip_image: z.boolean().optional(),
});

/** Spirit Animal Result Schema - matches V2 response + TamboSpiritAnimalCard */
const spiritResultSchema = z.object({
  animal: z.string().describe("The spirit animal name (e.g., 'Arctic Fox')"),
  animalReasoning: z.string().describe("Why this animal matches the user"),
  artMedium: z.string().describe("The artistic medium/style chosen"),
  mediumReasoning: z.string().describe("Why this medium captures their essence"),
  imageUrl: z.string().nullable().describe("URL to the generated spirit animal image"),
  imagePrompt: z.string().describe("The prompt used for image generation"),
});

// =============================================================================
// HELPER FUNCTIONS
// =============================================================================

/**
 * Assemble the rich personality summary from conversation data.
 * This format is designed to feed the backend's interpretation prompt.
 */
function assemblePersonalitySummary(data: ConversationData): string {
  const pronounLabel = data.pronouns === "unspecified" ? "" : ` (${data.pronouns})`;

  const energyDescriptions: Record<string, string> = {
    leader: "leads from the front when facing challenges, taking charge and making decisive moves",
    adapter: "adapts and maneuvers through challenges, finding clever paths rather than forcing through",
    observer: "observes first before acting, taking time to understand situations deeply",
  };

  const socialDescriptions: Record<string, string> = {
    solitude: "quiet time alone",
    close_circle: "a close circle of trusted people",
    crowd: "the energy of being around others",
  };

  const elementDescriptions: Record<string, string> = {
    fire: "Fire energy—passion, transformation, and intensity",
    water: "Water energy—depth, flow, and emotional resonance",
    earth: "Earth energy—stability, growth, and grounding",
    air: "Air energy—freedom, possibility, and lightness",
  };

  return `${data.name}${pronounLabel} describes themselves as "${data.selfDescription}".

Energy & Approach: They ${energyDescriptions[data.energyMode]}. When they need to recharge, they seek ${socialDescriptions[data.socialPattern]}.

What brings them joy: ${data.joySource}

What they're working toward: ${data.aspirations}

They're drawn to ${elementDescriptions[data.elementAffinity]}.`;
}

// =============================================================================
// TOOLS
// =============================================================================

export const tools: TamboTool[] = [
  {
    name: "generateSpiritAnimal",
    description: `Generate a spirit animal based on the complete personality profile gathered during conversation.

Call this tool ONLY after gathering ALL of the following:
1. Name and pronouns
2. Energy mode (leader/adapter/observer)
3. Social pattern (solitude/close_circle/crowd)
4. Self-description (their exact words)
5. Joy source (what brings genuine joy)
6. Aspirations (what matters most, what they're working toward)
7. Element affinity (fire/water/earth/air)

The tool will assemble a rich personality summary and send it to the V2 backend for interpretation.`,

    tool: async (params: {
      name: string;
      pronouns: "he/him" | "she/her" | "they/them" | "unspecified";
      energyMode: "leader" | "adapter" | "observer";
      socialPattern: "solitude" | "close_circle" | "crowd";
      selfDescription: string;
      joySource: string;
      aspirations: string;
      elementAffinity: "fire" | "water" | "earth" | "air";
      imageProvider?: "openai" | "gemini" | "ideogram" | "none";
    }) => {
      console.log("[Tambo Tool V2] generateSpiritAnimal called with:", params);

      // Assemble the rich personality summary
      const personalitySummary = assemblePersonalitySummary(params);
      console.log("[Tambo Tool V2] Assembled summary:", personalitySummary);

      // Build V2 request
      const requestBody = {
        personality_summary: personalitySummary,
        pronouns: params.pronouns,
        energy_mode: params.energyMode,
        social_pattern: params.socialPattern,
        element_affinity: params.elementAffinity,
        image_provider: params.imageProvider || "gemini",
        skip_image: false,
      };

      console.log("[Tambo Tool V2] Sending to V2 endpoint:", requestBody);

      try {
        const response = await fetch(`${API_BASE}/api/spirit-animal/v2`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(requestBody),
        });

        console.log("[Tambo Tool V2] Response status:", response.status);

        if (!response.ok) {
          const errorText = await response.text();
          console.error("[Tambo Tool V2] Backend error:", errorText);
          throw new Error(`Backend returned ${response.status}: ${errorText}`);
        }

        const backendResult = await response.json();
        console.log("[Tambo Tool V2] Backend response:", backendResult);

        // Transform V2 response to match our schema
        const result = {
          animal: backendResult.spirit_animal,
          animalReasoning: backendResult.animal_reasoning,
          artMedium: backendResult.art_medium,
          mediumReasoning: backendResult.medium_reasoning,
          imageUrl: backendResult.image_url,
          imagePrompt: backendResult.image_prompt,
        };

        console.log("[Tambo Tool V2] Transformed result:", result);
        return result;
      } catch (error) {
        console.error("[Tambo Tool V2] Error:", error);
        throw error;
      }
    },

    // Transform the tool result into content that guides the AI to render the component
    transformToContent: (result: {
      animal: string;
      animalReasoning: string;
      artMedium: string;
      mediumReasoning: string;
      imageUrl: string | null;
      imagePrompt: string;
    }) => {
      console.log("[Tambo Tool V2] transformToContent called with:", result);
      console.log("[Tambo Tool V2] imageUrl value:", result.imageUrl);
      
      // Include ALL data in the text so Tambo LLM can pass it to the component
      const imageInfo = result.imageUrl 
        ? `**Image URL:** ${result.imageUrl}\n` 
        : "**Image:** Not generated\n";
      
      return [
        {
          type: "text" as const,
          text: `Spirit animal generated successfully!

**Animal:** ${result.animal}
**Why:** ${result.animalReasoning}

**Art Style:** ${result.artMedium}
**Why this style:** ${result.mediumReasoning}

${imageInfo}
**Image Prompt:** ${result.imagePrompt}

Now render the SpiritAnimalCard component with these exact values:
- animal: "${result.animal}"
- animalReasoning: "${result.animalReasoning}"
- artMedium: "${result.artMedium}"
- mediumReasoning: "${result.mediumReasoning}"
- imageUrl: ${result.imageUrl ? `"${result.imageUrl}"` : "null"}
- imagePrompt: "${result.imagePrompt}"`,
        },
      ];
    },

    toolSchema: z
      .function()
      .args(
        z.object({
          name: z.string().describe("User's name"),
          pronouns: z
            .enum(["he/him", "she/her", "they/them", "unspecified"])
            .describe("User's pronouns"),
          energyMode: z
            .enum(["leader", "adapter", "observer"])
            .describe("How they approach challenges: leader (take charge), adapter (find clever paths), observer (understand first)"),
          socialPattern: z
            .enum(["solitude", "close_circle", "crowd"])
            .describe("How they recharge: solitude (alone), close_circle (few trusted people), crowd (social energy)"),
          selfDescription: z
            .string()
            .describe("Their exact words describing themselves"),
          joySource: z
            .string()
            .describe("What activities or moments bring genuine joy"),
          aspirations: z
            .string()
            .describe("What matters most to them right now, what they're working toward"),
          elementAffinity: z
            .enum(["fire", "water", "earth", "air"])
            .describe("Which element calls to them: fire (passion), water (depth), earth (stability), air (freedom)"),
          imageProvider: z
            .enum(["openai", "gemini", "ideogram", "none"])
            .optional()
            .describe("Image generation provider - defaults to 'openai'"),
        })
      )
      .returns(spiritResultSchema),
  },
];

// =============================================================================
// COMPONENTS
// =============================================================================

export const components: TamboComponent[] = [
  {
    name: "SpiritAnimalCard",
    description: `Displays the complete spirit animal result including:
- The spirit animal name and why it matches the user
- The artistic medium chosen and why it captures their essence
- The AI-generated image (if available)

Use this component after calling generateSpiritAnimal to reveal the user's spirit animal.
Pass all props flat (not nested under 'result').`,
    component: TamboSpiritAnimalCard,
    propsSchema: z.object({
      animal: z.string().describe("The spirit animal name (e.g., 'Arctic Fox')"),
      animalReasoning: z.string().describe("Why this animal matches the user"),
      artMedium: z.string().describe("The artistic medium/style chosen"),
      mediumReasoning: z.string().describe("Why this medium captures their essence"),
      imageUrl: z.string().nullable().describe("URL to the generated spirit animal image"),
      imagePrompt: z.string().describe("The prompt used for image generation"),
      userName: z.string().describe("The user's name to personalize the card"),
    }),
  },
];

// =============================================================================
// SYSTEM PROMPT
// =============================================================================

export const SPIRIT_ANIMAL_SYSTEM_PROMPT = `You are a warm, intuitive Spirit Animal Guide. Your role is to help users discover their spirit animal through a brief, meaningful conversation.

## Your Personality
- Warm and welcoming, with a touch of mystical wisdom
- Ask ONE question at a time, then wait for the answer
- Build on their responses naturally—this is a conversation, not a form
- Use their exact words back to them when it resonates

## Response Format: Multiple Choice
Present options as A, B, C, D (and E when needed). Users can respond with:
- Just the letter: "a", "A", "b", "B", etc.
- The full text: "Lead from the front"
- Their own words if they choose "Other"

Accept lowercase single letters — many users will just type "a" + enter quickly.

## The Conversation Flow

### Question 1: Name
The initial welcome message already asks for their name. When they respond, acknowledge warmly and move to Question 2.

### Question 2: Energy Mode
"When facing a challenge, [Name], how do you typically respond?

A) Lead from the front — take charge, make decisions
B) Adapt and maneuver — find the clever path through
C) Observe first — understand before acting
D) Other — tell me in your own words"

*Wait for their choice.*

### Question 3: Social Pattern
"When you need to recharge your energy, what do you seek?

A) Solitude — quiet time alone
B) Close circle — a few people you trust deeply
C) The crowd — energy from being around others
D) Other — describe what works for you"

*Wait for their choice.*

### Question 4: Self-Description
"In just a few words, how would someone who truly knows you describe you?"

*Open-ended. This is the heart of their profile. Wait for their words.*

### Question 5: Joy Source
"What brings you the most genuine joy?

A) Creating things — making, building, expressing
B) Connecting — deep conversations, relationships
C) Exploring — learning, discovering, experiencing
D) Being in nature — outdoors, animals, natural world
E) Other — tell me what lights you up"

*Wait for their choice. If they pick E, capture their words.*

### Question 6: Aspirations
"What matters most to you right now? What are you working toward?"

*Open-ended. This reveals values and direction. Wait for their response.*

### Question 7: Element Affinity
"Last one. Which element calls to you most?

A) Fire — passion, transformation, intensity
B) Water — depth, flow, emotional resonance
C) Earth — stability, growth, grounding
D) Air — freedom, possibility, lightness
E) Other — something else speaks to you?"

*Wait for their choice.*

## The Reveal

Once you have ALL the information (name, energy mode, social pattern, self-description, joy source, aspirations, element), call generateSpiritAnimal with the complete data.

Make the reveal moment special:
"The spirits have spoken, [Name]... your spirit animal is revealing itself..."

**IMPORTANT: After the tool returns, you MUST render the SpiritAnimalCard component** with these props:
- animal: the spirit animal name from the tool result
- animalReasoning: why this animal matches them
- artMedium: the artistic style chosen
- mediumReasoning: why this style was chosen
- imageUrl: the generated image URL (may be a base64 data URL)
- imagePrompt: the prompt used for image generation
- userName: the user's name you collected in Question 1

After showing the card, invite them to reflect:
"What do you think? Does [animal] resonate with you?"

## Mapping Responses

**Energy Mode (Question 2):**
- A or "lead" → energyMode: "leader"
- B or "adapt" → energyMode: "adapter"
- C or "observe" → energyMode: "observer"
- D (other) → Map to closest: leader/adapter/observer based on their words

**Social Pattern (Question 3):**
- A or "solitude" → socialPattern: "solitude"
- B or "close" → socialPattern: "close_circle"
- C or "crowd" → socialPattern: "crowd"
- D (other) → Map to closest based on their words

**Joy Source (Question 5):**
- Capture their choice or freeform text for joySource field

**Element Affinity (Question 7):**
- A → elementAffinity: "fire"
- B → elementAffinity: "water"
- C → elementAffinity: "earth"
- D → elementAffinity: "air"
- E (other) → Map to closest element based on their description

**Pronouns:** Use "unspecified" unless explicitly mentioned.

## Important Guidelines

- Ask ONE question per message, then WAIT
- Never skip questions or combine multiple questions
- Accept single letters (a, b, c, d, e) as valid responses
- Use their exact self-description words when calling the tool
- Keep each message concise—don't over-explain
- If they give a very short answer on open-ended questions, gently probe: "Tell me a bit more?"

## Example Conversation

**User:** "I'm Maya"

**You:** "Lovely to meet you, Maya! ✨

When facing a challenge, how do you typically respond?

A) Lead from the front — take charge, make decisions
B) Adapt and maneuver — find the clever path through
C) Observe first — understand before acting
D) Other — tell me in your own words"

**User:** "b"

**You:** "A navigator of possibilities — I like that.

When you need to recharge, what do you seek?

A) Solitude — quiet time alone
B) Close circle — a few people you trust deeply
C) The crowd — energy from being around others
D) Other — describe what works for you"

**User:** "a"

**You:** "Solitude it is. Now, in just a few words, how would someone who truly knows you describe you?"

...and so on through all the questions.
`;
