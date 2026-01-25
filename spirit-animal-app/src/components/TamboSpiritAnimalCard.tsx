/**
 * @file TamboSpiritAnimalCard.tsx
 * @description V2 Spirit Animal result card for Tambo conversational flow
 *
 * Displays the complete spirit animal interpretation including:
 * - Spirit animal name and reasoning
 * - Artistic medium and why it was chosen
 * - AI-generated image (if available)
 */

import { Share2, Download, Sparkles, Palette, Loader2 } from "lucide-react";
import { useState } from "react";

/**
 * Flat props interface for Tambo compatibility.
 * Tambo LLMs work better with flat props than nested objects.
 */
export interface TamboSpiritAnimalCardProps {
  animal: string;
  animalReasoning: string;
  artMedium: string;
  mediumReasoning: string;
  imageUrl: string | null;
  imagePrompt: string;
  userName: string;
}

export function TamboSpiritAnimalCard(props: TamboSpiritAnimalCardProps) {
  const { animal, animalReasoning, artMedium, mediumReasoning, imageUrl, imagePrompt, userName } = props;
  const [imageError, setImageError] = useState(false);
  const [imageLoading, setImageLoading] = useState(true);
  const [showDetails, setShowDetails] = useState(false);

  // Debug logging - always log props on render
  console.log("[TamboSpiritAnimalCard] Rendered with props:", {
    animal,
    imageUrl: imageUrl ? `${imageUrl.substring(0, 80)}...` : null,
    imageUrlType: imageUrl ? (imageUrl.startsWith("data:") ? "base64" : "url") : "null",
    userName,
  });

  // Defensive check - if animal is undefined, show error state
  if (!animal) {
    console.error("[TamboSpiritAnimalCard] props are incomplete", props);
    return (
      <div className="bg-white rounded-xl overflow-hidden shadow-lg border border-red-200 max-w-md p-6">
        <p className="text-red-600 font-medium">Unable to display spirit animal result.</p>
        <p className="text-gray-500 text-sm mt-2">The result data was not received properly. Please try again.</p>
      </div>
    );
  }

  const handleShare = async () => {
    const shareText = `My spirit animal is the ${animal}!\n\n${animalReasoning}\n\nArtistic style: ${artMedium}\n\nDiscover yours!`;

    if (navigator.share) {
      try {
        await navigator.share({
          title: `My Spirit Animal: ${animal}`,
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

  const hasImage = imageUrl && !imageError;

  return (
    <div className="bg-white rounded-xl overflow-hidden shadow-lg border border-purple-100 max-w-md">
      {/* Image Section */}
      {imageUrl && !imageError ? (
        <div className="relative aspect-square bg-gray-100">
          {imageLoading && (
            <div className="absolute inset-0 flex items-center justify-center bg-gradient-to-br from-purple-100 to-pink-100">
              <div className="text-center">
                <Loader2 className="w-8 h-8 mx-auto mb-2 text-purple-500 animate-spin" />
                <p className="text-sm text-purple-600">
                  Revealing your spirit animal...
                </p>
              </div>
            </div>
          )}
          <img
            src={imageUrl}
            alt={animal}
            className={`w-full h-full object-cover transition-opacity duration-500 ${
              imageLoading ? "opacity-0" : "opacity-100"
            }`}
            onLoad={() => setImageLoading(false)}
            onError={() => {
              setImageError(true);
              setImageLoading(false);
            }}
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />
          <div className="absolute bottom-4 left-4 right-4 text-white">
            <p className="text-sm opacity-80">{userName}'s Spirit Animal</p>
            <h3 className="text-2xl font-bold">{animal}</h3>
          </div>
        </div>
      ) : (
        <div className="aspect-video bg-gradient-to-br from-purple-500 via-purple-600 to-pink-500 flex items-center justify-center">
          <div className="text-center text-white p-6">
            <Sparkles className="w-12 h-12 mx-auto mb-3" />
            <p className="text-sm opacity-80 mb-1">{userName}'s Spirit Animal</p>
            <h3 className="text-3xl font-bold">{animal}</h3>
          </div>
        </div>
      )}

      {/* Content */}
      <div className="p-5 space-y-4">
        {/* Animal Reasoning */}
        <div>
          <h4 className="text-sm font-semibold text-purple-700 uppercase tracking-wide mb-2">
            Why This Animal
          </h4>
          <p className="text-gray-700 leading-relaxed">{animalReasoning}</p>
        </div>

        {/* Artistic Medium */}
        <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-2">
            <Palette className="w-4 h-4 text-purple-600" />
            <h4 className="text-sm font-semibold text-purple-700 uppercase tracking-wide">
              Artistic Style
            </h4>
          </div>
          <p className="font-medium text-gray-800 mb-1">{artMedium}</p>
          <p className="text-sm text-gray-600">{mediumReasoning}</p>
        </div>

        {/* Expandable Details */}
        <button
          onClick={() => setShowDetails(!showDetails)}
          className="text-sm text-purple-600 hover:text-purple-800 transition-colors"
        >
          {showDetails ? "Hide details" : "Show image prompt details"}
        </button>

        {showDetails && (
          <div className="bg-gray-50 rounded-lg p-3 text-xs text-gray-600 font-mono space-y-2">
            <div>
              <p className="mb-1 font-sans text-gray-500 text-[10px] uppercase tracking-wider">
                Image Generation Prompt
              </p>
              {imagePrompt}
            </div>
            {imageUrl && (
              <div>
                <p className="mb-1 font-sans text-gray-500 text-[10px] uppercase tracking-wider">
                  Image URL
                </p>
                <a 
                  href={imageUrl} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-purple-600 hover:underline break-all"
                >
                  {imageUrl.startsWith("data:") ? "[Base64 Data URL]" : imageUrl}
                </a>
              </div>
            )}
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-2 pt-2">
          <button
            onClick={handleShare}
            className="flex-1 py-2.5 px-4 bg-purple-600 text-white rounded-lg text-sm font-medium hover:bg-purple-700 transition-colors flex items-center justify-center gap-2"
          >
            <Share2 className="w-4 h-4" />
            Share Result
          </button>
          {hasImage && (
            <a
              href={imageUrl!}
              download={`spirit-animal-${animal.toLowerCase().replace(/\s+/g, "-")}.png`}
              target="_blank"
              rel="noopener noreferrer"
              className="py-2.5 px-4 bg-gray-100 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-200 transition-colors flex items-center justify-center gap-2"
            >
              <Download className="w-4 h-4" />
            </a>
          )}
        </div>
      </div>
    </div>
  );
}
