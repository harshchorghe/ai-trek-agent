import { TREKS, type Trek } from "@/lib/treks";

export type ChatRole = "user" | "assistant";

export type ChatMessage = {
  role: ChatRole;
  content: string;
};

export type ToolName =
  | "planner"
  | "packing"
  | "difficulty"
  | "itinerary"
  | "weather"
  | "trek_info"
  | "chat";

export type AgentResponse = {
  reply: string;
  tool: ToolName;
  trekName: string | null;
  source: "local" | "ollama";
  facts: Array<{ label: string; value: string }>;
  suggestions: string[];
};

const MODEL = process.env.OLLAMA_MODEL ?? "phi3";

function normalize(text: string) {
  return text.trim().toLowerCase();
}

function detectTool(text: string): ToolName {
  const normalized = normalize(text);

  if (
    ["plan a trek", "trek plan", "plan trek", "complete plan", "full plan", "plan my trek"].some(
      (keyword) => normalized.includes(keyword),
    )
  ) {
    return "planner";
  }

  if (["packing", "packing list", "pack", "carry", "bag", "what should i carry"].some((keyword) => normalized.includes(keyword))) {
    return "packing";
  }

  if (["difficulty", "hard", "easy", "moderate", "how difficult"].some((keyword) => normalized.includes(keyword))) {
    return "difficulty";
  }

  if (["itinerary", "schedule"].some((keyword) => normalized.includes(keyword))) {
    return "itinerary";
  }

  if (["weather", "forecast", "temperature", "rain"].some((keyword) => normalized.includes(keyword))) {
    return "weather";
  }

  if (["tell me about", "information about", "details about", "height", "duration"].some((keyword) => normalized.includes(keyword))) {
    return "trek_info";
  }

  return "chat";
}

function findTrek(text: string): Trek | null {
  const normalized = normalize(text);
  return TREKS.find((trek) => normalized.includes(trek.slug) || normalized.includes(trek.name.toLowerCase())) ?? null;
}

function factsForTrek(trek: Trek | null) {
  if (!trek) {
    return [];
  }

  return [
    { label: "Difficulty", value: trek.difficulty },
    { label: "Duration", value: trek.duration },
    { label: "Height", value: trek.height },
  ];
}

function quickReplies(tool: ToolName, trek: Trek | null) {
  if (tool === "packing") {
    return ["Show a monsoon version", "Add beginner safety tips", "Build a day-bag checklist"];
  }

  if (tool === "planner" || tool === "itinerary") {
    return trek
      ? [`Adjust this for ${trek.name}`, "Add transport guidance", "Make it client presentation ready"]
      : ["Add a trek name", "Make it a weekend plan", "Include safety checkpoints"];
  }

  if (tool === "difficulty") {
    return ["Compare two treks", "Add fitness guidance", "Show beginner alternatives"];
  }

  return ["Plan a weekend trek", "Recommend a beginner trek", "What should I pack?"];
}

function buildLocalReply(tool: ToolName, trek: Trek | null, input: string) {
  if (tool === "packing") {
    return [
      "Client-ready packing guidance:",
      "- Water, snacks, rain layer, and a small first-aid kit",
      "- Grip-friendly shoes with socks that dry fast",
      "- Power bank, ID, cash, and a compact torch",
      "- For monsoon hikes, add a dry bag and spare tee",
    ].join("\n");
  }

  if (tool === "difficulty") {
    if (trek) {
      return [
        `${trek.name} is rated ${trek.difficulty}.`,
        `Expected effort: ${trek.duration} with an elevation of ${trek.height}.`,
        "Good pacing, early start times, and weather checks will keep the experience client-safe and manageable.",
      ].join("\n\n");
    }

    return [
      "I can assess difficulty once you name the trek.",
      "Share the route and I’ll return a concise difficulty summary with effort, duration, and height.",
    ].join("\n\n");
  }

  if (tool === "itinerary") {
    return [
      "Sample one-day itinerary:",
      "1. Early departure and meet-up",
      "2. Ascent with hydration and short breaks",
      "3. Summit photos, snacks, and safety check",
      "4. Controlled descent before dark",
    ].join("\n");
  }

  if (tool === "weather") {
    return [
      "Weather-aware guidance:",
      "- Check the forecast 24 hours before departure",
      "- In monsoon months, plan for slippery rock patches and reduced visibility",
      "- Start early and keep an alternate descent plan ready",
    ].join("\n");
  }

  if (tool === "trek_info") {
    if (trek) {
      return [
        `${trek.name} overview:`,
        `Difficulty: ${trek.difficulty}`,
        `Duration: ${trek.duration}`,
        `Height: ${trek.height}`,
        trek.summary,
      ].join("\n");
    }

    return [
      "I can summarise a trek once you name it.",
      "Try Kalsubai, Rajmachi, or Harihar to see the structured summary format.",
    ].join("\n");
  }

  if (tool === "planner") {
    if (trek) {
      return [
        `Plan for ${trek.name}:`,
        `- Difficulty: ${trek.difficulty}`,
        `- Duration: ${trek.duration}`,
        `- Height: ${trek.height}`,
        "- Start early, keep a steady pace, and build in weather buffers",
        "- End with enough daylight for a safe descent and transport handoff",
      ].join("\n");
    }

    return [
      "I can build a full trek plan once you name the route.",
      "That plan can include timing, packing, safety, and a summary suitable for client handoff.",
    ].join("\n\n");
  }

  return input;
}

async function askOllama(messages: ChatMessage[]) {
  const conversation = messages
    .slice(-8)
    .map((message) => `${message.role === "user" ? "User" : "Assistant"}: ${message.content}`)
    .join("\n");

  const prompt = `
You are TrekForge, a polished client-facing trekking assistant for Maharashtra.
Keep the answer practical, confident, and concise.
Use short paragraphs or bullets when helpful.

Conversation:
${conversation}

Assistant:
`.trim();

  try {
    const response = await fetch("http://127.0.0.1:11434/api/generate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: MODEL,
        prompt,
        stream: false,
        options: {
          temperature: 0.2,
          num_predict: 220,
        },
      }),
    });

    if (!response.ok) {
      return null;
    }

    const data = (await response.json()) as { response?: string };
    return data.response?.trim() || null;
  } catch {
    return null;
  }
}

export async function buildAgentResponse(messages: ChatMessage[]): Promise<AgentResponse> {
  const lastUserMessage = [...messages].reverse().find((message) => message.role === "user");

  if (!lastUserMessage) {
    return {
      reply: "Send a trek question to start the assistant.",
      tool: "chat",
      trekName: null,
      source: "local",
      facts: [],
      suggestions: ["Plan a trek to Kalsubai", "What should I pack for monsoon?", "How difficult is Rajmachi?"],
    };
  }

  const tool = detectTool(lastUserMessage.content);
  const trek = findTrek(lastUserMessage.content);

  if (tool === "chat") {
    const ollamaReply = await askOllama(messages);

    if (ollamaReply) {
      return {
        reply: ollamaReply,
        tool,
        trekName: trek?.name ?? null,
        source: "ollama",
        facts: factsForTrek(trek),
        suggestions: quickReplies(tool, trek),
      };
    }

    return {
      reply: [
        "I’m ready to help with trekking planning, but the local model is not reachable right now.",
        "Try asking for a trek plan, packing list, difficulty check, or a trek summary.",
      ].join("\n\n"),
      tool,
      trekName: trek?.name ?? null,
      source: "local",
      facts: factsForTrek(trek),
      suggestions: quickReplies(tool, trek),
    };
  }

  return {
    reply: buildLocalReply(tool, trek, lastUserMessage.content),
    tool,
    trekName: trek?.name ?? null,
    source: "local",
    facts: factsForTrek(trek),
    suggestions: quickReplies(tool, trek),
  };
}