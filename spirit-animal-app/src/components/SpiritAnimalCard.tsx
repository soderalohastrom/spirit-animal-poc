import { useState } from 'react';
import { Share2, Download, RefreshCw, X, Check } from 'lucide-react';

export interface SpiritResult {
  personality_summary: string;
  spirit_animal: string;
  animal_reasoning: string;
  art_medium: string;
  medium_reasoning: string;
  image_url: string;
}

interface SpiritAnimalCardProps {
  result: SpiritResult;
  userName: string;
  onReset: () => void;
}

type NotificationType = 'success' | 'error' | null;

interface Notification {
  type: NotificationType;
  message: string;
}

export function SpiritAnimalCard({ result, userName, onReset }: SpiritAnimalCardProps) {
  const [notification, setNotification] = useState<Notification | null>(null);
  const [isDownloading, setIsDownloading] = useState(false);

  const showNotification = (type: 'success' | 'error', message: string) => {
    setNotification({ type, message });
    // Auto-dismiss after 4 seconds
    setTimeout(() => setNotification(null), 4000);
  };

  const dismissNotification = () => {
    setNotification(null);
  };

  const handleShare = async () => {
    const shareData = {
      title: `My Spirit Animal is a ${result.spirit_animal}!`,
      text: `I discovered my spirit animal: ${result.spirit_animal} in ${result.art_medium} style. Find yours!`,
      url: window.location.href,
    };

    if (navigator.share) {
      try {
        await navigator.share(shareData);
        showNotification('success', 'Shared successfully!');
      } catch (err) {
        // User cancelled the share dialog - not an error
        if (err instanceof Error && err.name === 'AbortError') {
          return;
        }
        console.error('Share failed:', err);
        showNotification('error', 'Failed to share. Please try again.');
      }
    } else {
      // Fallback: copy to clipboard
      try {
        await navigator.clipboard.writeText(
          `${shareData.title}\n${shareData.text}\n${shareData.url}`
        );
        showNotification('success', 'Copied to clipboard!');
      } catch (err) {
        console.error('Clipboard copy failed:', err);
        showNotification('error', 'Failed to copy to clipboard.');
      }
    }
  };

  const handleDownload = async () => {
    setIsDownloading(true);
    try {
      const response = await fetch(result.image_url);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `spirit-animal-${result.spirit_animal.toLowerCase().replace(/\s+/g, '-')}.png`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
      showNotification('success', 'Download started!');
    } catch (err) {
      console.error('Download failed:', err);
      showNotification('error', 'Failed to download image. Please try again.');
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto animate-fadeIn">
      {/* Notification Toast */}
      {notification && (
        <div
          className={`fixed top-4 left-1/2 -translate-x-1/2 z-50 flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg transition-all ${
            notification.type === 'success'
              ? 'bg-green-50 border border-green-200 text-green-800'
              : 'bg-red-50 border border-red-200 text-red-800'
          }`}
        >
          {notification.type === 'success' ? (
            <Check size={18} className="text-green-600" />
          ) : (
            <X size={18} className="text-red-600" />
          )}
          <span className="text-sm font-medium">{notification.message}</span>
          <button
            type="button"
            onClick={dismissNotification}
            className="ml-2 p-1 hover:bg-black/5 rounded transition-colors"
            aria-label="Dismiss notification"
          >
            <X size={14} />
          </button>
        </div>
      )}

      {/* Hero Image */}
      <div className="relative rounded-2xl overflow-hidden shadow-2xl mb-8">
        <img
          src={result.image_url}
          alt={result.spirit_animal}
          className="w-full aspect-square object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />
        <div className="absolute bottom-0 left-0 right-0 p-6 text-white">
          <p className="text-sm uppercase tracking-wider opacity-80 mb-1">
            {userName}'s Spirit Animal
          </p>
          <h1 className="text-4xl font-bold mb-2">{result.spirit_animal}</h1>
          <p className="text-lg opacity-90">in {result.art_medium} style</p>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3 mb-8">
        <button
          type="button"
          onClick={handleShare}
          className="flex-1 py-3 px-4 bg-purple-500 text-white rounded-lg font-medium hover:bg-purple-600 transition-colors flex items-center justify-center gap-2"
        >
          <Share2 size={20} />
          Share
        </button>
        <button
          type="button"
          onClick={handleDownload}
          disabled={isDownloading}
          className="flex-1 py-3 px-4 bg-gray-100 text-gray-700 rounded-lg font-medium hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2"
        >
          <Download size={20} />
          {isDownloading ? 'Downloading...' : 'Download'}
        </button>
      </div>

      {/* Details Cards */}
      <div className="space-y-4">
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h3 className="text-sm uppercase tracking-wider text-purple-600 font-semibold mb-2">
            Why {result.spirit_animal}?
          </h3>
          <p className="text-gray-700 leading-relaxed">{result.animal_reasoning}</p>
        </div>

        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h3 className="text-sm uppercase tracking-wider text-pink-600 font-semibold mb-2">
            Why {result.art_medium}?
          </h3>
          <p className="text-gray-700 leading-relaxed">{result.medium_reasoning}</p>
        </div>

        <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl p-6 border border-purple-100">
          <h3 className="text-sm uppercase tracking-wider text-gray-600 font-semibold mb-3">
            Your Personality Profile
          </h3>
          <p className="text-gray-700 leading-relaxed whitespace-pre-line">
            {result.personality_summary}
          </p>
        </div>
      </div>

      {/* Reset Button */}
      <button
        type="button"
        onClick={onReset}
        className="w-full mt-8 py-3 px-6 border border-gray-300 text-gray-600 rounded-lg font-medium hover:bg-gray-50 transition-colors flex items-center justify-center gap-2"
      >
        <RefreshCw size={18} />
        Start Over
      </button>
    </div>
  );
}
