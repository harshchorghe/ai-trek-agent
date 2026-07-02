"use client";

import { useEffect, useRef, useState } from "react";
import type { AgentResponse, ChatMessage } from "@/lib/agent";
import { QUICK_PROMPTS } from "@/lib/treks";
import { Markdown } from "./markdown";

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

// Custom Helper to extract sections from plan content
function extractSection(content: string, headingKeywords: string[]): string | null {
  const lines = content.split("\n");
  let inside = false;
  const sectionLines: string[] = [];

  for (const line of lines) {
    const isHeading = 
      line.trim().startsWith("#") || 
      line.includes("======") || 
      line.includes("------") || 
      (line.toUpperCase() === line && line.trim().length > 3 && !line.includes("-") && !line.includes("|"));
    
    if (isHeading) {
      const match = headingKeywords.some(keyword => line.toLowerCase().includes(keyword.toLowerCase()));
      if (match) {
        inside = true;
        continue;
      } else if (inside) {
        // We hit another heading, stop extracting
        break;
      }
    }

    if (inside) {
      sectionLines.push(line);
    }
  }

  const result = sectionLines.join("\n").trim();
  // Strip horizontal rules or separators from start/end
  return result ? result.replace(/^[=\-\s]+|[=\-\s]+$/g, "") : null;
}

export function ChatConsole() {
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [conversation, setConversation] = useState<ConversationItem[]>([initialMessage]);
  const [activeTab, setActiveTab] = useState<"itinerary" | "budget" | "stays" | "packing" | "weather">("itinerary");
  
  // Selected assistant response for the showcase panel
  const [selectedPlanIndex, setSelectedPlanIndex] = useState<number>(-1);
  const endRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [conversation]);

  // Set the latest plan response index when a new assistant message arrives
  useEffect(() => {
    const lastIdx = conversation.length - 1;
    if (lastIdx >= 0 && conversation[lastIdx].role === "assistant") {
      const content = conversation[lastIdx].content;
      if (content.includes("EXPLORUSH TRAVEL PLAN") || content.includes("Itinerary") || content.includes("Budget") || content.includes("Packing")) {
        setSelectedPlanIndex(lastIdx);
      }
    }
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

  // Get content for the Showcase Panel
  const selectedMessage = selectedPlanIndex >= 0 ? conversation[selectedPlanIndex] : null;
  const rawContent = selectedMessage ? selectedMessage.content : "";

  // Extract sections
  const itineraryContent = extractSection(rawContent, ["itinerary", "daily itinerary"]);
  const budgetContent = extractSection(rawContent, ["budget", "estimated budget"]);
  const staysContent = extractSection(rawContent, ["accommodation", "hotel", "hotel recommendations", "dining", "restaurant", "foodie guide", "food & drinks"]);
  const packingContent = extractSection(rawContent, ["packing", "packing list"]);
  const weatherContent = extractSection(rawContent, ["weather", "forecast", "safety & emergency", "safety", "emergency", "general travel tips"]);

  // Show details panel only if there's any valid plan content extracted
  const hasShowcaseData = itineraryContent || budgetContent || staysContent || packingContent || weatherContent;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 w-full items-stretch">
      
      {/* Left Panel: Chat Console (5 Cols) */}
      <div className="lg:col-span-5 flex flex-col h-[620px] bg-slate-900/60 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl backdrop-blur-md">
        
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-slate-800 bg-slate-950/40">
          <div className="flex items-center gap-2.5">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
            <div>
              <span className="text-xs font-bold text-slate-100 uppercase tracking-wide block">
                Explorush Console
              </span>
              <span className="text-[10px] text-slate-400">
                Groq Cloud Engine Active
              </span>
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-4 py-4 flex flex-col gap-4">
          {conversation.map((item, idx) => (
            <div
              key={item.id}
              className={`flex flex-col max-w-[90%] ${
                item.role === "user" ? "self-end items-end" : "self-start items-start"
              }`}
            >
              <span className="text-[9px] text-slate-500 mb-1 flex items-center gap-1 uppercase tracking-wider font-semibold">
                {item.role === "user" ? (
                  "You"
                ) : (
                  <>
                    Agent
                    {item.meta?.tool && (
                      <span className="inline-flex items-center gap-1 text-[9px] bg-emerald-950/40 text-emerald-300 border border-emerald-900 rounded-full px-1.5 py-0.2 font-mono">
                        {item.meta.tool}
                      </span>
                    )}
                  </>
                )}
              </span>

              <button
                type="button"
                disabled={item.role !== "assistant" || idx === 0}
                onClick={() => setSelectedPlanIndex(idx)}
                className={`text-left transition-all duration-200 rounded-2xl px-3.5 py-2.5 text-xs leading-relaxed border ${
                  item.role === "user"
                    ? "bg-emerald-600 text-white rounded-tr-none border-emerald-500 shadow-md"
                    : `rounded-tl-none border-slate-800 shadow-md ${
                        selectedPlanIndex === idx
                          ? "bg-slate-800 border-emerald-500/50 shadow-emerald-950/20 shadow-md"
                          : "bg-slate-900/80 hover:bg-slate-850"
                      }`
                }`}
              >
                {item.role === "assistant" && (item.content.includes("EXPLORUSH TRAVEL PLAN") || item.content.includes("Day 1:")) ? (
                  <div>
                    <div className="font-bold text-slate-200 mb-1.5 flex items-center gap-1">
                      🗺️ Travel Plan Response
                      <span className="text-[9px] font-normal text-slate-400 bg-slate-800 border border-slate-700 px-1 py-0.2 rounded">
                        Details in Showcase ➜
                      </span>
                    </div>
                    {/* Render a truncated summary inside chat bubble */}
                    <p className="text-[11px] text-slate-400 line-clamp-2 italic">
                      {item.content.split("\n").slice(0, 4).join(" ")}...
                    </p>
                  </div>
                ) : (
                  <Markdown content={item.content} />
                )}
              </button>
            </div>
          ))}

          {/* Typing indicator */}
          {isSending && (
            <div className="self-start flex flex-col max-w-[80%]">
              <span className="text-[9px] text-slate-500 mb-1 uppercase tracking-wider font-semibold">Agent</span>
              <div className="bg-slate-900/80 border border-slate-850 rounded-2xl rounded-tl-none px-4 py-3 flex gap-1.5 items-center">
                {[0, 150, 300].map((delay) => (
                  <span
                    key={delay}
                    className="w-1.5 h-1.5 rounded-full bg-slate-500 animate-bounce"
                    style={{ animationDelay: `${delay}ms` }}
                  />
                ))}
              </div>
            </div>
          )}

          <div ref={endRef} />
        </div>

        {/* Quick prompts */}
        <div className="px-4 py-3 border-t border-slate-800/80 bg-slate-950/20 flex gap-2 flex-wrap items-center">
          {QUICK_PROMPTS.map((prompt) => (
            <button
              key={prompt}
              type="button"
              onClick={() => setInput(prompt)}
              className="text-[10px] px-2.5 py-1 rounded-lg border border-slate-800 bg-slate-900/60 text-slate-400 hover:border-emerald-500/50 hover:text-emerald-300 hover:bg-emerald-950/20 transition-all duration-200"
            >
              {prompt}
            </button>
          ))}
        </div>

        {/* Input row */}
        <div className="px-4 py-4 border-t border-slate-850 bg-slate-950/30 flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter") void submitPrompt(input); }}
            placeholder="Plan a trip, check budget, weather, stays..."
            className="flex-1 h-10 rounded-xl border border-slate-800 bg-slate-950 px-3.5 text-xs text-slate-200 placeholder:text-slate-500 outline-none focus:border-emerald-500 transition-colors"
          />
          <button
            type="button"
            onClick={() => void submitPrompt(input)}
            disabled={isSending}
            className="h-10 px-4 rounded-xl bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed text-white text-xs font-semibold transition-all duration-200 flex items-center gap-1.5 shadow-lg shadow-emerald-950/20"
          >
            {isSending ? "Sending…" : "Send"}
          </button>
        </div>
      </div>

      {/* Right Panel: Showcase Panel (7 Cols) */}
      <div className="lg:col-span-7 flex flex-col h-[620px] bg-slate-900/35 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl backdrop-blur-md">
        
        {/* Showcase Header */}
        <div className="px-5 py-4 border-b border-slate-800 bg-slate-950/30 flex items-center justify-between">
          <div>
            <h2 className="text-sm font-bold tracking-tight text-white flex items-center gap-2">
              🧭 Explorush Travel Plan Showcase
            </h2>
            <p className="text-[10px] text-slate-400">
              {selectedMessage && selectedMessage.meta?.trekName 
                ? `Structured proposal details for: ${selectedMessage.meta.trekName}`
                : "Enter a planning request on the left to generate details"}
            </p>
          </div>
        </div>

        {/* Display Content */}
        {hasShowcaseData ? (
          <div className="flex-1 flex flex-col overflow-hidden">
            {/* Tabs */}
            <div className="flex border-b border-slate-800 bg-slate-950/15 overflow-x-auto">
              {[
                { id: "itinerary", label: "🗺️ Itinerary", enabled: !!itineraryContent },
                { id: "budget", label: "💰 Budget Plan", enabled: !!budgetContent },
                { id: "stays", label: "🏨 Stays & Food", enabled: !!staysContent },
                { id: "packing", label: "🎒 Packing List", enabled: !!packingContent },
                { id: "weather", label: "🌤️ Weather & Safety", enabled: !!weatherContent },
              ].map((tab) => (
                <button
                  key={tab.id}
                  type="button"
                  disabled={!tab.enabled}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`flex-1 py-3 text-center text-[11px] font-semibold tracking-wide border-b-2 whitespace-nowrap px-4 transition-all duration-200 ${
                    !tab.enabled 
                      ? "opacity-25 cursor-not-allowed border-transparent text-slate-600" 
                      : activeTab === tab.id
                      ? "border-emerald-500 text-emerald-400 bg-slate-800/20"
                      : "border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-900/30"
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </div>

            {/* Tab content */}
            <div className="flex-1 overflow-y-auto px-6 py-5 bg-slate-900/10">
              {activeTab === "itinerary" && itineraryContent && (
                <div className="animate-fadeIn">
                  <Markdown content={itineraryContent} />
                </div>
              )}
              {activeTab === "budget" && budgetContent && (
                <div className="animate-fadeIn">
                  <Markdown content={budgetContent} />
                </div>
              )}
              {activeTab === "stays" && staysContent && (
                <div className="animate-fadeIn">
                  <Markdown content={staysContent} />
                </div>
              )}
              {activeTab === "packing" && packingContent && (
                <div className="animate-fadeIn">
                  <Markdown content={packingContent} />
                </div>
              )}
              {activeTab === "weather" && weatherContent && (
                <div className="animate-fadeIn">
                  <Markdown content={weatherContent} />
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center text-center p-8 bg-slate-900/5">
            <span className="text-4xl mb-3">🧭</span>
            <h3 className="text-sm font-semibold text-slate-300">No active proposal showcase</h3>
            <p className="text-xs text-slate-500 max-w-sm mt-1">
              Ask the assistant to *\"Plan a 4 day Goa trip\"* or *\"Recommend weekend trips from Mumbai\"* to visualize structured itineraries, cost tables, and packing lists side-by-side!
            </p>
          </div>
        )}
      </div>

    </div>
  );
}