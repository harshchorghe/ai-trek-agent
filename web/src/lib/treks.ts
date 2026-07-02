export type Trek = {
  slug: string;
  name: string;
  difficulty: string;
  duration: string;
  height: string;
  summary: string;
  bestFor: string;
};

export type Destination = {
  slug: string;
  name: string;
  type: "beach" | "mountain" | "hills" | "historical" | "trek";
  minBudget: number;
  duration: string;
  summary: string;
  bestFor: string;
  highlights: string[];
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

export const DESTINATIONS: Destination[] = [
  {
    slug: "goa",
    name: "Goa",
    type: "beach",
    minBudget: 8000,
    duration: "3-4 days",
    summary: "India's pocket-sized paradise, known for its beautiful beaches, Portuguese heritage, and vibrant nightlife.",
    bestFor: "Beach lovers, nightlife seekers, seafood lovers, and leisure travelers.",
    highlights: ["Calangute Beach", "Fontainhas Latin Quarter", "Basilica of Bom Jesus", "Chapora Fort"]
  },
  {
    slug: "manali",
    name: "Manali",
    type: "mountain",
    minBudget: 12000,
    duration: "4-5 days",
    summary: "A high-altitude Himalayan resort town known for its cool climate, snow-capped peaks, and adventure sports.",
    bestFor: "Families, honeymooners, snow seekers, and adventure sports fans.",
    highlights: ["Solang Valley", "Rohtang Pass", "Hadimba Temple", "Old Manali"]
  },
  {
    slug: "ladakh",
    name: "Ladakh",
    type: "mountain",
    minBudget: 25000,
    duration: "5-7 days",
    summary: "A land of high passes, spectacular lakes, and ancient monasteries, perfect for road trips and adventure seekers.",
    bestFor: "Bikers, adventure lovers, photographers, and solo backpackers.",
    highlights: ["Pangong Tso Lake", "Khardung La Pass", "Nubra Valley", "Diskit Monastery"]
  },
  {
    slug: "lonavala",
    name: "Lonavala",
    type: "hills",
    minBudget: 3000,
    duration: "1-2 days",
    summary: "A popular hill station close to Mumbai and Pune, famous for its lush green valleys, waterfalls, and chikki.",
    bestFor: "Quick weekend getaways, monsoon road trips, and families.",
    highlights: ["Tiger's Point", "Bhushi Dam", "Karla Caves", "Lohagad Fort"]
  },
  {
    slug: "mahabaleshwar",
    name: "Mahabaleshwar",
    type: "hills",
    minBudget: 4500,
    duration: "2-3 days",
    summary: "A scenic hill station in the Western Ghats range, known for its strawberry farms, valleys, and colonial style.",
    bestFor: "Couples, family outings, and strawberry picking.",
    highlights: ["Arthur's Seat", "Venna Lake", "Mapro Garden", "Elephant's Head Point"]
  },
  {
    slug: "ujjain",
    name: "Ujjain",
    type: "historical",
    minBudget: 3500,
    duration: "2-3 days",
    summary: "An ancient city situated on the banks of the Shipra River, famous for the Mahakaleshwar Jyotirlinga temple and the Kumbh Mela.",
    bestFor: "Spiritual travelers, family pilgrimage groups, and history/archeology enthusiasts.",
    highlights: ["Mahakaleshwar Temple", "Kal Bhairav Temple", "Ram Ghat Aarti", "Sandipani Ashram"]
  }
];

export const QUICK_PROMPTS = [
  "Plan a trip to Goa for 4 days",
  "Recommend places under 10000",
  "Is Manali safe in monsoon?",
  "Plan a trek to Kalsubai this weekend",
  "How difficult is Harihar for beginners?"
];

export const CAPABILITIES = [
  "Destination recommendations",
  "Tailored travel itineraries",
  "Detailed budget estimation",
  "Dynamic packing & safety checklists",
  "Weather windows & travel advisories",
  "Trek routing & difficulty summaries"
];