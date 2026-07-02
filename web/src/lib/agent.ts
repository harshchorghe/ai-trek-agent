import { TREKS, DESTINATIONS, type Trek, type Destination } from "@/lib/treks";

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
  | "chat"
  | "budget"
  | "hotel"
  | "restaurant"
  | "destination"
  | "transport"
  | "emergency"
  | "visa"
  | "currency"
  | "nearby"
  | "activities"
  | "faq";

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
    ["plan a trip", "plan my trip", "trip plan", "full plan", "complete plan", "itinerary for", "schedule for", "road trip to", "travel plan", "planning a", "planning to", "planning trip", "trip to", "going to", "travel to", "travelling to"].some(
      (keyword) => normalized.includes(keyword)
    )
  ) {
    return "planner";
  }

  if (
    ["when should i", "best time to", "when to visit", "suitable for", "is it safe", "is manali safe", "can i go to"].some(
      (keyword) => normalized.includes(keyword)
    )
  ) {
    return "faq";
  }

  if (
    ["budget", "cost", "how much money", "price", "expensive", "cheap", "estimate", "expense"].some(
      (keyword) => normalized.includes(keyword)
    )
  ) {
    return "budget";
  }

  if (
    ["packing", "packing list", "pack", "carry", "bag", "luggage", "checklist", "what should i carry"].some(
      (keyword) => normalized.includes(keyword)
    )
  ) {
    return "packing";
  }

  if (
    ["weather", "forecast", "temperature", "rain", "snow", "climate", "degree"].some(
      (keyword) => normalized.includes(keyword)
    )
  ) {
    return "weather";
  }

  if (
    ["hotel", "hostel", "resort", "homestay", "stay", "accommodation", "where to sleep", "places to stay"].some(
      (keyword) => normalized.includes(keyword)
    )
  ) {
    return "hotel";
  }

  if (
    ["restaurant", "cafe", "food", "eat", "street food", "dining", "cuisine", "breakfast", "lunch", "dinner", "cafes"].some(
      (keyword) => normalized.includes(keyword)
    )
  ) {
    return "restaurant";
  }

  if (
    ["suggest places", "recommend places", "where should i go", "go somewhere", "weekend trip", "holiday destinations", "best destinations", "hidden places", "somewhere this weekend"].some(
      (keyword) => normalized.includes(keyword)
    )
  ) {
    return "destination";
  }

  if (
    ["flight", "train", "cab", "bus", "transportation", "how to reach", "drive", "road trip", "public transport"].some(
      (keyword) => normalized.includes(keyword)
    )
  ) {
    return "transport";
  }

  if (
    ["safety", "emergency", "scam", "danger", "safe", "hospital", "police", "scams"].some(
      (keyword) => normalized.includes(keyword)
    )
  ) {
    return "emergency";
  }

  if (
    ["visa", "passport", "entry requirements"].some(
      (keyword) => normalized.includes(keyword)
    )
  ) {
    return "visa";
  }

  if (
    ["currency", "money exchange", "forex"].some(
      (keyword) => normalized.includes(keyword)
    )
  ) {
    return "currency";
  }

  if (
    ["attraction", "photography", "hidden gem", "sightseeing", "places to see", "tourist spot", "nearby points"].some(
      (keyword) => normalized.includes(keyword)
    )
  ) {
    return "nearby";
  }

  if (
    ["activities", "camping", "adventure", "sports", "beach activities", "rafting", "paragliding"].some(
      (keyword) => normalized.includes(keyword)
    )
  ) {
    return "activities";
  }

  if (
    ["trek", "hike", "climb", "difficulty", "hard", "easy", "moderate", "how difficult", "kalsubai", "rajmachi", "harihar", "height", "duration"].some(
      (keyword) => normalized.includes(keyword)
    )
  ) {
    return "trek_info";
  }

  return "chat";
}

function findTrekOrDestination(text: string): { type: "trek" | "destination"; name: string; details: any } | null {
  const normalized = normalize(text);
  
  // Try to match destination first
  const dest = DESTINATIONS.find((d) => normalized.includes(d.slug) || normalized.includes(d.name.toLowerCase()));
  if (dest) {
    return { type: "destination", name: dest.name, details: dest };
  }

  // Try to match trek
  const trek = TREKS.find((t) => normalized.includes(t.slug) || normalized.includes(t.name.toLowerCase()));
  if (trek) {
    return { type: "trek", name: trek.name, details: trek };
  }

  return null;
}

function factsForMatch(match: { type: "trek" | "destination"; name: string; details: any } | null) {
  if (!match) {
    return [];
  }

  if (match.type === "destination") {
    const dest = match.details as Destination;
    return [
      { label: "Type", value: dest.type.toUpperCase() },
      { label: "Est. Budget", value: `₹${dest.minBudget}` },
      { label: "Duration", value: dest.duration },
    ];
  } else {
    const trek = match.details as Trek;
    return [
      { label: "Difficulty", value: trek.difficulty },
      { label: "Duration", value: trek.duration },
      { label: "Height", value: trek.height },
    ];
  }
}

function quickReplies(tool: ToolName, match: { type: "trek" | "destination"; name: string; details: any } | null) {
  const name = match?.name ?? "Goa";
  
  if (tool === "packing") {
    return ["What should I pack for trekking?", "Monsoon road trip packing checklist", "Packing gear for cold weather"];
  }

  if (tool === "planner" || tool === "itinerary") {
    return [`Adjust itinerary for ${name}`, `Show me hotels in ${name}`, `Get budget breakdown for ${name}`];
  }

  if (tool === "budget") {
    return [`Is this budget enough for ${name}?`, `Suggest budget resorts in ${name}`, `Compare costs for Goa vs Manali`];
  }

  if (tool === "destination") {
    return ["Suggest weekend trips from Mumbai", "Recommend hidden gems in Maharashtra", "Best solo destinations in winter"];
  }

  return ["Plan a 4-day Goa trip", "Is Manali safe in monsoon?", "What are the top things to do in Ladakh?"];
}

function buildLocalReply(
  tool: ToolName,
  match: { type: "trek" | "destination"; name: string; details: any } | null,
  input: string
): string {
  const name = match?.name ?? "Goa";
  const nameLower = name.toLowerCase();

  if (tool === "planner") {
    return [
      `🏝️ **Explorush Travel Plan: ${name.toUpperCase()}**`,
      "--------------------------------------------------",
      `- **Duration**: 3-4 Days`,
      `- **Transport**: Flight to nearest airport or road trip route.`,
      `- **Accommodation**: Boutique stay or hostel according to budget.`,
      `- **Itinerary Summary**: Explore major attractions on Day 1-2, outdoor activities on Day 3, and shopping/departure on Day 4.`,
      `- **Budget**: Starts at ₹8,000 per person.`,
      `- **Weather Advice**: Weather is generally suitable. Plan buffers for seasons.`,
      "--------------------------------------------------",
      "💡 *Tip*: Use specific tools like 'hotels in Goa' or 'budget for Manali' to expand any of these cards!"
    ].join("\n");
  }

  if (tool === "budget") {
    return [
      `💰 **Estimated Budget Plan for ${name} (3 Days · Mid-range Style)**`,
      "",
      `- 🏨 **Accommodation**: ₹7,500 (Hotel room for 3 nights)`,
      `- 🚗 **Transport**: ₹3,600 (Local rental cab/scooter)`,
      `- 🍽️ **Food & Drinks**: ₹3,600 (Daily casual cafes)`,
      `- 🎡 **Activities**: ₹2,400 (Entry tickets & tours)`,
      `- 🛡️ **Emergency Buffer**: ₹1,800 (10% contingency)`,
      `- 💵 **Total Estimate**: **₹18,900** per person.`,
      "",
      "💡 *Tip*: Travel off-season (Monsoon in Goa, or spring in Manali) to get hotel discounts up to 40%!"
    ].join("\n");
  }

  if (tool === "packing") {
    return [
      "🎒 **Explorush Travel Packing Checklist**",
      "",
      "📌 **Essential Packing List**:",
      "- IDs, tickets, and booking confirmations saved offline",
      "- High-capacity power bank & charger cables",
      "- Small medical kit (rehydration salts, painkillers, bandages)",
      "- Comfortable shoes & flip-flops",
      "- High SPF sunscreen & sunglasses"
    ].join("\n");
  }

  if (tool === "weather") {
    return [
      `🌤️ **Weather Forecast & Advice for ${name}**`,
      "",
      "- **Current Average**: 22°C to 28°C",
      "- **Humidity**: Moderate",
      "- **Advice**: Excellent weather for sightseeing. Carry lightweight cotton clothes and a light jacket for cold nights.",
      "⚠️ *Caution*: In monsoon months, check for local rainfall warnings and road blocks before travelling."
    ].join("\n");
  }

  if (tool === "hotel") {
    return [
      `🏨 **Recommended Accommodations in ${name}**:`,
      "",
      "- 🎒 **Budget**: Zostel or Hosteller (Social hostels, great for solo backpackers)",
      "- 🏢 **Mid-range**: Bloom Suites or Local Boutique Hotels (Comfortable, family-friendly)",
      "- 👑 **Luxury**: Taj Resorts or Local Premium Heritage Mansions"
    ].join("\n");
  }

  if (tool === "restaurant") {
    return [
      `🍽️ **Foodie & Restaurant Recommendations in ${name}**:`,
      "",
      "- ☕ **Cafes**: Artjuna / Old Manali riverside cafes (Relaxed ambience & good coffee)",
      "- 🍲 **Restaurants**: Fisherman's Wharf / Local fine dining (Famous local specialties)",
      "- 🍢 **Street Food**: Try local street markets for traditional snacks (Cutlet bread, Siddu, or Vada Pav)"
    ].join("\n");
  }

  if (tool === "destination") {
    return [
      "🎒 **Explorush Curated Destination Recommendations**:",
      "",
      "- 🏖️ **Goa**: Perfect for beaches, parties, and Portuguese heritage trails.",
      "- 🏔️ **Manali**: Perfect for snow peaks, river rafting, and cafe hopping.",
      "- 🚴 **Ladakh**: Ideal for adventure seekers, biking trips, and lakes.",
      "- 🍃 **Lonavala / Mahabaleshwar**: Excellent weekend hills getaways near Mumbai."
    ].join("\n");
  }

  if (tool === "transport") {
    return [
      `🚗 **How to Reach & Local Commute in ${name}**:`,
      "",
      "- ✈️ **By Flight**: Fly to nearest commercial airport followed by pre-booked taxi transfer.",
      "- 🚂 **By Train**: Book tickets via IRCTC to the nearest junction.",
      "- 🛵 **Local Commute**: Renting self-drive scooters or hiring local cabs is highly recommended."
    ].join("\n");
  }

  if (tool === "emergency") {
    return [
      `🛡️ **Safety & Emergency Helplines for ${name}**:`,
      "",
      "- 🚨 **Avoid Scams**: Do not rent vehicles without filming a 360-degree video first. Avoid helpful strangers at ATMs.",
      "- ☎️ **All-in-one Emergency Number**: 112",
      "- ☎️ **Tourist Helpline**: 1363",
      "- 💡 **Tip**: Save hotel address offline and keep emergency cash in a separate pocket."
    ].join("\n");
  }

  if (tool === "visa") {
    return [
      "🛂 **General Visa Guidance (Indian Citizens)**:",
      "",
      "- 🏝️ **Thailand / Vietnam**: eVisa or Visa-on-Arrival is available. Confirm cash currency requirements.",
      "- 🇪🇺 **Schengen Area (Europe)**: Apply via VFS Global at least 30 days prior. Requires medical travel insurance and detailed itinerary.",
      "- 🏔️ **Nepal & Bhutan**: Visa-free. Valid Passport or Voter ID is required for entry."
    ].join("\n");
  }

  if (tool === "currency") {
    return [
      "💵 **Currency & Money Management Tips**:",
      "",
      "- **Cash**: Essential for minor street vendors, tolls, and remote mountain villages.",
      "- **Digital Payments**: UPI is widely accepted in India. Carry physical cards for hotels.",
      "- **Exchange**: Avoid airport exchange counters. Buy a zero-forex card or exchange at authorized city dealer booths."
    ].join("\n");
  }

  if (tool === "nearby") {
    return [
      `📸 **Top Sights & Hidden Gems in ${name}**:`,
      "",
      "- 🏛️ **Attractions**: Historic forts, museum heritage houses, and central viewpoints.",
      "- 💎 **Hidden Gems**: Offbeat beaches (Cola Beach) or quiet village waterfalls.",
      "- 📷 **Best Photo spots**: Historic quarters, sunset points, and palm-lined roads."
    ].join("\n");
  }

  if (tool === "activities") {
    return [
      `🏂 **Adventure & Leisure Activities in ${name}**:`,
      "",
      "- 🪂 **High Adventure**: Paragliding, white-water rafting, or scuba diving depending on location.",
      "- 🏕️ **Outdoor Experience**: Lakeside camping, stargazing, and hiking.",
      "- 🛶 **Leisure**: Mangrove kayaking, boat cruises, and shopping spice tours."
    ].join("\n");
  }

  if (tool === "faq") {
    if (input.toLowerCase().includes("visit goa")) {
      return [
        "🌅 **Best Time to Visit Goa FAQ**:",
        "- **Peak Season (Nov-Feb)**: Perfect sunny weather, beaches are fully active.",
        "- **Monsoon (Jun-Sep)**: Quiet, lush landscapes, but water sports are suspended."
      ].join("\n");
    }
    if (input.toLowerCase().includes("manali safe")) {
      return [
        "🏔️ **Safety in Manali FAQ**:",
        "- Manali is generally very safe. Avoid traveling during peak monsoon (July-August) due to landslide risks."
      ].join("\n");
    }
    return [
      "🌸 **Travel FAQ Support**:",
      "I can answer queries about the best time to visit, safety, visa requirements, or child suitability. Ask me directly!"
    ].join("\n");
  }

  if (tool === "itinerary") {
    return [
      `📅 **Suggested 3-Day Itinerary for ${name}**:`,
      "",
      "**Day 1: Arrival & Local Walks**",
      "- Check-in, visit nearby cafes, sunset at closest viewpoint.",
      "",
      "**Day 2: Sightseeing Tour**",
      "- Full day exploring historic highlights and eating local foods.",
      "",
      "**Day 3: Adventure & Departure**",
      "- Adventure sports, gift shopping, and return journey."
    ].join("\n");
  }

  if (tool === "trek_info" || tool === "difficulty") {
    const trek = TREKS.find((t) => nameLower.includes(t.slug) || t.slug.includes(nameLower));
    if (trek) {
      return [
        `🥾 **Trek Details: ${trek.name}**`,
        `- **Difficulty**: ${trek.difficulty}`,
        `- **Duration**: ${trek.duration}`,
        `- **Height**: ${trek.height}`,
        `- **Summary**: ${trek.summary}`,
        `- **Best For**: ${trek.bestFor}`
      ].join("\n");
    }
    return [
      `🥾 **Trekking Guidance**:`,
      `We support Maharashtra treks like Kalsubai, Rajmachi, and Harihar.`,
      `Specify a trek name to view difficulty, height, and route advice.`
    ].join("\n");
  }

  return input;
}

async function askOllama(messages: ChatMessage[]) {
  const conversation = messages
    .slice(-8)
    .map((message) => `${message.role === "user" ? "User" : "Assistant"}: ${message.content}`)
    .join("\n");

  const prompt = `
You are an experienced, friendly, and professional travel consultant for Explorush.
Answer the user request naturally and helpfully. Keep the answer practical and concise.
Use short paragraphs or bullets.

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
      reply: "Send a travel question to start the assistant.",
      tool: "chat",
      trekName: null,
      source: "local",
      facts: [],
      suggestions: ["Plan a trip to Goa", "Recommend weekend trips", "What should I pack for camping?"],
    };
  }

  const tool = detectTool(lastUserMessage.content);
  const match = findTrekOrDestination(lastUserMessage.content);

  // Scan back to find the active destination context from history if none is in the current message
  let activeMatch = match;
  if (!activeMatch) {
    for (const msg of [...messages].reverse()) {
      if (msg.role === "user") {
        const historyMatch = findTrekOrDestination(msg.content);
        if (historyMatch) {
          activeMatch = historyMatch;
          break;
        }
      }
    }
  }

  if (tool === "chat") {
    const ollamaReply = await askOllama(messages);

    if (ollamaReply) {
      return {
        reply: ollamaReply,
        tool,
        trekName: activeMatch?.name ?? null,
        source: "ollama",
        facts: factsForMatch(activeMatch),
        suggestions: quickReplies(tool, activeMatch),
      };
    }

    return {
      reply: [
        "I'm ready to help with your travel planning, but the local AI model is currently offline.",
        "Try asking for a travel plan, budget breakdown, packing lists, or hotel recommendations to activate my travel tools."
      ].join("\n\n"),
      tool,
      trekName: activeMatch?.name ?? null,
      source: "local",
      facts: factsForMatch(activeMatch),
      suggestions: quickReplies(tool, activeMatch),
    };
  }

  return {
    reply: buildLocalReply(tool, activeMatch, lastUserMessage.content),
    tool,
    trekName: activeMatch?.name ?? null,
    source: "local",
    facts: factsForMatch(activeMatch),
    suggestions: quickReplies(tool, activeMatch),
  };
}