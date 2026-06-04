import { ChatConsole } from "../components/trek-dashboard";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-slate-50 dark:bg-slate-950 p-6">
      <div className="w-full max-w-2xl">
        <div className="mb-4 flex items-center gap-2">
          <span className="text-lg font-medium text-slate-900 dark:text-slate-100">TrekForge</span>
          <span className="text-xs text-slate-400">/ Agent console</span>
        </div>
        <ChatConsole />
      </div>
    </main>
  );
}