import Link from "next/link";
import { Utensils, QrCode, Sliders, ShieldCheck, Layers, Sparkles } from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 selection:bg-amber-500 selection:text-slate-950">
      {/* Header */}
      <header className="border-b border-slate-800/80 px-6 py-4 flex items-center justify-between max-w-7xl mx-auto">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-amber-500 flex items-center justify-center text-slate-950 font-black text-xl shadow-lg shadow-amber-500/20">
            M
          </div>
          <div>
            <span className="font-bold text-lg tracking-tight">ModularMenu</span>
            <span className="ml-2 text-xs px-2 py-0.5 rounded-full bg-slate-800 text-amber-400 font-mono border border-slate-700">v1.0.0</span>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <Link
            href="/platform"
            className="text-sm font-medium text-slate-400 hover:text-white transition-colors"
          >
            Platform Admin
          </Link>
          <Link
            href="/app"
            className="text-sm font-semibold bg-amber-500 hover:bg-amber-400 text-slate-950 px-4 py-2 rounded-lg transition-all shadow-md shadow-amber-500/10"
          >
            Launch Builder
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <main className="max-w-5xl mx-auto px-6 py-20 text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-amber-500/10 border border-amber-500/20 text-amber-400 text-xs font-semibold uppercase tracking-wider mb-8">
          <Sparkles className="w-3.5 h-3.5" /> India-First · Web-First · Multi-Tenant Architecture
        </div>
        <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white mb-6 leading-tight">
          One Codebase. <br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-400 via-orange-400 to-amber-200">
            Endless Branded Restaurant Menus.
          </span>
        </h1>
        <p className="text-lg sm:text-xl text-slate-400 max-w-2xl mx-auto mb-12">
          ModularMenu is a multi-tenant digital restaurant menu platform with token-driven design presets, 
          a live 3-panel visual studio, and instantaneous QR self-browsing.
        </p>

        {/* The Three Frontend Portals */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-left max-w-4xl mx-auto mb-20">
          {/* Portal A: Platform Admin */}
          <Link
            href="/platform"
            className="group p-6 rounded-2xl bg-slate-900 border border-slate-800 hover:border-amber-500/40 hover:bg-slate-900/80 transition-all flex flex-col justify-between"
          >
            <div>
              <div className="h-12 w-12 rounded-xl bg-blue-500/10 text-blue-400 border border-blue-500/20 flex items-center justify-center mb-4 group-hover:scale-105 transition-transform">
                <Layers className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-white mb-2">Platform Administration</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                Super-admin cockpit to onboard restaurants, monitor tenant quotas, inspect subscriptions, and manage platform theme presets.
              </p>
            </div>
            <div className="mt-6 flex items-center text-xs font-semibold text-blue-400 group-hover:translate-x-1 transition-transform">
              Open Admin Panel →
            </div>
          </Link>

          {/* Portal B: Restaurant Dashboard & Visual Builder */}
          <Link
            href="/app"
            className="group p-6 rounded-2xl bg-slate-900 border border-amber-500/30 hover:border-amber-500 hover:bg-slate-900/80 transition-all flex flex-col justify-between shadow-lg shadow-amber-500/5 ring-1 ring-amber-500/20"
          >
            <div>
              <div className="h-12 w-12 rounded-xl bg-amber-500/10 text-amber-400 border border-amber-500/20 flex items-center justify-center mb-4 group-hover:scale-105 transition-transform">
                <Sliders className="w-6 h-6" />
              </div>
              <div className="flex items-center gap-2 mb-2">
                <h3 className="text-lg font-bold text-white">Visual Menu Studio</h3>
                <span className="text-[10px] bg-amber-500/20 text-amber-300 px-2 py-0.5 rounded font-mono font-bold">CORE</span>
              </div>
              <p className="text-sm text-slate-400 leading-relaxed">
                3-panel interactive canvas: catalog management, instant dietary badges, live mobile viewport preview, and one-click publishing.
              </p>
            </div>
            <div className="mt-6 flex items-center text-xs font-semibold text-amber-400 group-hover:translate-x-1 transition-transform">
              Open Studio & Builder →
            </div>
          </Link>

          {/* Portal C: Customer QR Menu */}
          <Link
            href="/r/the-bombay-canteen"
            className="group p-6 rounded-2xl bg-slate-900 border border-slate-800 hover:border-emerald-500/40 hover:bg-slate-900/80 transition-all flex flex-col justify-between"
          >
            <div>
              <div className="h-12 w-12 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center justify-center mb-4 group-hover:scale-105 transition-transform">
                <QrCode className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-white mb-2">Public QR Experience</h3>
              <p className="text-sm text-slate-400 leading-relaxed">
                Sub-second LCP mobile-first dining menu. Zero-login friction, FSSAI-compliant dietary filter pills, and allergen alerts.
              </p>
            </div>
            <div className="mt-6 flex items-center text-xs font-semibold text-emerald-400 group-hover:translate-x-1 transition-transform">
              Experience Customer View →
            </div>
          </Link>
        </div>

        {/* Feature Highlights Grid */}
        <div className="border-t border-slate-800/80 pt-16">
          <h2 className="text-2xl font-bold text-slate-200 mb-8">Architectural Standards Built-In</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800">
              <div className="text-amber-400 font-bold text-xl mb-1">6 Themes</div>
              <div className="text-xs text-slate-400">Luxury, Minimal, Rustic, Vibrant, Contemporary, Editorial</div>
            </div>
            <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800">
              <div className="text-emerald-400 font-bold text-xl mb-1">&lt; 1.5s LCP</div>
              <div className="text-xs text-slate-400">Pre-compiled immutable snapshots on Edge</div>
            </div>
            <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800">
              <div className="text-blue-400 font-bold text-xl mb-1">RLS Protected</div>
              <div className="text-xs text-slate-400">Cryptographic multi-tenant data isolation</div>
            </div>
            <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800">
              <div className="text-purple-400 font-bold text-xl mb-1">Hybrid Ready</div>
              <div className="text-xs text-slate-400">Cloud SaaS + Customer-Hosted Docker Profile</div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
