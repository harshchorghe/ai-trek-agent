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
    "Welcome to TrekForge. Ask me anything about Maharashtra treks — route planning, packing lists, difficulty, or weather windows.",
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
          content: "Agent endpoint unavailable. Please start the Next.js app and try again.",
        },
      ]);
    } finally {
      setIsSending(false);
    }
  }

  return (
    <div className="flex flex-col h-[560px] bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl overflow-hidden">

      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-slate-200 dark:border-slate-700">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-500" />
          <span className="text-sm font-medium text-slate-900 dark:text-slate-100">
            TrekForge agent
          </span>
        </div>
        <span className="text-xs text-slate-400">
          Maharashtra trek assistant · Ollama fallback enabled
        </span>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4 flex flex-col gap-3">
        {conversation.map((item) => (
          <div
            key={item.id}
            className={`flex flex-col max-w-[80%] ${
              item.role === "user" ? "self-end items-end" : "self-start items-start"
            }`}
          >
            <span className="text-[11px] text-slate-400 mb-1 flex items-center gap-1">
              {item.role === "user" ? (
                "You"
              ) : (
                <>
                  Agent
                  {item.meta?.tool && (
                    <span className="inline-flex items-center gap-1 text-[11px] bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-700 rounded-full px-2 py-0.5">
                      {item.meta.tool}
                    </span>
                  )}
                </>
              )}
            </span>

            <div
              className={`px-3 py-2 rounded-xl text-sm leading-relaxed ${
                item.role === "user"
                  ? "bg-emerald-50 dark:bg-emerald-900/30 text-emerald-900 dark:text-emerald-100 border border-emerald-200 dark:border-emerald-700"
                  : "bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 border border-slate-200 dark:border-slate-700"
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
                    className="bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700 rounded-md px-2.5 py-1 text-[11.5px] text-slate-500 dark:text-slate-400"
                  >
                    {fact.label}:{" "}
                    <span className="font-medium text-slate-800 dark:text-slate-200">
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
                    className="text-xs px-2.5 py-1 rounded-full border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-500 dark:text-slate-400 hover:border-emerald-400 hover:text-emerald-700 dark:hover:text-emerald-300 hover:bg-emerald-50 dark:hover:bg-emerald-900/20 transition-colors"
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
            <span className="text-[11px] text-slate-400 mb-1">Agent</span>
            <div className="bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-3 py-3 flex gap-1 items-center">
              {[0, 150, 300].map((delay) => (
                <span
                  key={delay}
                  className="w-1.5 h-1.5 rounded-full bg-slate-400 animate-bounce"
                  style={{ animationDelay: `${delay}ms` }}
                />
              ))}
            </div>
          </div>
        )}

        <div ref={endRef} />
      </div>

      {/* Quick prompts */}
      <div className="px-4 py-2 border-t border-slate-200 dark:border-slate-700 flex gap-1.5 flex-wrap items-center">
        <span className="text-[11px] text-slate-400 mr-1">Quick:</span>
        {QUICK_PROMPTS.map((prompt) => (
          <button
            key={prompt}
            type="button"
            onClick={() => setInput(prompt)}
            className="text-xs px-2.5 py-1 rounded-full border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-500 dark:text-slate-400 hover:border-emerald-400 hover:text-emerald-700 dark:hover:text-emerald-300 hover:bg-emerald-50 dark:hover:bg-emerald-900/20 transition-colors"
          >
            {prompt}
          </button>
        ))}
      </div>

      {/* Input row */}
      <div className="px-4 py-3 border-t border-slate-200 dark:border-slate-700 flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter") void submitPrompt(input); }}
          placeholder="Ask about routes, packing, weather, difficulty…"
          className="flex-1 h-9 rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-3 text-sm text-slate-900 dark:text-slate-100 placeholder:text-slate-400 outline-none focus:border-emerald-400 dark:focus:border-emerald-500 transition-colors"
        />
        <button
          type="button"
          onClick={() => void submitPrompt(input)}
          disabled={isSending}
          className="h-9 px-4 rounded-lg bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium transition-colors flex items-center gap-1.5"
        >
          {isSending ? "Sending…" : "Send"}
        </button>
      </div>
    </div>
  );
}