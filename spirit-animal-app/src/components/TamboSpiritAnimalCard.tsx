/**
 * @file TamboSpiritAnimalCard.tsx
 * @description Tambo-compatible Spirit Animal result card
 * 
 * A simplified version that works with Tambo's prop passing.
 * The AI generates the props and this component renders them beautifully.
 */

import { Share2, Download, Sparkles } from "lucide-react";
import { useState } from "react";

export interface TamboSpiritResult {
  animal: string;
  traits: string[];
  explanation: string;
  image_url?: string;
}

interface TamboSpiritAnimalCardProps {
  result: TamboSpiritResult;
  userName: string;
}

export function TamboSpiritAnimalCard({ result, userName }: TamboSpiritAnimalCardProps) {
  const [imageError, setImageError] = useState(false);

  const handleShare = async () => {
    const shareText = `🦁 My spirit animal is a ${result.animal}!\n\nTraits: ${result.traits.join(", ")}\n\nDiscover yours!`;
    
    if (navigator.share) {
      try {
        await navigator.share({
          title: `My Spirit Animal: ${result.animal}`,
          text: shareText,
          url: window.location.href,
        });
      } catch (err) {
        console.log("Share cancelled");
      }
    } else {
      await navigator.clipboard.writeText(shareText);
      alert("Copied to clipboard!");
    }
  };

  return (
    <div className="bg-white rounded-xl overflow-hidden shadow-lg border border-purple-100 max-w-md">
      {/* Image or Placeholder */}
      {result.image_url && !imageError ? (
        <div className="relative aspect-square">
          <img
            src={result.image_url}
            alt={result.animal}
            className="w-full h-full object-cover"
            onError={() => setImageError(true)}
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent" />
          <div className="absolute bottom-4 left-4 text-white">
            <p className="text-sm opacity-80">{userName}'s Spirit Animal</p>
            <h3 className="text-2xl font-bold">{result.animal}</h3>
          </div>
        </div>
      ) : (
        <div className="aspect-video bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
          <div className="text-center text-white">
            <Sparkles className="w-12 h-12 mx-auto mb-2" />
            <p className="text-sm opacity-80">{userName}'s Spirit Animal</p>
            <h3 className="text-3xl font-bold">{result.animal}</h3>
          </div>
        </div>
      )}

      {/* Content */}
      <div className="p-5">
        {/* Traits */}
        <div className="flex flex-wrap gap-2 mb-4">
          {result.traits.map((trait, i) => (
            <span
              key={i}
              className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm font-medium"
            >
              {trait}
            </span>
          ))}
        </div>

        {/* Explanation */}
        <p className="text-gray-700 leading-relaxed mb-4">{result.explanation}</p>

        {/* Actions */}
        <div className="flex gap-2">
          <button
            onClick={handleShare}
            className="flex-1 py-2 px-4 bg-purple-600 text-white rounded-lg text-sm font-medium hover:bg-purple-700 transition-colors flex items-center justify-center gap-2"
          >
            <Share2 className="w-4 h-4" />
            Share
          </button>
          {result.image_url && !imageError && (
            <a
              href={result.image_url}
              download={`spirit-animal-${result.animal.toLowerCase()}.png`}
              className="py-2 px-4 bg-gray-100 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-200 transition-colors flex items-center justify-center gap-2"
            >
              <Download className="w-4 h-4" />
            </a>
          )}
        </div>
      </div>
    </div>
  );
}
