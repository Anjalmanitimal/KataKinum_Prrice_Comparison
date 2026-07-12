"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

import Navbar from "@/components/Navbar";
import { getDeals } from "@/lib/api";
import type { Deal } from "@/types/product";

const STORE_STYLES: Record<string, string> = {
  Daraz: "bg-orange-50 text-orange-700 ring-orange-200",
  Hukut: "bg-sky-50 text-sky-700 ring-sky-200",
  Oliz: "bg-violet-50 text-violet-700 ring-violet-200",
};

function storeStyle(marketplace: string) {
  return STORE_STYLES[marketplace] ?? "bg-slate-100 text-slate-700 ring-slate-200";
}

export default function DealsPage() {
  const [deals, setDeals] = useState<Deal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const data = await getDeals();
        setDeals(data);
      } catch {
        setError("Couldn't load deals. Make sure the backend is running.");
      } finally {
        setLoading(false);
      }
    }

    load();
  }, []);

  return (
    <main className="min-h-screen bg-background">
      <Navbar />

      <div className="mx-auto max-w-7xl px-6 py-16">
        <span className="inline-flex items-center gap-2 rounded-full border border-brand-100 bg-brand-50 px-4 py-1.5 text-xs font-semibold uppercase tracking-wider text-brand-700">
          <span className="h-1.5 w-1.5 animate-pulse-slow rounded-full bg-accent" />
          Updated from live tracked prices
        </span>

        <h1 className="mt-4 text-4xl font-bold text-ink-900">Best Deals</h1>
        <p className="mt-2 text-slate-500">
          The biggest verified price gaps between stores for the same product —
          same product, different price.
        </p>

        {loading && (
          <div className="mt-16 flex flex-col items-center gap-3 text-center text-slate-500">
            <span className="h-10 w-10 animate-spin rounded-full border-4 border-brand-100 border-t-brand-600" />
            <p className="font-medium">Loading deals...</p>
          </div>
        )}

        {!loading && error && (
          <div className="mt-16 rounded-2xl border border-red-200 bg-red-50 p-6 text-center text-red-700">
            {error}
          </div>
        )}

        {!loading && !error && deals.length === 0 && (
          <div className="mt-16 rounded-2xl border border-surface-border bg-surface p-10 text-center text-slate-500">
            No verified deals right now. Check back once more products are tracked across stores.
          </div>
        )}

        {!loading && !error && deals.length > 0 && (
          <div className="mt-10 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {deals.map((deal) => (
              <Link
                key={deal.product_id}
                href={`/product/${deal.product_id}`}
                className={`group flex flex-col rounded-2xl border bg-surface p-6 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-xl hover:shadow-brand-500/10 ${
                  deal.price_trend === "falling"
                    ? "border-accent/40 ring-1 ring-accent/20"
                    : "border-surface-border"
                }`}
              >
                {deal.price_trend === "falling" && (
                  <span className="mb-3 inline-flex w-fit items-center gap-1.5 rounded-full bg-accent/10 px-3 py-1 text-xs font-bold text-accent-strong">
                    🔥 Price dropping
                  </span>
                )}

                <div className="flex items-start justify-between gap-3">
                  <h2 className="line-clamp-2 text-base font-semibold leading-6 text-ink-900">
                    {deal.product_name}
                  </h2>

                  <span className="shrink-0 rounded-full bg-accent/10 px-2.5 py-1 text-xs font-bold text-accent-strong">
                    -{deal.savings_percent}%
                  </span>
                </div>

                <p className="mt-4 text-3xl font-extrabold tracking-tight text-accent-strong">
                  Save Rs {deal.savings.toLocaleString()}
                </p>

                <div className="mt-4 flex items-center gap-2 text-sm">
                  <span
                    className={`rounded-lg px-2.5 py-1 font-semibold ring-1 ring-inset ${storeStyle(deal.best_store)}`}
                  >
                    {deal.best_store} {deal.best_price_display}
                  </span>
                  <span className="text-slate-300">vs</span>
                  <span
                    className={`rounded-lg px-2.5 py-1 font-semibold ring-1 ring-inset ${storeStyle(deal.highest_store)}`}
                  >
                    {deal.highest_store} {deal.highest_price_display}
                  </span>
                </div>

                <p className="mt-auto pt-6 text-sm font-semibold text-brand-600 group-hover:text-brand-700">
                  Compare all {deal.store_count} stores →
                </p>
              </Link>
            ))}
          </div>
        )}
      </div>
    </main>
  );
}
