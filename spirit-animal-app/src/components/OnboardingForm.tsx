import { useState } from "react";
import { Plus, Trash2 } from "lucide-react";

interface SocialHandle {
  platform: string;
  handle: string;
}

export interface UserProfile {
  name: string;
  interests: string;
  values: string;
  socialHandles: SocialHandle[];
  imageProvider: string;
}

const PLATFORMS = [
  { id: "twitter", label: "Twitter / X", placeholder: "@username" },
  { id: "reddit", label: "Reddit", placeholder: "u/username" },
  {
    id: "linkedin",
    label: "LinkedIn",
    placeholder: "linkedin.com/in/username",
  },
  { id: "instagram", label: "Instagram", placeholder: "@username" },
  { id: "tiktok", label: "TikTok", placeholder: "@username" },
  { id: "bluesky", label: "Bluesky", placeholder: "@handle.bsky.social" },
];

const IMAGE_PROVIDERS = [
  {
    id: "openai",
    label: "DALL-E 3",
    description: "OpenAI's powerful image generation",
  },
  {
    id: "gemini",
    label: "Gemini 3 Pro (Nano Banana)",
    description: "Google's Nano Banana model",
  },
];

interface OnboardingFormProps {
  onSubmit: (profile: UserProfile) => void;
  isLoading?: boolean;
}

export function OnboardingForm({ onSubmit, isLoading }: OnboardingFormProps) {
  const [profile, setProfile] = useState<UserProfile>({
    name: "",
    interests: "",
    values: "",
    socialHandles: [],
    imageProvider: "openai",
  });

  const [step, setStep] = useState(1);

  const addSocialHandle = () => {
    setProfile((p) => ({
      ...p,
      socialHandles: [...p.socialHandles, { platform: "twitter", handle: "" }],
    }));
  };

  const removeSocialHandle = (index: number) => {
    setProfile((p) => ({
      ...p,
      socialHandles: p.socialHandles.filter((_, i) => i !== index),
    }));
  };

  const updateSocialHandle = (
    index: number,
    field: "platform" | "handle",
    value: string,
  ) => {
    setProfile((p) => {
      const updated = [...p.socialHandles];
      updated[index] = { ...updated[index], [field]: value };
      return { ...p, socialHandles: updated };
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(profile);
  };

  const canProceedStep1 = profile.name.trim().length > 0;
  const canProceedStep2 =
    profile.interests.trim().length > 0 || profile.values.trim().length > 0;

  return (
    <form onSubmit={handleSubmit} className="max-w-2xl mx-auto">
      {/* Progress indicator */}
      <div className="flex items-center justify-center mb-8 gap-2">
        {[1, 2, 3].map((s) => (
          <div
            key={s}
            className={`w-3 h-3 rounded-full transition-colors ${
              s === step
                ? "bg-purple-500"
                : s < step
                  ? "bg-purple-300"
                  : "bg-gray-200"
            }`}
          />
        ))}
      </div>

      {/* Step 1: Basic Info */}
      {step === 1 && (
        <div className="space-y-6 animate-fadeIn">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-gray-800 mb-2">
              Let's get to know you
            </h2>
            <p className="text-gray-600">First, tell us your name</p>
          </div>

          <div>
            <label
              htmlFor="name"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              What should we call you?
            </label>
            <input
              id="name"
              type="text"
              placeholder="Your name or nickname"
              value={profile.name}
              onChange={(e) =>
                setProfile((p) => ({ ...p, name: e.target.value }))
              }
              className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
              autoFocus
            />
          </div>

          <button
            type="button"
            onClick={() => setStep(2)}
            disabled={!canProceedStep1}
            className="w-full py-3 px-6 bg-purple-500 text-white rounded-lg font-medium hover:bg-purple-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Continue
          </button>
        </div>
      )}

      {/* Step 2: Interests & Values */}
      {step === 2 && (
        <div className="space-y-6 animate-fadeIn">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-gray-800 mb-2">
              Tell us about yourself
            </h2>
            <p className="text-gray-600">What makes you, you?</p>
          </div>

          <div>
            <label
              htmlFor="interests"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              What are your interests and hobbies?
            </label>
            <textarea
              id="interests"
              placeholder="e.g., I love hiking, reading sci-fi novels, cooking Italian food, and playing chess..."
              value={profile.interests}
              onChange={(e) =>
                setProfile((p) => ({ ...p, interests: e.target.value }))
              }
              rows={4}
              className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all resize-none"
            />
          </div>

          <div>
            <label
              htmlFor="values"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              What do you value in life?
            </label>
            <textarea
              id="values"
              placeholder="e.g., I value honesty, creativity, spending time with family, continuous learning..."
              value={profile.values}
              onChange={(e) =>
                setProfile((p) => ({ ...p, values: e.target.value }))
              }
              rows={4}
              className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all resize-none"
            />
          </div>

          {/* Image Provider Selection */}
          <div className="mb-6">
            <label
              htmlFor="imageProvider"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Choose your image generator
            </label>
            <select
              id="imageProvider"
              value={profile.imageProvider}
              onChange={(e) =>
                setProfile((p) => ({ ...p, imageProvider: e.target.value }))
              }
              className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white"
            >
              {IMAGE_PROVIDERS.map((provider) => (
                <option key={provider.id} value={provider.id}>
                  {provider.label}
                </option>
              ))}
            </select>
            <p className="mt-2 text-sm text-gray-500">
              {
                IMAGE_PROVIDERS.find((p) => p.id === profile.imageProvider)
                  ?.description
              }
            </p>
          </div>

          <div className="flex gap-3">
            <button
              type="button"
              onClick={() => setStep(1)}
              className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors"
            >
              Back
            </button>
            <button
              type="button"
              onClick={() => setStep(3)}
              disabled={!canProceedStep2}
              className="flex-1 py-3 px-6 bg-purple-500 text-white rounded-lg font-medium hover:bg-purple-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Continue
            </button>
          </div>
        </div>
      )}

      {/* Step 3: Social Profiles */}
      {step === 3 && (
        <div className="space-y-6 animate-fadeIn">
          <div className="text-center mb-8">
            <h2 className="text-2xl font-bold text-gray-800 mb-2">
              Connect your socials
            </h2>
            <p className="text-gray-600">
              Optional: Add social profiles for a deeper analysis
            </p>
          </div>

          <div className="space-y-3">
            {profile.socialHandles.map((sh, i) => (
              <div key={i} className="flex gap-2 items-center">
                <select
                  value={sh.platform}
                  onChange={(e) =>
                    updateSocialHandle(i, "platform", e.target.value)
                  }
                  className="px-3 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white"
                >
                  {PLATFORMS.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.label}
                    </option>
                  ))}
                </select>
                <input
                  type="text"
                  placeholder={
                    PLATFORMS.find((p) => p.id === sh.platform)?.placeholder
                  }
                  value={sh.handle}
                  onChange={(e) =>
                    updateSocialHandle(i, "handle", e.target.value)
                  }
                  className="flex-1 px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                />
                <button
                  type="button"
                  onClick={() => removeSocialHandle(i)}
                  className="p-2 text-gray-400 hover:text-red-500 transition-colors"
                >
                  <Trash2 size={20} />
                </button>
              </div>
            ))}
          </div>

          <button
            type="button"
            onClick={addSocialHandle}
            className="w-full py-3 px-6 border-2 border-dashed border-gray-300 text-gray-600 rounded-lg font-medium hover:border-purple-400 hover:text-purple-600 transition-colors flex items-center justify-center gap-2"
          >
            <Plus size={20} />
            Add Social Profile
          </button>

          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={() => setStep(2)}
              className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors"
            >
              Back
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="flex-1 py-3 px-6 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg font-medium hover:from-purple-600 hover:to-pink-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {isLoading ? "Discovering..." : "Discover My Spirit Animal"}
            </button>
          </div>
        </div>
      )}
    </form>
  );
}
