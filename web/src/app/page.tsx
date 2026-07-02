import { ChatConsole } from "../components/trek-dashboard";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-slate-950 p-6">
      <div className="w-full max-w-2xl">
        <div className="mb-6 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-xl font-bold tracking-tight text-white">Explorush AI</span>
            <span className="text-xs text-slate-400 px-2 py-0.5 rounded border border-slate-800 bg-slate-900">
              Agent Console
            </span>
          </div>
          <span className="text-xs text-slate-500">Pairs with Ollama phi3</span>
        </div>
        <ChatConsole />
      </div>
    </main>
  );
}