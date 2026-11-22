"use client";

import React, { useEffect, useState } from "react";
import type { MenuRenderInput } from "@modularmenu/contracts";
import { PublicMenuRenderer } from "@/features/public-menu";

interface PreviewPageProps {
  params: {
    menuId: string;
  };
}

export default function MenuPreviewPage({ params }: PreviewPageProps) {
  const { menuId } = params;
  const [data, setData] = useState<MenuRenderInput | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchPreview() {
      try {
        setLoading(true);
        const res = await fetch(`/api/v1/menus/${menuId}/preview`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
        });

        if (!res.ok) {
          throw new Error(`Failed to load preview: HTTP ${res.status}`);
        }

        const previewData = await res.json();
        // Construct canonical MenuRenderInput from preview response
        setData(previewData.render_input || previewData);
      } catch (err: any) {
        setError(err.message || "Preview error");
      } finally {
        setLoading(false);
      }
    }

    if (menuId) {
      fetchPreview();
    }
  }, [menuId]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-zinc-50">
        <div className="flex flex-col items-center gap-2">
          <div className="w-8 h-8 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" />
          <p className="text-xs text-zinc-500 font-medium">Generating preview...</p>
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-zinc-50 p-4">
        <div className="max-w-md p-6 bg-white rounded-xl shadow-sm border border-zinc-200 text-center">
          <p className="text-rose-600 font-semibold mb-1">Preview Unavailable</p>
          <p className="text-xs text-zinc-500">{error || "Could not generate menu preview."}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="relative">
      <div className="sticky top-0 z-40 bg-amber-500 text-zinc-950 text-xs font-bold px-4 py-1.5 flex items-center justify-between shadow-sm">
        <span>Draft Preview Mode (Private · Unpublished changes)</span>
        <span className="text-[10px] bg-black/10 px-2 py-0.5 rounded">Not visible to public diners</span>
      </div>
      <PublicMenuRenderer input={data} />
    </div>
  );
}
