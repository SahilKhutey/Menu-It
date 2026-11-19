"use client";

import React, { useState } from "react";
import Link from "next/link";
import {
  Layers,
  Building2,
  TrendingUp,
  ShieldCheck,
  Server,
  Plus,
  Search,
  ExternalLink,
  ChevronRight,
  Sliders,
  CheckCircle2,
} from "lucide-react";

interface TenantRecord {
  id: string;
  name: string;
  org: string;
  slug: string;
  deployment: "Managed SaaS" | "Customer-Hosted";
  status: "Active" | "Trial" | "Suspended";
  menusCount: number;
  itemsCount: number;
  activeTheme: string;
  dailyScans: number;
}

const INITIAL_TENANTS: TenantRecord[] = [
  {
    id: "rest-1",
    name: "The Bombay Canteen",
    org: "Hunger Inc Hospitality",
    slug: "the-bombay-canteen",
    deployment: "Managed SaaS",
    status: "Active",
    menusCount: 3,
    itemsCount: 48,
    activeTheme: "Luxury",
    dailyScans: 420,
  },
  {
    id: "rest-2",
    name: "Subko Specialty Coffee & Bakehouse",
    org: "Subko India",
    slug: "subko-coffee",
    deployment: "Managed SaaS",
    status: "Active",
    menusCount: 2,
    itemsCount: 34,
    activeTheme: "Minimal",
    dailyScans: 680,
  },
  {
    id: "rest-3",
    name: "O Pedro Goa",
    org: "Hunger Inc Hospitality",
    slug: "o-pedro",
    deployment: "Managed SaaS",
    status: "Active",
    menusCount: 2,
    itemsCount: 40,
    activeTheme: "Vibrant",
    dailyScans: 310,
  },
  {
    id: "rest-4",
    name: "Charcoal Steakhouse & Grill",
    org: "Charcoal Hospitality Ltd",
    slug: "charcoal-steakhouse",
    deployment: "Customer-Hosted",
    status: "Active",
    menusCount: 1,
    itemsCount: 52,
    activeTheme: "Rustic",
    dailyScans: 280,
  },
];

export default function PlatformAdminPage() {
  const [tenants, setTenants] = useState<TenantRecord[]>(INITIAL_TENANTS);
  const [search, setSearch] = useState("");
  const [showOnboardModal, setShowOnboardModal] = useState(false);
  const [newRestName, setNewRestName] = useState("");
  const [newOrgName, setNewOrgName] = useState("");
  const [newDeployment, setNewDeployment] = useState<"Managed SaaS" | "Customer-Hosted">("Managed SaaS");

  const filteredTenants = tenants.filter(
    (t) =>
      t.name.toLowerCase().includes(search.toLowerCase()) ||
      t.org.toLowerCase().includes(search.toLowerCase()) ||
      t.slug.toLowerCase().includes(search.toLowerCase())
  );

  const handleAddRestaurant = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newRestName.trim()) return;

    const slug = newRestName.toLowerCase().replace(/[^a-z0-9]+/g, "-");
    const newTenant: TenantRecord = {
      id: `rest-${tenants.length + 1}`,
      name: newRestName,
      org: newOrgName || "Independent",
      slug,
      deployment: newDeployment,
      status: "Active",
      menusCount: 1,
      itemsCount: 0,
      activeTheme: "Contemporary",
      dailyScans: 0,
    };

    setTenants([newTenant, ...tenants]);
    setNewRestName("");
    setNewOrgName("");
    setShowOnboardModal(false);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans">
      {/* Top Bar */}
      <header className="h-16 border-b border-slate-800 bg-slate-900/80 px-6 flex items-center justify-between sticky top-0 z-20 backdrop-blur-md">
        <div className="flex items-center gap-3">
          <Link href="/" className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-amber-500 text-slate-950 flex items-center justify-center font-black text-base">
              M
            </div>
            <span className="font-bold text-base text-white tracking-tight">ModularMenu Platform</span>
          </Link>
          <span className="text-xs px-2.5 py-0.5 rounded-full bg-blue-500/10 text-blue-400 font-mono border border-blue-500/20">
            Platform Operator
          </span>
        </div>

        <div className="flex items-center gap-3">
          <Link
            href="/app"
            className="text-xs font-semibold text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 px-3 py-1.5 rounded-lg border border-slate-700 transition-colors"
          >
            Launch Restaurant Studio →
          </Link>
          <button
            onClick={() => setShowOnboardModal(true)}
            className="flex items-center gap-1.5 text-xs font-bold bg-amber-500 hover:bg-amber-400 text-slate-950 px-3.5 py-1.5 rounded-lg transition-all shadow-md shadow-amber-500/10"
          >
            <Plus className="w-3.5 h-3.5" /> Onboard Restaurant
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {/* KPI Metric Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800">
            <div className="flex items-center justify-between text-slate-400 text-xs font-medium mb-2">
              <span>Total Onboarded Restaurants</span>
              <Building2 className="w-4 h-4 text-amber-500" />
            </div>
            <div className="text-2xl font-extrabold text-white font-mono">{tenants.length}</div>
            <div className="text-[11px] text-emerald-400 mt-1 flex items-center gap-1">
              <span>+2 this month</span>
            </div>
          </div>

          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800">
            <div className="flex items-center justify-between text-slate-400 text-xs font-medium mb-2">
              <span>Daily QR Scan Impressions</span>
              <TrendingUp className="w-4 h-4 text-emerald-500" />
            </div>
            <div className="text-2xl font-extrabold text-white font-mono">1,690</div>
            <div className="text-[11px] text-slate-400 mt-1">
              <span>Across all dining rooms</span>
            </div>
          </div>

          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800">
            <div className="flex items-center justify-between text-slate-400 text-xs font-medium mb-2">
              <span>Deployment Distribution</span>
              <Server className="w-4 h-4 text-blue-500" />
            </div>
            <div className="text-sm font-bold text-white mt-1">
              3 Managed SaaS <span className="text-slate-500">/</span> 1 Self-Hosted
            </div>
            <div className="text-[11px] text-blue-400 mt-1">
              <span>Hybrid profile active</span>
            </div>
          </div>

          <div className="p-5 rounded-2xl bg-slate-900 border border-slate-800">
            <div className="flex items-center justify-between text-slate-400 text-xs font-medium mb-2">
              <span>System Health & Isolation</span>
              <ShieldCheck className="w-4 h-4 text-purple-500" />
            </div>
            <div className="text-sm font-bold text-emerald-400 mt-1 flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4" /> RLS Enforcement 100%
            </div>
            <div className="text-[11px] text-slate-400 mt-1">
              <span>Zero cross-tenant leaks</span>
            </div>
          </div>
        </div>

        {/* Tenant Table Section */}
        <div className="rounded-2xl border border-slate-800 bg-slate-900/60 overflow-hidden shadow-xl">
          <div className="p-4 border-b border-slate-800 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              <h2 className="text-sm font-bold text-white uppercase tracking-wider">Restaurant Tenants</h2>
              <span className="text-xs font-mono text-slate-500">({filteredTenants.length} total)</span>
            </div>

            <div className="relative w-full sm:w-72">
              <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                placeholder="Search tenant or organization..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full bg-slate-950 text-xs text-slate-200 pl-9 pr-3 py-1.5 rounded-lg border border-slate-800 focus:outline-none focus:border-amber-500"
              />
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950 text-slate-400 border-b border-slate-800 font-mono uppercase text-[10px]">
                <tr>
                  <th className="py-3 px-4">Restaurant & Organization</th>
                  <th className="py-3 px-4">Deployment Profile</th>
                  <th className="py-3 px-4">Catalog Scope</th>
                  <th className="py-3 px-4">Active Theme</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/80">
                {filteredTenants.map((tenant) => (
                  <tr key={tenant.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="py-3.5 px-4">
                      <div className="font-bold text-white text-sm">{tenant.name}</div>
                      <div className="text-[11px] text-slate-400 flex items-center gap-1.5 mt-0.5">
                        <span>{tenant.org}</span>
                        <span className="text-slate-600">·</span>
                        <code className="text-slate-500 text-[10px]">/r/{tenant.slug}</code>
                      </div>
                    </td>
                    <td className="py-3.5 px-4">
                      <span
                        className={`text-[11px] px-2.5 py-0.5 rounded-full font-mono font-medium ${
                          tenant.deployment === "Managed SaaS"
                            ? "bg-blue-500/10 text-blue-400 border border-blue-500/20"
                            : "bg-purple-500/10 text-purple-400 border border-purple-500/20"
                        }`}
                      >
                        {tenant.deployment}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 font-mono text-slate-300">
                      {tenant.menusCount} Menus · {tenant.itemsCount} Items
                    </td>
                    <td className="py-3.5 px-4 font-medium text-amber-400 font-mono">
                      {tenant.activeTheme}
                    </td>
                    <td className="py-3.5 px-4">
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        {tenant.status}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <Link
                          href={`/r/${tenant.slug}`}
                          target="_blank"
                          className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors"
                          title="Open Customer QR Menu"
                        >
                          <ExternalLink className="w-3.5 h-3.5" />
                        </Link>
                        <Link
                          href="/app"
                          className="p-1.5 rounded-lg bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 border border-amber-500/30 transition-colors"
                          title="Launch Visual Studio"
                        >
                          <Sliders className="w-3.5 h-3.5" />
                        </Link>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </main>

      {/* Onboard Restaurant Modal */}
      {showOnboardModal && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl">
            <h3 className="text-base font-bold text-white mb-1">Onboard New Restaurant</h3>
            <p className="text-xs text-slate-400 mb-4">
              Create a tenant profile with organization grouping and deployment configuration.
            </p>

            <form onSubmit={handleAddRestaurant} className="space-y-4 text-xs">
              <div>
                <label className="block font-medium text-slate-300 mb-1">Restaurant Name *</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Bastian Mumbai"
                  value={newRestName}
                  onChange={(e) => setNewRestName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:border-amber-500"
                />
              </div>

              <div>
                <label className="block font-medium text-slate-300 mb-1">Organization / Group</label>
                <input
                  type="text"
                  placeholder="e.g. Bastian Hospitality"
                  value={newOrgName}
                  onChange={(e) => setNewOrgName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:border-amber-500"
                />
              </div>

              <div>
                <label className="block font-medium text-slate-300 mb-1">Deployment Profile</label>
                <select
                  value={newDeployment}
                  onChange={(e) => setNewDeployment(e.target.value as any)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:border-amber-500"
                >
                  <option value="Managed SaaS">Profile A: Managed SaaS (Shared Cloud)</option>
                  <option value="Customer-Hosted">Profile B: Customer-Hosted (Dedicated Docker)</option>
                </select>
              </div>

              <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowOnboardModal(false)}
                  className="px-3 py-1.5 rounded-lg bg-slate-800 text-slate-300 hover:text-white transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-1.5 rounded-lg bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold transition-colors"
                >
                  Confirm & Provision
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
