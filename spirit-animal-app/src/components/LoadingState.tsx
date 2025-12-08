import { useState, useEffect } from 'react';

const LOADING_MESSAGES = [
  'Analyzing your personality...',
  'Consulting the animal kingdom...',
  'Finding your perfect match...',
  'Choosing an artistic style...',
  'Summoning your spirit animal...',
  'Creating your unique portrait...',
  'Adding the finishing touches...',
];

export function LoadingState() {
  const [messageIndex, setMessageIndex] = useState(0);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const messageInterval = setInterval(() => {
      setMessageIndex((i) => (i + 1) % LOADING_MESSAGES.length);
    }, 3000);

    const progressInterval = setInterval(() => {
      setProgress((p) => Math.min(p + Math.random() * 5, 95));
    }, 500);

    return () => {
      clearInterval(messageInterval);
      clearInterval(progressInterval);
    };
  }, []);

  return (
    <div className="max-w-md mx-auto text-center py-16 animate-fadeIn">
      {/* Animated animal silhouettes */}
      <div className="relative w-32 h-32 mx-auto mb-8">
        <div className="absolute inset-0 rounded-full bg-gradient-to-br from-purple-400 to-pink-400 animate-pulse" />
        <div className="absolute inset-2 rounded-full bg-white flex items-center justify-center">
          <svg
            className="w-16 h-16 text-purple-500 animate-bounce"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"
            />
          </svg>
        </div>
      </div>

      {/* Loading message */}
      <p className="text-lg text-gray-600 mb-6 h-7 transition-opacity duration-300">
        {LOADING_MESSAGES[messageIndex]}
      </p>

      {/* Progress bar */}
      <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-purple-500 to-pink-500 transition-all duration-500 ease-out"
          style={{ width: `${progress}%` }}
        />
      </div>
      <p className="text-sm text-gray-400 mt-2">This may take a minute...</p>
    </div>
  );
}
