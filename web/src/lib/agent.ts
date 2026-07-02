import { MongoClient } from "mongodb";
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

// Read env vars dynamically in functions

// ============================================================
// MONGODB CACHING HELPERS
// ============================================================
const CACHE_EXPIRY_POLICIES: Record<string, number | null> = {
  weather: 3600,     // 1 Hour
  events: 86400,     // 24 Hours
};

function normalizeDestination(destination: string): string {
  if (!destination) return "";
  let text = destination.toLowerCase().trim();
  text = text.replace(/\b(junction|airport|station|terminal|city|town|village|beach|hills)\b/g, "").trim();
  text = text.replace(/[\s\-\/]+/g, "_");
  text = text.replace(/[^a-z0-9_]/g, "");
  return text.replace(/^_+|_+$/g, "");
}

let cachedClient: MongoClient | null = null;
let cachedDb: any = null;

async function connectToDatabase() {
  if (cachedClient && cachedDb) {
    return { client: cachedClient, db: cachedDb };
  }

  const uri = process.env.MONGODB_URI;
  if (!uri) throw new Error("No MONGODB_URI found");

  const client = new MongoClient(uri, {
    serverSelectionTimeoutMS: 5000,
    maxPoolSize: 10
  });

  await client.connect();
  const db = client.db("explorush_db");

  cachedClient = client;
  cachedDb = db;

  return { client, db };
}

async function getCachedSectionFromMongo(
  category: string,
  destination: string
): Promise<string | null> {
  const uri = process.env.MONGODB_URI;
  if (!uri) return null;
  
  const destNorm = normalizeDestination(destination);
  if (!destNorm) return null;
  
  const currentTime = Date.now() / 1000;
  
  try {
    const { db } = await connectToDatabase();
    
    // Index creation to guarantee performance
    await db.collection("destinations").createIndex({ normalizedDestination: 1 }, { unique: true });
    
    const doc = await db.collection("destinations").findOne({ normalizedDestination: destNorm });
    
    if (doc && doc.sections && doc.sections[category]) {
      const section = doc.sections[category];
      const expiry = section.expiry;
      const updatedAt = section.updatedAt;
      
      if (expiry !== null && expiry !== undefined && (currentTime - updatedAt) > expiry) {
        console.log(`⌛ Next.js Cache Expired: ${category} for ${destNorm} is stale.`);
        return null;
      }
      
      // Increment hit count asynchronously using pooled connection
      db.collection("destinations").updateOne(
        { normalizedDestination: destNorm },
        {
          $inc: {
            totalHits: 1,
            [`sections.${category}.hitCount`]: 1
          },
          $set: {
            lastAccessed: currentTime,
            [`sections.${category}.lastAccessed`]: currentTime
          }
        }
      ).catch(() => {});
      
      console.log(`🎯 Next.js KB Hit: ${category} for ${destNorm}`);
      return section.response || null;
    }
    return null;
  } catch (e) {
    console.error("Next.js: MongoDB KB fetch failed", e);
    return null;
  }
}

async function saveSectionToMongo(
  category: string,
  destination: string,
  value: string,
  source: string = "groq"
): Promise<void> {
  const uri = process.env.MONGODB_URI;
  if (!uri || !value) return;
  
  const destNorm = normalizeDestination(destination);
  if (!destNorm) return;
  
  const currentTime = Date.now() / 1000;
  const expiry = CACHE_EXPIRY_POLICIES[category] !== undefined ? CACHE_EXPIRY_POLICIES[category] : null;
  
  const sectionDoc = {
    response: value.trim(),
    createdAt: currentTime,
    updatedAt: currentTime,
    lastAccessed: currentTime,
    hitCount: 1,
    source,
    version: "1.0",
    expiry
  };
  
  try {
    const { db } = await connectToDatabase();
    
    await db.collection("destinations").updateOne(
      { normalizedDestination: destNorm },
      {
        $set: {
          destination: destination.trim(),
          normalizedDestination: destNorm,
          lastUpdated: currentTime,
          lastAccessed: currentTime,
          [`sections.${category}`]: sectionDoc
        },
        $setOnInsert: {
          createdAt: currentTime,
          totalHits: 0
        }
      },
      { upsert: true }
    );
    
    await db.collection("destinations").updateOne(
      { normalizedDestination: destNorm },
      { $inc: { totalHits: 1 } }
    );
    
    console.log(`💾 Next.js KB Save: Saved ${category} for ${destNorm}`);
  } catch (e) {
    console.error("Next.js: MongoDB KB save failed", e);
  }
}

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

function quickReplies(tool: ToolName, match: { type: "trek" | "destination"; name: string; details: any } | null, resolvedName: string | null) {
  const name = match?.name ?? resolvedName ?? "Goa";
  
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
  name: string,
  input: string
): string {
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
      "- 🏨 **Accommodation**: ₹7,500 (Hotel room for 3 nights)",
      "- 🚗 **Transport**: ₹3,600 (Local rental cab/scooter)",
      "- 🍽️ **Food & Drinks**: ₹3,600 (Daily casual cafes)",
      "- 🎡 **Activities**: ₹2,400 (Entry tickets & tours)",
      "- 🛡️ **Emergency Buffer**: ₹1,800 (10% contingency)",
      "- 💵 **Total Estimate**: **₹18,900** per person.",
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

async function askGroq(messages: ChatMessage[]): Promise<string | null> {
  const key = process.env.GROQ_API_KEY;
  if (!key) return null;
  
  const conversation = messages
    .slice(-8)
    .map((message) => ({
      role: message.role === "user" ? "user" : "assistant",
      content: message.content
    }));

  try {
    const response = await fetch("https://api.groq.com/openai/v1/chat/completions", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${key}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: "llama-3.3-70b-versatile",
        messages: [
          {
            role: "system",
            content: "You are an experienced, friendly, and professional travel consultant for Explorush. Answer the user request naturally and helpfully. Keep the answer practical and concise. Use short paragraphs or bullets."
          },
          ...conversation
        ],
        temperature: 0.2,
        max_tokens: 1024
      }),
    });

    if (!response.ok) {
      return null;
    }

    const data = await response.json();
    return data.choices?.[0]?.message?.content?.trim() || null;
  } catch (e) {
    console.error("Next.js: Groq API call failed", e);
    return null;
  }
}

function extractDestinationFromPrompt(input: string): string | null {
  const normalized = input.toLowerCase().trim();
  
  // Prioritize known cities in the prompt text
  const knownCities = ["goa", "manali", "ladakh", "lonavala", "mahabaleshwar", "ujjain", "tirupati", "jaipur", "rishikesh", "hampi", "alibaug"];
  for (const city of knownCities) {
    if (new RegExp(`\\b${city}\\b`, "i").test(normalized)) {
      return city.charAt(0).toUpperCase() + city.slice(1).toLowerCase();
    }
  }

  // Fallback to regex capture after action keywords
  const match = normalized.match(/(?:trip to|go to|travel to|visit|planning a trip to|planning to|planning trip to)\s+([a-zA-Z\s]+)/i);
  if (match && match[1]) {
    const words = match[1].trim().split(/\s+/);
    const stopWords = ["for", "in", "with", "this", "next", "during", "under", "budget", "of"];
    const filteredWords: string[] = [];
    for (const w of words) {
      if (stopWords.includes(w.toLowerCase())) break;
      filteredWords.push(w);
    }
    if (filteredWords.length > 0) {
      return filteredWords.map(w => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase()).join(" ");
    }
  }
  return null;
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

  const extractedName = extractDestinationFromPrompt(lastUserMessage.content);

  // Scan back to find the active destination context from history ONLY if none is in the current message
  let activeMatch = match;
  let historyExtractedName: string | null = null;
  if (!activeMatch && !extractedName) {
    for (const msg of [...messages].reverse()) {
      if (msg.role === "user") {
        const historyMatch = findTrekOrDestination(msg.content);
        if (historyMatch) {
          activeMatch = historyMatch;
          break;
        }
        const historyExt = extractDestinationFromPrompt(msg.content);
        if (historyExt) {
          historyExtractedName = historyExt;
          break;
        }
      }
    }
  }

  const name = activeMatch?.name ?? extractedName ?? historyExtractedName ?? null;

  if (!name && tool !== "chat") {
    return {
      reply: "Please specify a destination or trek name so I can help you (e.g., 'plan a trip to Jaipur', 'hotels in Dubai').",
      tool,
      trekName: null,
      source: "local",
      facts: [],
      suggestions: ["Plan a trip to Manali", "Hotels in Jaipur", "Packing list for Ladakh"],
    };
  }

  // GLOBAL CACHE CONNECTOR FOR ANY TRAVEL SUB-TOOL
  if (tool !== "chat") {
    const destName = name as string;
    let category = tool as string;
    if (tool === "planner") {
      category = "planner_3d_1p_mid-range";
    } else if (tool === "hotel") {
      category = "hotel_mid-range";
    }

    const isRefreshRequested = /refresh|update|reload/i.test(lastUserMessage.content);
    let cachedItem = null;
    if (!isRefreshRequested) {
      cachedItem = await getCachedSectionFromMongo(category, destName);
    }
    
    if (cachedItem) {
      return {
        reply: cachedItem,
        tool,
        trekName: activeMatch?.name ?? extractedName,
        source: "local",
        facts: factsForMatch(activeMatch),
        suggestions: quickReplies(tool, activeMatch, destName),
      };
    }

    // Call Groq API dynamically to generate a highly detailed response
    const key = process.env.GROQ_API_KEY;
    if (key) {
      let prompt = "";
      if (tool === "planner") {
        prompt = `Create a highly detailed, professional travel plan for ${destName}. Include:
1) Daily Itinerary
2) Estimated Budget Breakdown (as a markdown table using Indian Rupees ₹ / INR values)
3) Accommodation Planned (Budget, Mid-range, Luxury options with pricing estimates in Indian Rupees ₹)
4) Dining & Local Cuisine
5) Sightseeing & Hidden Gems
6) Adventure Activities
7) Weather Window & Advisory
8) Packing List
9) Safety & Emergency Information.

Use standard headers like '### Daily Itinerary' and '### Estimated Budget Breakdown' so the UI showcase tabs can extract them.`;
      } else if (tool === "hotel") {
        prompt = `Recommend 3 actual, popular real-world accommodation options (with names, budget range in Indian Rupees ₹, and brief descriptions) for a user traveling to ${destName} with a "Mid-range" travel style. Keep it realistic, detailed, and concise.`;
      } else if (tool === "restaurant") {
        prompt = `Recommend 3 actual, popular local eateries (including cafes, traditional restaurants, and street food areas) for a user visiting ${destName}. Write a brief, appetizing description for each. Keep it concise.`;
      } else if (tool === "transport") {
        prompt = `Write a clear, structured transportation guide for a user traveling to ${destName}. Provide real-world logistics advice on nearest airport transfer, nearby railway stations, highway routes, and local vehicle rentals. Keep it realistic and concise.`;
      } else if (tool === "nearby") {
        prompt = `Recommend sightseeing spots for a user visiting ${destName}. Provide 2-3 real major tourist attractions with name/description, 1-2 offbeat hidden gems, and 1-2 scenic photo spots. Keep it realistic and concise.`;
      } else if (tool === "budget") {
        prompt = `Estimate a detailed travel budget breakdown for a trip to ${destName} for 3 days. Format it as a markdown table with stay, transport, food, activities, and contingency. Use Indian Rupees (₹) and realistic INR costs. Keep it clean and concise.`;
      } else if (tool === "packing") {
        prompt = `Create a detailed travel packing checklist for a user visiting ${destName} based on its regional climate. Keep it categorized and concise.`;
      } else if (tool === "weather") {
        prompt = `Provide a current average weather forecast, seasonal guide, and safety advisory for a traveler visiting ${destName}. Keep it realistic and concise.`;
      } else {
        // General query prompt
        prompt = `Provide a detailed, practical, and helpful travel guide section about "${tool}" for a visitor going to ${destName}. Keep it concise.`;
      }

      const groqReply = await askGroq([{ role: "user", content: prompt }]);
      if (groqReply) {
        // Save the generated response to MongoDB Atlas
        await saveSectionToMongo(category, destName, groqReply);
        return {
          reply: groqReply,
          tool,
          trekName: activeMatch?.name ?? extractedName,
          source: "ollama", // "ollama" acts as model-source flag
          facts: factsForMatch(activeMatch),
          suggestions: quickReplies(tool, activeMatch, destName),
        };
      }
    }
  }

  if (tool === "chat") {
    const groqReply = await askGroq(messages);

    if (groqReply) {
      return {
        reply: groqReply,
        tool,
        trekName: activeMatch?.name ?? extractedName,
        source: "ollama",
        facts: factsForMatch(activeMatch),
        suggestions: quickReplies(tool, activeMatch, name),
      };
    }

    return {
      reply: [
        "I'm ready to help with your travel planning, but the Groq Cloud API is currently offline.",
        "Try asking for a travel plan, budget breakdown, packing lists, or hotel recommendations to activate my travel tools."
      ].join("\n\n"),
      tool,
      trekName: activeMatch?.name ?? extractedName,
      source: "local",
      facts: factsForMatch(activeMatch),
      suggestions: quickReplies(tool, activeMatch, name),
    };
  }

  return {
    reply: buildLocalReply(tool, name || "Goa", lastUserMessage.content),
    tool,
    trekName: activeMatch?.name ?? extractedName,
    source: "local",
    facts: factsForMatch(activeMatch),
    suggestions: quickReplies(tool, activeMatch, name),
  };
}