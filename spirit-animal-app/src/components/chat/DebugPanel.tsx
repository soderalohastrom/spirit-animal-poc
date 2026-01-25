import { useTamboThread } from "@tambo-ai/react";
import { Bug, ChevronDown, ChevronRight, X } from "lucide-react";
import { useEffect, useState } from "react";

interface DebugPanelProps {
  defaultOpen?: boolean;
}

export function DebugPanel({ defaultOpen = false }: DebugPanelProps) {
  const { thread, generationStage } = useTamboThread();
  const [isOpen, setIsOpen] = useState(defaultOpen);
  const [expandedMessages, setExpandedMessages] = useState<Set<string>>(new Set());

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey && e.shiftKey && e.key === "D") {
        e.preventDefault();
        setIsOpen((prev) => !prev);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  const toggleMessage = (id: string) => {
    setExpandedMessages((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  if (!isOpen) {
    return (
      <button
        type="button"
        onClick={() => setIsOpen(true)}
        className="fixed bottom-4 right-4 z-50 p-3 bg-gray-800 text-white rounded-full shadow-lg hover:bg-gray-700 transition-colors"
        title="Open Debug Panel (Ctrl+Shift+D)"
      >
        <Bug className="w-5 h-5" />
      </button>
    );
  }

  return (
    <div className="fixed bottom-4 right-4 z-50 w-[500px] max-h-[70vh] bg-gray-900 text-gray-100 rounded-lg shadow-2xl overflow-hidden font-mono text-xs">
      <div className="flex items-center justify-between px-3 py-2 bg-gray-800 border-b border-gray-700">
        <div className="flex items-center gap-2">
          <Bug className="w-4 h-4 text-green-400" />
          <span className="font-semibold text-sm">Tambo Debug</span>
          <span className="px-2 py-0.5 bg-gray-700 rounded text-[10px]">
            {generationStage}
          </span>
        </div>
        <button
          type="button"
          onClick={() => setIsOpen(false)}
          className="p-1 hover:bg-gray-700 rounded"
          title="Close (Ctrl+Shift+D)"
        >
          <X className="w-4 h-4" />
        </button>
      </div>

      <div className="overflow-y-auto max-h-[calc(70vh-40px)] p-2 space-y-2">
        <div className="p-2 bg-gray-800 rounded">
          <div className="text-gray-400 text-[10px] uppercase tracking-wide mb-1">Thread</div>
          <div className="text-green-400">ID: {thread.id?.slice(0, 12)}...</div>
          <div className="text-gray-400">Messages: {thread.messages.length}</div>
        </div>

        {thread.messages.map((msg, idx) => {
          const isExpanded = expandedMessages.has(msg.id);
          const hasToolCall = !!(msg as any).toolCallRequest;
          const hasReasoning = !!(msg as any).reasoning?.length;
          const hasComponent = !!(msg as any).component;
          const hasError = !!(msg as any).error;

          const textContent = Array.isArray(msg.content)
            ? msg.content
                .filter((p: any) => p.type === "text")
                .map((p: any) => p.text)
                .join(" ")
            : String(msg.content);
          const preview = textContent.slice(0, 80) + (textContent.length > 80 ? "..." : "");

          return (
            <div
              key={msg.id}
              className={`rounded border ${
                msg.role === "user"
                  ? "border-blue-700 bg-blue-900/30"
                  : msg.role === "assistant"
                  ? "border-purple-700 bg-purple-900/30"
                  : msg.role === "tool"
                  ? "border-orange-700 bg-orange-900/30"
                  : "border-gray-700 bg-gray-800/30"
              }`}
            >
              <button
                type="button"
                onClick={() => toggleMessage(msg.id)}
                className="w-full flex items-center gap-2 px-2 py-1.5 text-left hover:bg-white/5"
              >
                {isExpanded ? (
                  <ChevronDown className="w-3 h-3 text-gray-500" />
                ) : (
                  <ChevronRight className="w-3 h-3 text-gray-500" />
                )}
                <span className="text-gray-500 text-[10px]">#{idx + 1}</span>
                <span
                  className={`px-1.5 py-0.5 rounded text-[10px] font-medium ${
                    msg.role === "user"
                      ? "bg-blue-600 text-blue-100"
                      : msg.role === "assistant"
                      ? "bg-purple-600 text-purple-100"
                      : msg.role === "tool"
                      ? "bg-orange-600 text-orange-100"
                      : "bg-gray-600 text-gray-100"
                  }`}
                >
                  {msg.role}
                </span>
                {hasToolCall && (
                  <span className="px-1.5 py-0.5 bg-yellow-600 text-yellow-100 rounded text-[10px]">
                    TOOL_CALL
                  </span>
                )}
                {hasReasoning && (
                  <span className="px-1.5 py-0.5 bg-cyan-600 text-cyan-100 rounded text-[10px]">
                    REASONING
                  </span>
                )}
                {hasComponent && (
                  <span className="px-1.5 py-0.5 bg-green-600 text-green-100 rounded text-[10px]">
                    COMPONENT
                  </span>
                )}
                {hasError && (
                  <span className="px-1.5 py-0.5 bg-red-600 text-red-100 rounded text-[10px]">
                    ERROR
                  </span>
                )}
              </button>

              {!isExpanded && (
                <div className="px-2 pb-1.5 text-gray-400 truncate">{preview}</div>
              )}

              {isExpanded && (
                <div className="px-2 pb-2 space-y-2 border-t border-gray-700/50 mt-1 pt-2">
                  <div>
                    <div className="text-gray-500 text-[10px] uppercase tracking-wide mb-1">
                      Content
                    </div>
                    <pre className="text-gray-200 whitespace-pre-wrap break-words text-[11px] bg-black/20 p-2 rounded max-h-32 overflow-y-auto">
                      {textContent || "(empty)"}
                    </pre>
                  </div>

                  {hasToolCall && (
                    <div>
                      <div className="text-yellow-400 text-[10px] uppercase tracking-wide mb-1">
                        Tool Call Request
                      </div>
                      <pre className="text-yellow-200 whitespace-pre-wrap break-words text-[11px] bg-black/20 p-2 rounded max-h-40 overflow-y-auto">
                        {JSON.stringify((msg as any).toolCallRequest, null, 2)}
                      </pre>
                    </div>
                  )}

                  {hasReasoning && (
                    <div>
                      <div className="text-cyan-400 text-[10px] uppercase tracking-wide mb-1">
                        Reasoning Steps
                      </div>
                      <div className="space-y-1">
                        {(msg as any).reasoning.map((step: string, i: number) => (
                          <div
                            key={`reasoning-${msg.id}-${i}`}
                            className="text-cyan-200 text-[11px] bg-black/20 p-2 rounded"
                          >
                            <span className="text-cyan-500">Step {i + 1}:</span> {step}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {hasComponent && (
                    <div>
                      <div className="text-green-400 text-[10px] uppercase tracking-wide mb-1">
                        Component Decision
                      </div>
                      <pre className="text-green-200 whitespace-pre-wrap break-words text-[11px] bg-black/20 p-2 rounded max-h-40 overflow-y-auto">
                        {JSON.stringify((msg as any).component, null, 2)}
                      </pre>
                    </div>
                  )}

                  {hasError && (
                    <div>
                      <div className="text-red-400 text-[10px] uppercase tracking-wide mb-1">
                        Error
                      </div>
                      <pre className="text-red-200 whitespace-pre-wrap break-words text-[11px] bg-black/20 p-2 rounded">
                        {(msg as any).error}
                      </pre>
                    </div>
                  )}

                  <details className="text-gray-500">
                    <summary className="cursor-pointer text-[10px] uppercase tracking-wide hover:text-gray-300">
                      Raw JSON
                    </summary>
                    <pre className="mt-1 text-gray-400 whitespace-pre-wrap break-words text-[10px] bg-black/30 p-2 rounded max-h-60 overflow-y-auto">
                      {JSON.stringify(msg, null, 2)}
                    </pre>
                  </details>
                </div>
              )}
            </div>
          );
        })}

        {thread.messages.length === 0 && (
          <div className="text-center py-8 text-gray-500">No messages yet</div>
        )}
      </div>
    </div>
  );
}
