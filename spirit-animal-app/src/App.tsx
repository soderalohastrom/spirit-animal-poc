/**
 * @file App.tsx
 * @description Spirit Animal App with dual mode: Form or Conversational Chat
 * 
 * Toggle between the traditional form-based flow and the new
 * AI-guided conversational experience powered by Tambo.
 */

import { useState } from "react";
import { TamboProvider } from "@tambo-ai/react";
import { OnboardingForm, UserProfile } from "./components/OnboardingForm";
import { SpiritAnimalCard, SpiritResult } from "./components/SpiritAnimalCard";
import { LoadingState } from "./components/LoadingState";
import { SpiritAnimalChat } from "./components/chat";
import { components, tools, SPIRIT_ANIMAL_SYSTEM_PROMPT } from "./lib/tambo";
import { MessageSquare, ClipboardList } from "lucide-react";

/**
 * Context helper that provides the Spirit Animal Guide instructions.
 * This gives the AI its personality and conversation flow.
 */
const spiritAnimalContextHelper = () => ({
  role: "Spirit Animal Guide",
  instructions: SPIRIT_ANIMAL_SYSTEM_PROMPT,
});

type AppState = "form" | "loading" | "result";
type AppMode = "form" | "chat";

// API base URL - change this for production
const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

// Tambo API Key
const TAMBO_API_KEY = import.meta.env.VITE_TAMBO_API_KEY || "";

function App() {
  const [mode, setMode] = useState<AppMode>("chat"); // Default to chat mode
  const [appState, setAppState] = useState<AppState>("form");
  const [result, setResult] = useState<SpiritResult | null>(null);
  const [userName, setUserName] = useState("");
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (profile: UserProfile) => {
    setUserName(profile.name);
    setAppState("loading");
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/api/spirit-animal`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          ...profile,
          image_provider: profile.imageProvider,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to generate spirit animal");
      }

      const data: SpiritResult = await response.json();
      setResult(data);
      setAppState("result");
    } catch (err) {
      console.error("Error:", err);
      setError(err instanceof Error ? err.message : "Something went wrong");
      setAppState("form");
    }
  };

  const handleReset = () => {
    setResult(null);
    setUserName("");
    setAppState("form");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-pink-50">
      {/* Header */}
      <header className="py-8 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent mb-2">
            Spirit Animal
          </h1>
          <p className="text-gray-600 mb-6">Discover your inner creature</p>

          {/* Mode Toggle */}
          <div className="inline-flex bg-white rounded-lg p-1 shadow-sm border border-purple-100">
            <button
              onClick={() => setMode("chat")}
              className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${
                mode === "chat"
                  ? "bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-sm"
                  : "text-gray-600 hover:text-purple-600"
              }`}
            >
              <MessageSquare className="w-4 h-4" />
              Chat
            </button>
            <button
              onClick={() => setMode("form")}
              className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all ${
                mode === "form"
                  ? "bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-sm"
                  : "text-gray-600 hover:text-purple-600"
              }`}
            >
              <ClipboardList className="w-4 h-4" />
              Form
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="px-4 pb-16">
        {mode === "chat" ? (
          /* Conversational Mode with Tambo */
          <TamboProvider
            apiKey={TAMBO_API_KEY}
            components={components}
            tools={tools}
            contextHelpers={{
              spiritGuide: spiritAnimalContextHelper,
            }}
          >
            <SpiritAnimalChat />
          </TamboProvider>
        ) : (
          /* Traditional Form Mode */
          <>
            {error && (
              <div className="max-w-2xl mx-auto mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
                {error}
              </div>
            )}

            {appState === "form" && (
              <OnboardingForm onSubmit={handleSubmit} isLoading={false} />
            )}

            {appState === "loading" && <LoadingState />}

            {appState === "result" && result && (
              <SpiritAnimalCard
                result={result}
                userName={userName}
                onReset={handleReset}
              />
            )}
          </>
        )}
      </main>

      {/* Footer */}
      <footer className="py-6 text-center text-gray-400 text-sm">
        <p>Made with AI for fun • {mode === "chat" ? "Powered by Tambo" : "Classic Mode"}</p>
      </footer>
    </div>
  );
}

export default App;
