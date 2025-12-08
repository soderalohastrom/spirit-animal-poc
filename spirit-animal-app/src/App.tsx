import { useState } from "react";
import { OnboardingForm, UserProfile } from "./components/OnboardingForm";
import { SpiritAnimalCard, SpiritResult } from "./components/SpiritAnimalCard";
import { LoadingState } from "./components/LoadingState";

type AppState = "form" | "loading" | "result";

// API base URL - change this for production
const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

function App() {
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
          <p className="text-gray-600">Discover your inner creature</p>
        </div>
      </header>

      {/* Main Content */}
      <main className="px-4 pb-16">
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
      </main>

      {/* Footer */}
      <footer className="py-6 text-center text-gray-400 text-sm">
        <p>Made with AI for fun</p>
      </footer>
    </div>
  );
}

export default App;
