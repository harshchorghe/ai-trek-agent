import { TrekDashboard } from "@/components/trek-dashboard";
import { TREKS } from "@/lib/treks";

export default function Home() {
  return <TrekDashboard treks={TREKS} />;
}
