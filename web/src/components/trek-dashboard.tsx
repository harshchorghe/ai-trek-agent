"use client";

import { useEffect, useRef, useState } from "react";
import type { AgentResponse, ChatMessage } from "@/lib/agent";
import { QUICK_PROMPTS } from "@/lib/treks";

type ConversationItem = ChatMessage & {
  id: string;
  meta?: AgentResponse;
};

const initialMessage: ConversationItem = {
  id: "welcome",
  role: "assistant",
  content:
    "Welcome to Explorush AI Travel Assistant! 🎒\n\nI am your experienced travel consultant. Ask me anything about trip planning, budget estimates, packing guides, hotels, dining, or trekking adventures.",
};

export function ChatConsole() {
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [conversation, setConversation] = useState<ConversationItem[]>([initialMessage]);
  const endRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [conversation]);

  async function submitPrompt(prompt: string) {
    const trimmed = prompt.trim();
    if (!trimmed || isSending) return;

    const userMessage: ConversationItem = {
      id: `${Date.now()}-user`,
      role: "user",
      content: trimmed,
    };

    const nextConversation = [...conversation, userMessage];
    setConversation(nextConversation);
    setInput("");
    setIsSending(true);

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: nextConversation.map(({ role, content }) => ({ role, content })),
        }),
      });

      const data = (await response.json()) as AgentResponse;

      setConversation((current) => [
        ...current,
        {
          id: `${Date.now()}-assistant`,
          role: "assistant",
          content: data.reply,
          meta: data,
        },
      ]);
    } catch {
      setConversation((current) => [
        ...current,
        {
          id: `${Date.now()}-error`,
          role: "assistant",
          content: "Travel assistant endpoint unavailable. Please start the Next.js app and try again.",
        },
      ]);
    } finally {
      setIsSending(false);
    }
  }

  return (
    <div className="flex flex-col h-[600px] bg-slate-900 border border-slate-700 rounded-2xl overflow-hidden shadow-2xl">

      {/* Header */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-slate-800 bg-slate-950/60 backdrop-blur-md">
        <div className="flex items-center gap-3">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
          <div>
            <span className="text-sm font-semibold text-slate-100 block">
              Explorush AI Travel Assistant
            </span>
            <span className="text-[10px] text-slate-400">
              Active Session Context Enabled
            </span>
          </div>
        </div>
        <span className="text-xs text-slate-400 bg-slate-800 px-2.5 py-1 rounded-full border border-slate-700">
          Agent Version 2.0
        </span>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-5 py-5 flex flex-col gap-4 bg-slate-900/40">
        {conversation.map((item) => (
          <div
            key={item.id}
            className={`flex flex-col max-w-[85%] ${
              item.role === "user" ? "self-end items-end" : "self-start items-start"
            }`}
          >
            <span className="text-[10px] text-slate-400 mb-1 flex items-center gap-1">
              {item.role === "user" ? (
                "You"
              ) : (
                <>
                  Explorush Consultant
                  {item.meta?.tool && (
                    <span className="inline-flex items-center gap-1 text-[10px] bg-emerald-950/40 text-emerald-300 border border-emerald-800 rounded-full px-2 py-0.5 font-mono">
                      {item.meta.tool}
                    </span>
                  )}
                </>
              )}
            </span>

            <div
              className={`px-4 py-3 rounded-2xl text-sm leading-relaxed ${
                item.role === "user"
                  ? "bg-emerald-600 text-slate-50 shadow-md rounded-tr-none border border-emerald-500"
                  : "bg-slate-800 text-slate-100 shadow-md rounded-tl-none border border-slate-700"
              }`}
            >
              <p className="whitespace-pre-wrap">{item.content}</p>
            </div>

            {/* Fact chips */}
            {item.meta?.facts && item.meta.facts.length > 0 && (
              <div className="flex gap-1.5 flex-wrap mt-2">
                {item.meta.facts.map((fact) => (
                  <div
                    key={fact.label}
                    className="bg-slate-950/60 border border-slate-800 rounded-lg px-2.5 py-1 text-[11px] text-slate-400"
                  >
                    {fact.label}:{" "}
                    <span className="font-semibold text-slate-200">
                      {fact.value}
                    </span>
                  </div>
                ))}
              </div>
            )}

            {/* Suggestion pills */}
            {item.meta?.suggestions && item.meta.suggestions.length > 0 && (
              <div className="flex gap-1.5 flex-wrap mt-2">
                {item.meta.suggestions.map((s) => (
                  <button
                    key={s}
                    type="button"
                    onClick={() => setInput(s)}
                    className="text-[11px] px-3 py-1 rounded-full border border-slate-700 bg-slate-800 text-slate-300 hover:border-emerald-500 hover:text-emerald-300 hover:bg-emerald-950/20 transition-all duration-200"
                  >
                    {s}
                  </button>
                ))}
              </div>
            )}
          </div>
        ))}

        {/* Typing indicator */}
        {isSending && (
          <div className="self-start flex flex-col max-w-[80%]">
            <span className="text-[10px] text-slate-400 mb-1">Explorush Consultant</span>
            <div className="bg-slate-800 border border-slate-700 rounded-2xl rounded-tl-none px-4 py-3 flex gap-1.5 items-center">
              {[0, 150, 300].map((delay) => (
                <span
                  key={delay}
                  className="w-2 h-2 rounded-full bg-slate-400 animate-bounce"
                  style={{ animationDelay: `${delay}ms` }}
                />
              ))}
            </div>
          </div>
        )}

        <div ref={endRef} />
      </div>

      {/* Quick prompts */}
      <div className="px-5 py-2.5 border-t border-slate-800/80 bg-slate-950/20 flex gap-2 flex-wrap items-center">
        <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider mr-1">Quick:</span>
        {QUICK_PROMPTS.map((prompt) => (
          <button
            key={prompt}
            type="button"
            onClick={() => setInput(prompt)}
            className="text-[11px] px-3 py-1 rounded-full border border-slate-700 bg-slate-800/60 text-slate-300 hover:border-emerald-500 hover:text-emerald-300 hover:bg-emerald-950/25 transition-all duration-200"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Input row */}
      <div className="px-5 py-4 border-t border-slate-800 bg-slate-950/40 flex gap-3">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter") void submitPrompt(input); }}
          placeholder="Ask about planning, packing, budget estimation, safety..."
          className="flex-1 h-10 rounded-xl border border-slate-700 bg-slate-850 px-4 text-sm text-slate-100 placeholder:text-slate-500 outline-none focus:border-emerald-500 transition-colors"
        />
        <button
          type="button"
          onClick={() => void submitPrompt(input)}
          disabled={isSending}
          className="h-10 px-5 rounded-xl bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-semibold transition-all duration-200 flex items-center gap-1.5 shadow-lg shadow-emerald-900/20"
        >
          {isSending ? "Sending…" : "Send"}
        </button>
      </div>
    </div>
  );
}