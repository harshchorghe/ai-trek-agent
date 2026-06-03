export type Trek = {
  slug: string;
  name: string;
  difficulty: string;
  duration: string;
  height: string;
  summary: string;
  bestFor: string;
};

export const TREKS: Trek[] = [
  {
    slug: "kalsubai",
    name: "Kalsubai",
    difficulty: "Moderate",
    duration: "4-5 hours",
    height: "5400 ft",
    summary: "Maharashtra's highest peak and a strong client-facing hero trek.",
    bestFor: "Signature summit shots, sunrise climbs, and structured weekend itineraries.",
  },
  {
    slug: "rajmachi",
    name: "Rajmachi",
    difficulty: "Easy",
    duration: "3-4 hours",
    height: "2710 ft",
    summary: "A beginner-friendly route with broad appeal for relaxed planning decks.",
    bestFor: "Low-friction group outings, monsoon add-ons, and first-time hikers.",
  },
  {
    slug: "harihar",
    name: "Harihar",
    difficulty: "Hard",
    duration: "3 hours",
    height: "3676 ft",
    summary: "A dramatic, high-energy trek that reads well in premium adventure proposals.",
    bestFor: "Advanced hikers, signature challenge content, and bold campaign visuals.",
  },
];

export const QUICK_PROMPTS = [
  "Plan a trek to Kalsubai this weekend",
  "What should I pack for a monsoon trek?",
  "How difficult is Harihar for a beginner?",
  "Give me a one-day itinerary for Rajmachi",
];

export const CAPABILITIES = [
  "Trek routing and classification",
  "Packing and safety recommendations",
  "Difficulty and duration summaries",
  "Client-ready trip planning responses",
];