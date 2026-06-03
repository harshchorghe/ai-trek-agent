"use client";

import { useEffect, useRef, useState } from "react";

import type { AgentResponse, ChatMessage } from "@/lib/agent";
import { CAPABILITIES, QUICK_PROMPTS, type Trek } from "@/lib/treks";

type ConversationItem = ChatMessage & {
  id: string;
  meta?: AgentResponse;
};

type TrekDashboardProps = {
  treks: Trek[];
};

const initialAssistantMessage: ConversationItem = {
  id: "welcome",
  role: "assistant",
  content:
    "Welcome to TrekForge. I can route trek questions, build plans, and present clear client-ready summaries for Maharashtra adventures.",
};

export function TrekDashboard({ treks }: TrekDashboardProps) {
  const [input, setInput] = useState("Plan a trek to Kalsubai this weekend");
  const [isSending, setIsSending] = useState(false);
  const [conversation, setConversation] = useState<ConversationItem[]>([initialAssistantMessage]);
  const endRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [conversation]);

  async function submitPrompt(prompt: string) {
    const trimmed = prompt.trim();

    if (!trimmed || isSending) {
      return;
    }

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
        headers: {
          "Content-Type": "application/json",
        },
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
          id: `${Date.now()}-assistant-error`,
          role: "assistant",
          content: "The local agent endpoint is unavailable. Please try again after starting the Next.js app.",
        },
      ]);
    } finally {
      setIsSending(false);
    }
  }

  return (
    <div className="relative min-h-screen overflow-hidden text-slate-50">
      <div className="absolute inset-0 grid-fade opacity-35" />
      <div className="absolute left-[-6rem] top-[-7rem] h-72 w-72 rounded-full bg-emerald-400/20 blur-3xl" />
      <div className="absolute right-[-5rem] top-24 h-80 w-80 rounded-full bg-amber-400/15 blur-3xl" />
      <div className="absolute bottom-[-6rem] left-1/3 h-72 w-72 rounded-full bg-cyan-500/10 blur-3xl" />

      <div className="relative mx-auto flex min-h-screen max-w-7xl flex-col px-4 pb-8 pt-6 sm:px-6 lg:px-8">
        <header className="glass-panel flex flex-col gap-4 rounded-[28px] px-5 py-4 shadow-2xl sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.35em] text-emerald-300/80">AI Trek Agent</p>
            <h1 className="mt-1 font-display text-3xl tracking-tight text-white sm:text-4xl">
              TrekForge Command Center
            </h1>
          </div>
          <div className="flex flex-wrap gap-2 text-xs text-slate-200">
            <span className="rounded-full border border-emerald-300/20 bg-emerald-400/10 px-3 py-1.5">Live chat</span>
            <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1.5">Client presentation ready</span>
            <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1.5">Ollama fallback enabled</span>
          </div>
        </header>

        <main className="mt-6 grid flex-1 gap-6 lg:grid-cols-[1.15fr_0.85fr]">
          <section className="space-y-6">
            <div className="glass-panel rounded-[32px] p-6 shadow-2xl">
              <div className="flex flex-col gap-6 xl:flex-row xl:items-end xl:justify-between">
                <div className="max-w-2xl space-y-4">
                  <span className="inline-flex rounded-full border border-amber-300/25 bg-amber-400/10 px-3 py-1 text-xs font-medium uppercase tracking-[0.3em] text-amber-100">
                    Professional trekking assistant
                  </span>
                  <h2 className="font-display text-4xl leading-tight text-white sm:text-5xl">
                    A client-facing Next.js experience for trek planning, packing, and route intelligence.
                  </h2>
                  <p className="max-w-2xl text-sm leading-7 text-slate-300 sm:text-base">
                    Designed for a polished handoff, this interface combines the agent chat, trek summaries, quick actions,
                    and delivery-ready visual hierarchy in one place.
                  </p>
                </div>

                <div className="grid gap-3 sm:grid-cols-3 xl:w-[22rem] xl:grid-cols-1">
                  {[
                    { label: "Featured treks", value: `${treks.length}` },
                    { label: "Core tools", value: `${CAPABILITIES.length}` },
                    { label: "Response mode", value: "Local + Ollama" },
                  ].map((item) => (
                    <div key={item.label} className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
                      <p className="text-xs uppercase tracking-[0.24em] text-slate-400">{item.label}</p>
                      <p className="mt-2 text-lg font-semibold text-white">{item.value}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              {treks.map((trek) => (
                <article key={trek.slug} className="glass-panel rounded-[28px] p-5 transition-transform duration-200 hover:-translate-y-1">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <p className="text-xs uppercase tracking-[0.3em] text-emerald-300/80">Featured trek</p>
                      <h3 className="mt-2 font-display text-2xl text-white">{trek.name}</h3>
                    </div>
                    <span className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-slate-300">
                      {trek.difficulty}
                    </span>
                  </div>
                  <p className="mt-4 text-sm leading-6 text-slate-300">{trek.summary}</p>
                  <div className="mt-4 grid grid-cols-3 gap-2 text-xs text-slate-200">
                    <div className="rounded-2xl bg-white/5 px-3 py-2">
                      <p className="text-slate-400">Duration</p>
                      <p className="mt-1 font-medium text-white">{trek.duration}</p>
                    </div>
                    <div className="rounded-2xl bg-white/5 px-3 py-2">
                      <p className="text-slate-400">Height</p>
                      <p className="mt-1 font-medium text-white">{trek.height}</p>
                    </div>
                    <div className="rounded-2xl bg-white/5 px-3 py-2">
                      <p className="text-slate-400">Use case</p>
                      <p className="mt-1 font-medium text-white">{trek.bestFor.split(",")[0]}</p>
                    </div>
                  </div>
                </article>
              ))}
            </div>

            <section className="glass-panel rounded-[32px] p-5 shadow-2xl">
              <div className="flex items-center justify-between gap-4">
                <div>
                  <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Conversation studio</p>
                  <h3 className="mt-2 font-display text-3xl text-white">Agent chat and response console</h3>
                </div>
                <div className="hidden rounded-full border border-white/10 bg-white/5 px-4 py-2 text-xs text-slate-300 sm:block">
                  Structured replies with tool routing
                </div>
              </div>

              <div className="mt-5 rounded-[28px] border border-white/10 bg-slate-950/35 p-4">
                <div className="max-h-[34rem] space-y-4 overflow-y-auto pr-1">
                  {conversation.map((item) => (
                    <div
                      key={item.id}
                      className={`flex ${item.role === "user" ? "justify-end" : "justify-start"}`}
                    >
                      <div
                        className={`max-w-[92%] rounded-[24px] px-4 py-4 shadow-lg sm:max-w-[82%] ${
                          item.role === "user"
                            ? "bg-gradient-to-br from-emerald-400 to-teal-500 text-slate-950"
                            : "border border-white/10 bg-white/6 text-slate-100"
                        }`}
                      >
                        {item.role === "assistant" && item.meta ? (
                          <div className="mb-3 flex flex-wrap gap-2 text-[11px] uppercase tracking-[0.22em] text-slate-400">
                            <span className="rounded-full border border-white/10 bg-white/5 px-2.5 py-1">Tool: {item.meta.tool}</span>
                            {item.meta.trekName ? (
                              <span className="rounded-full border border-white/10 bg-white/5 px-2.5 py-1">Trek: {item.meta.trekName}</span>
                            ) : null}
                            <span className="rounded-full border border-white/10 bg-white/5 px-2.5 py-1">Source: {item.meta.source}</span>
                          </div>
                        ) : null}

                        <p className="whitespace-pre-wrap text-sm leading-7 sm:text-[15px]">{item.content}</p>

                        {item.meta?.facts.length ? (
                          <div className="mt-4 grid gap-3 sm:grid-cols-3">
                            {item.meta.facts.map((fact) => (
                              <div key={fact.label} className="rounded-2xl border border-white/10 bg-slate-950/30 px-3 py-2">
                                <p className="text-[10px] uppercase tracking-[0.22em] text-slate-400">{fact.label}</p>
                                <p className="mt-1 text-sm font-medium text-white">{fact.value}</p>
                              </div>
                            ))}
                          </div>
                        ) : null}

                        {item.meta?.suggestions.length ? (
                          <div className="mt-4 flex flex-wrap gap-2">
                            {item.meta.suggestions.map((suggestion) => (
                              <button
                                key={suggestion}
                                type="button"
                                onClick={() => setInput(suggestion)}
                                className="rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-xs text-slate-200 transition hover:border-amber-300/40 hover:bg-amber-400/10"
                              >
                                {suggestion}
                              </button>
                            ))}
                          </div>
                        ) : null}
                      </div>
                    </div>
                  ))}
                  <div ref={endRef} />
                </div>

                <form
                  className="mt-4 grid gap-3 sm:grid-cols-[1fr_auto]"
                  onSubmit={(event) => {
                    event.preventDefault();
                    void submitPrompt(input);
                  }}
                >
                  <label className="sr-only" htmlFor="agent-prompt">
                    Ask the agent
                  </label>
                  <input
                    id="agent-prompt"
                    value={input}
                    onChange={(event) => setInput(event.target.value)}
                    placeholder="Ask about planning, packing, difficulty, or weather..."
                    className="h-12 rounded-2xl border border-white/10 bg-slate-950/50 px-4 text-sm text-white outline-none transition placeholder:text-slate-500 focus:border-emerald-300/40"
                  />
                  <button
                    type="submit"
                    disabled={isSending}
                    className="h-12 rounded-2xl bg-gradient-to-r from-amber-300 via-orange-400 to-emerald-400 px-5 text-sm font-semibold text-slate-950 transition hover:brightness-105 disabled:cursor-not-allowed disabled:opacity-70"
                  >
                    {isSending ? "Sending..." : "Send to agent"}
                  </button>
                </form>
              </div>

              <div className="mt-4 flex flex-wrap gap-2">
                {QUICK_PROMPTS.map((prompt) => (
                  <button
                    key={prompt}
                    type="button"
                    onClick={() => setInput(prompt)}
                    className="rounded-full border border-white/10 bg-white/5 px-3 py-2 text-xs text-slate-300 transition hover:border-emerald-300/40 hover:bg-emerald-400/10 hover:text-white"
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </section>
          </section>

          <aside className="space-y-6">
            <section className="glass-panel rounded-[32px] p-5 shadow-2xl">
              <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Capability stack</p>
              <div className="mt-4 space-y-3">
                {CAPABILITIES.map((capability) => (
                  <div key={capability} className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-200">
                    {capability}
                  </div>
                ))}
              </div>
            </section>

            <section className="glass-panel rounded-[32px] p-5 shadow-2xl">
              <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Delivery notes</p>
              <div className="mt-4 space-y-4 text-sm leading-6 text-slate-300">
                <p>
                  The interface is styled like a client handoff, with a glass-panel layout, refined typography, and a clear
                  information hierarchy.
                </p>
                <p>
                  The chat endpoint mirrors the Python router logic and automatically falls back if Ollama is unavailable,
                  so the frontend remains usable during demos.
                </p>
              </div>
            </section>

            <section className="glass-panel rounded-[32px] p-5 shadow-2xl">
              <p className="text-xs uppercase tracking-[0.3em] text-slate-400">Client summary</p>
              <div className="mt-4 rounded-[24px] border border-white/10 bg-slate-950/35 p-4">
                <h4 className="font-display text-2xl text-white">What this delivers</h4>
                <ul className="mt-4 space-y-3 text-sm text-slate-300">
                  <li>• A professional landing surface for the trekking assistant</li>
                  <li>• Live chat routed through a clean Next.js API layer</li>
                  <li>• Trek cards, quick prompts, and structured response metadata</li>
                  <li>• A polished visual style suitable for client demos</li>
                </ul>
              </div>
            </section>
          </aside>
        </main>
      </div>
    </div>
  );
}