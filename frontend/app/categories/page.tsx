"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

import Navbar from "@/components/Navbar";
import { getCategories } from "@/lib/api";
import type { Category } from "@/types/product";

const CATEGORY_ICONS: Record<string, string> = {
  smartphone: "📱",
  laptop: "💻",
  tablet: "📟",
  smartwatch: "⌚",
  earphone: "🎧",
};

export default function CategoriesPage() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const data = await getCategories();
        setCategories(data);
      } catch {
        setError("Couldn't load categories. Make sure the backend is running.");
      } finally {
        setLoading(false);
      }
    }

    load();
  }, []);

  const totalProducts = categories.reduce((sum, c) => sum + c.count, 0);

  return (
    <main className="min-h-screen bg-background">
      <Navbar />

      <div className="mx-auto max-w-7xl px-6 py-16">
        <h1 className="text-4xl font-bold text-ink-900">Browse Categories</h1>
        <p className="mt-2 text-slate-500">
          Every category we track across Daraz, Hukut and Oliz combined
          {totalProducts > 0 && ` — ${totalProducts} products total.`}
        </p>

        {loading && (
          <div className="mt-16 flex flex-col items-center gap-3 text-center text-slate-500">
            <span className="h-10 w-10 animate-spin rounded-full border-4 border-brand-100 border-t-brand-600" />
            <p className="font-medium">Loading categories...</p>
          </div>
        )}

        {!loading && error && (
          <div className="mt-16 rounded-2xl border border-red-200 bg-red-50 p-6 text-center text-red-700">
            {error}
          </div>
        )}

        {!loading && !error && (
          <div className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {categories.map((c) => (
              <Link
                key={c.category}
                href={`/categories/${c.category}`}
                className="group flex items-center gap-5 rounded-2xl border border-surface-border bg-surface p-6 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-xl hover:shadow-brand-500/10"
              >
                <span className="flex h-14 w-14 shrink-0 items-center justify-center rounded-xl bg-brand-50 text-3xl">
                  {CATEGORY_ICONS[c.category] ?? "🛒"}
                </span>

                <div>
                  <h2 className="text-lg font-semibold text-ink-900">
                    {c.label}
                  </h2>
                  <p className="mt-1 text-sm text-slate-500">
                    {c.count} product{c.count === 1 ? "" : "s"} across 3 stores
                  </p>
                </div>

                <span className="ml-auto text-slate-300 transition group-hover:translate-x-1 group-hover:text-brand-500">
                  →
                </span>
              </Link>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}
