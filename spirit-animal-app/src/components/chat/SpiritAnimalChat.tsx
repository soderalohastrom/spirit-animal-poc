/**
 * @file SpiritAnimalChat.tsx
 * @description Conversational interface for Spirit Animal discovery
 * 
 * This replaces the traditional form with an AI-guided conversation
 * that feels more personal and engaging.
 */

import { useTamboThread, useTamboThreadInput } from "@tambo-ai/react";
import { Send, Sparkles } from "lucide-react";
import { useEffect, useRef } from "react";

export function SpiritAnimalChat() {
  const { thread } = useTamboThread();
  const { value, setValue, submit, isPending } = useTamboThreadInput();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [thread.messages]);

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (value.trim() && !isPending) {
      submit();
    }
  };

  return (
    <div className="flex flex-col h-[600px] max-w-2xl mx-auto bg-white rounded-2xl shadow-xl overflow-hidden border border-purple-100">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-pink-600 px-6 py-4">
        <div className="flex items-center gap-2 text-white">
          <Sparkles className="w-5 h-5" />
          <h2 className="font-semibold">Spirit Animal Guide</h2>
        </div>
        <p className="text-purple-100 text-sm mt-1">Discover your inner creature through conversation</p>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gradient-to-b from-purple-50/50 to-white">
        {thread.messages.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            <Sparkles className="w-12 h-12 mx-auto mb-3 text-purple-300" />
            <p className="text-lg font-medium text-purple-600">Welcome, seeker!</p>
            <p className="text-sm mt-1">Type a message to begin your journey...</p>
          </div>
        )}

        {thread.messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                message.role === "user"
                  ? "bg-gradient-to-r from-purple-600 to-pink-600 text-white"
                  : "bg-white border border-purple-100 text-gray-800 shadow-sm"
              }`}
            >
              {/* Render text content */}
              {Array.isArray(message.content) ? (
                message.content.map((part, i) =>
                  part.type === "text" ? (
                    <p key={i} className="whitespace-pre-wrap">{part.text}</p>
                  ) : null
                )
              ) : (
                <p className="whitespace-pre-wrap">{String(message.content)}</p>
              )}
              
              {/* Render AI-generated component if present */}
              {message.renderedComponent && (
                <div className="mt-4">
                  {message.renderedComponent}
                </div>
              )}
            </div>
          </div>
        ))}

        {/* Loading indicator */}
        {isPending && (
          <div className="flex justify-start">
            <div className="bg-white border border-purple-100 rounded-2xl px-4 py-3 shadow-sm">
              <div className="flex items-center gap-2 text-purple-600">
                <div className="flex gap-1">
                  <span className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                  <span className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                  <span className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                </div>
                <span className="text-sm">Consulting the spirits...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <form onSubmit={handleSubmit} className="p-4 border-t border-purple-100 bg-white">
        <div className="flex gap-2">
          <input
            ref={inputRef}
            type="text"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            placeholder="Share your thoughts..."
            disabled={isPending}
            className="flex-1 px-4 py-3 rounded-xl border border-purple-200 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
          />
          <button
            type="submit"
            disabled={isPending || !value.trim()}
            className="px-4 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </form>
    </div>
  );
}
