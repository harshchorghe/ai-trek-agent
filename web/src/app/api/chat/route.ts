import { NextResponse } from "next/server";

import { buildAgentResponse, type ChatMessage } from "@/lib/agent";

export const runtime = "nodejs";

export async function POST(request: Request) {
  try {
    const payload = (await request.json()) as { messages?: ChatMessage[] };
    const messages = Array.isArray(payload.messages) ? payload.messages : [];
    const response = await buildAgentResponse(messages);

    return NextResponse.json(response);
  } catch {
    return NextResponse.json(
      {
        reply: "The agent API could not process that request.",
        tool: "chat",
        trekName: null,
        source: "local",
        facts: [],
        suggestions: ["Try a trek planning prompt", "Ask for packing advice", "Ask about trek difficulty"],
      },
      { status: 500 },
    );
  }
}