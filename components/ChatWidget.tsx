"use client";

import { useState, useRef, useEffect } from "react";
import { KawaiiIcon } from "./AniMascot";

type Msg = { role: "user" | "assistant"; content: string };

const SUGGESTIONS = [
  "Best kebap restaurants?",
  "Romantic dinner with Bosphorus view?",
  "Budget breakfast spots?",
  "Late night options?",
  "Business lunch Beşiktaş?",
  "Vegetarian friendly?",
];

export function ChatWidget() {
  const [open, setOpen] = useState(false);
  const [msgs, setMsgs] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [streaming, setStreaming] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Listen for mascot click event
  useEffect(() => {
    const handler = () => setOpen(true);
    window.addEventListener("openChat", handler);
    return () => window.removeEventListener("openChat", handler);
  }, []);

  useEffect(() => {
    if (open && msgs.length === 0) {
      setMsgs([{
        role: "assistant",
        content: "Merhaba! 🍽 I know 453 Istanbul restaurants inside out. Ask me anything — cuisine, neighborhood, mood, budget!",
      }]);
    }
    if (open) setTimeout(() => inputRef.current?.focus(), 100);
  }, [open]); // eslint-disable-line

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [msgs, streaming]);

  async function send(text: string) {
    if (!text.trim() || loading) return;
    const userMsg: Msg = { role: "user", content: text };
    setMsgs(prev => [...prev, userMsg]);
    setInput("");
    setLoading(true);
    setStreaming("");

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: text,
          history: msgs.slice(-8),
        }),
      });

      if (!res.ok || !res.body) throw new Error("API error");

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let full = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        full += decoder.decode(value, { stream: true });
        setStreaming(full);
      }

      setMsgs(prev => [...prev, { role: "assistant", content: full }]);
    } catch {
      setMsgs(prev => [...prev, {
        role: "assistant",
        content: "Something went wrong. Please try again!",
      }]);
    } finally {
      setLoading(false);
      setStreaming("");
    }
  }

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end gap-3">
      {/* Chat panel */}
      {open && (
        <div className="bg-white border border-gray-200 rounded-2xl shadow-2xl flex flex-col overflow-hidden"
          style={{ width: 340, maxHeight: 540 }}>

          {/* Header */}
          <div className="bg-gray-900 px-4 py-3 flex items-center gap-3 shrink-0">
            <KawaiiIcon variant="finedining" className="w-9 h-9 shrink-0" />
            <div className="flex-1 min-w-0">
              <div className="text-white font-semibold text-sm leading-tight">Istanbul Restaurant AI</div>
              <div className="text-gray-400 text-xs">453 restaurants · ask anything</div>
            </div>
            <button
              onClick={() => setOpen(false)}
              className="text-gray-400 hover:text-white text-xl leading-none ml-1 shrink-0"
              aria-label="Close"
            >×</button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-3 space-y-3" style={{ minHeight: 160 }}>
            {msgs.map((m, i) => (
              <div key={i} className={`flex gap-2 ${m.role === "user" ? "justify-end" : "items-start"}`}>
                {m.role === "assistant" && (
                  <KawaiiIcon variant="breakfast" className="w-7 h-7 shrink-0 mt-0.5" />
                )}
                <div className={`text-sm rounded-2xl px-3 py-2 leading-relaxed whitespace-pre-wrap ${
                  m.role === "user"
                    ? "bg-gray-900 text-white rounded-tr-sm max-w-[230px]"
                    : "bg-gray-100 text-gray-800 rounded-tl-sm max-w-[250px]"
                }`}>
                  {m.content}
                </div>
              </div>
            ))}

            {/* Streaming */}
            {streaming && (
              <div className="flex gap-2 items-start">
                <KawaiiIcon variant="breakfast" className="w-7 h-7 shrink-0 mt-0.5" />
                <div className="bg-gray-100 text-gray-800 rounded-2xl rounded-tl-sm px-3 py-2 text-sm leading-relaxed max-w-[250px] whitespace-pre-wrap">
                  {streaming}
                  <span className="inline-block w-0.5 h-3.5 bg-gray-500 ml-0.5 align-middle animate-pulse" />
                </div>
              </div>
            )}

            {/* Typing dots */}
            {loading && !streaming && (
              <div className="flex gap-2 items-start">
                <KawaiiIcon variant="breakfast" className="w-7 h-7 shrink-0 mt-0.5" />
                <div className="bg-gray-100 rounded-2xl rounded-tl-sm px-3 py-3">
                  <span className="flex gap-1 items-center">
                    {[0, 150, 300].map(d => (
                      <span key={d} className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce"
                        style={{ animationDelay: `${d}ms` }} />
                    ))}
                  </span>
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* Suggestion chips */}
          {msgs.length <= 1 && !loading && (
            <div className="px-3 pb-2 flex flex-wrap gap-1.5 shrink-0">
              {SUGGESTIONS.map(s => (
                <button
                  key={s}
                  onClick={() => send(s)}
                  className="text-xs bg-blue-50 hover:bg-blue-100 text-blue-700 px-2.5 py-1 rounded-full transition-colors border border-blue-100"
                >
                  {s}
                </button>
              ))}
            </div>
          )}

          {/* Input */}
          <div className="p-3 border-t border-gray-100 shrink-0">
            <form onSubmit={e => { e.preventDefault(); send(input); }} className="flex gap-2">
              <input
                ref={inputRef}
                value={input}
                onChange={e => setInput(e.target.value)}
                placeholder="Where to eat tonight?"
                disabled={loading}
                className="flex-1 text-sm border border-gray-200 rounded-xl px-3 py-2 outline-none focus:border-blue-300 transition-colors disabled:opacity-50"
              />
              <button
                type="submit"
                disabled={loading || !input.trim()}
                className="bg-gray-900 hover:bg-gray-700 disabled:opacity-40 text-white px-3 py-2 rounded-xl text-sm font-bold transition-colors shrink-0"
              >→</button>
            </form>
          </div>
        </div>
      )}

      {/* Floating toggle button */}
      <button
        onClick={() => setOpen(o => !o)}
        className={`rounded-full w-14 h-14 flex items-center justify-center shadow-xl transition-all hover:scale-105 ${
          open ? "bg-gray-700 hover:bg-gray-600" : "bg-gray-900 hover:bg-gray-700"
        }`}
        aria-label="Open restaurant AI assistant"
      >
        {open
          ? <span className="text-white text-xl font-light">×</span>
          : <KawaiiIcon variant="fish" className="w-9 h-9" />
        }
      </button>
    </div>
  );
}
