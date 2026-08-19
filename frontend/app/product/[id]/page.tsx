"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { getProduct, getPriceTrend } from "@/lib/api";
import PriceSparkline from "@/components/PriceSparkline";
import { formatPriceDate } from "@/lib/formatDate";
import type { PriceTrend } from "@/types/product";

type Listing = {
  product_id: string;
  product_name: string;
  marketplace: string;
  price: string;
  price_numeric: number | null;
  link: string;
  scraped_at: string | null;
};

const STORE_STYLES: Record<string, string> = {
  Daraz: "bg-orange-50 text-orange-700 ring-orange-200",
  Hukut: "bg-sky-50 text-sky-700 ring-sky-200",
  Oliz: "bg-violet-50 text-violet-700 ring-violet-200",
};

function storeStyle(marketplace: string) {
  return STORE_STYLES[marketplace] ?? "bg-slate-100 text-slate-700 ring-slate-200";
}

export default function ProductPage() {
  const params = useParams();

  const [products, setProducts] = useState<Listing[]>([]);
  const [trend, setTrend] = useState<PriceTrend | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      setError(null);

      try {
        const data: Listing[] = await getProduct(params.id as string);

        const sorted = [...data].sort((a, b) => {
          if (a.price_numeric == null) return 1;
          if (b.price_numeric == null) return -1;
          return a.price_numeric - b.price_numeric;
        });

        setProducts(sorted);
      } catch {
        setError("Couldn't load this comparison. The backend may be offline.");
      } finally {
        setLoading(false);
      }
    }

    loadData();

    getPriceTrend(params.id as string)
      .then(setTrend)
      .catch(() => setTrend(null));
  }, [params.id]);

  if (loading) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-3 bg-background text-slate-500">
        <span className="h-10 w-10 animate-spin rounded-full border-4 border-brand-100 border-t-brand-600" />
        <p className="font-medium">Loading comparison...</p>
      </div>
    );
  }

  if (error || products.length === 0) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center gap-4 bg-background px-6 text-center text-slate-500">
        <p>{error ?? "No listings found for this product."}</p>
        <Link
          href="/"
          className="rounded-xl bg-ink-900 px-5 py-2.5 font-semibold text-white transition hover:bg-brand-600"
        >
          ← Back to search
        </Link>
      </div>
    );
  }

  const cheapest = products[0];

  const validOffers = products.filter((p) => p.price_numeric != null);
  const priciest = validOffers[validOffers.length - 1];
  const hasSpread =
    validOffers.length >= 2 &&
    priciest.price_numeric! > cheapest.price_numeric!;
  const savings = hasSpread
    ? priciest.price_numeric! - cheapest.price_numeric!
    : 0;
  const savingsPercent = hasSpread
    ? Math.round((savings / priciest.price_numeric!) * 100)
    : 0;

  const progressDots = trend?.status === "insufficient_data"
    ? Array.from({ length: 3 }, (_, i) => i < trend.points.length)
    : [];

  return (
    <main className="min-h-screen bg-background px-6 py-10 text-ink-900">

      <div className="mx-auto max-w-6xl">

        <Link
          href="/"
          className="mb-6 inline-flex items-center gap-1 text-sm font-medium text-slate-500 transition hover:text-brand-600"
        >
          ← Back to search
        </Link>

        <h1 className="mb-8 text-4xl font-bold text-ink-900">
          {cheapest.product_name}
        </h1>

        <div className="mb-8 rounded-2xl border border-emerald-200 bg-emerald-50 p-8 shadow-sm">

          <p className="text-sm font-semibold uppercase tracking-wider text-accent-strong">
            Best Price · {products.length} store{products.length === 1 ? "" : "s"} compared
          </p>

          <h2 className="mt-2 text-5xl font-extrabold text-accent-strong">
            {cheapest.price}
          </h2>

          <span
            className={`mt-3 inline-flex items-center rounded-lg px-3 py-1 text-sm font-semibold ring-1 ring-inset ${storeStyle(cheapest.marketplace)}`}
          >
            {cheapest.marketplace}
          </span>

        </div>

        {(trend || hasSpread) && (
          <div className="mb-8 grid gap-6 sm:grid-cols-2">

            {trend && (
              <div className="rounded-2xl border border-surface-border bg-surface p-8 shadow-sm">

                <p className="text-sm font-semibold uppercase tracking-wider text-slate-500">
                  Price Trend
                </p>

                {trend.status === "insufficient_data" ? (
                  <div className="mt-4">
                    {trend.current != null && (
                      <p className="text-3xl font-extrabold text-ink-900">
                        Rs {trend.current.toLocaleString()}
                      </p>
                    )}

                    <div className="mt-4 flex items-center gap-2">
                      {progressDots.map((filled, i) => (
                        <span
                          key={i}
                          className={`h-2.5 w-2.5 rounded-full ${
                            filled ? "bg-brand-500" : "bg-slate-200"
                          }`}
                        />
                      ))}
                      <span className="ml-1 text-sm font-medium text-slate-500">
                        {trend.points.length}/3 check-ins tracked
                      </span>
                    </div>

                    <p className="mt-3 text-sm text-slate-500">
                      {trend.first_tracked
                        ? `First tracked ${trend.first_tracked}. `
                        : ""}
                      {trend.points_needed} more visit
                      {trend.points_needed !== 1 ? "s" : ""} on a different
                      day will unlock a trend line.
                    </p>
                  </div>
                ) : (
                  <div className="mt-4 flex flex-col items-start gap-6 sm:flex-row sm:items-center">
                    <PriceSparkline
                      points={trend.points}
                      color={
                        trend.trend === "falling"
                          ? "#059669"
                          : trend.trend === "rising"
                          ? "#dc2626"
                          : "#64748b"
                      }
                    />

                    <div>
                      <span
                        className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-sm font-semibold ${
                          trend.trend === "falling"
                            ? "bg-emerald-50 text-emerald-700"
                            : trend.trend === "rising"
                            ? "bg-red-50 text-red-700"
                            : "bg-slate-100 text-slate-700"
                        }`}
                      >
                        {trend.trend === "falling" && "↓ Falling"}
                        {trend.trend === "rising" && "↑ Rising"}
                        {trend.trend === "stable" && "→ Stable"}
                      </span>
                      <p className="mt-2 text-slate-600">{trend.recommendation}</p>
                      <p className="mt-1 text-sm text-slate-400">
                        Based on {trend.points.length} recorded price points
                      </p>
                    </div>
                  </div>
                )}

              </div>
            )}

            {hasSpread && (
              <div className="rounded-2xl border border-surface-border bg-surface p-8 shadow-sm">

                <p className="text-sm font-semibold uppercase tracking-wider text-slate-500">
                  Store Price Spread
                </p>

                <p className="mt-4 text-3xl font-extrabold text-accent-strong">
                  Save up to Rs {savings.toLocaleString()}
                </p>

                <p className="mt-1 text-sm font-medium text-slate-500">
                  {savingsPercent}% cheaper at {cheapest.marketplace} vs {priciest.marketplace}
                </p>

                <div className="mt-4 flex items-center gap-3">
                  <span
                    className={`rounded-lg px-2.5 py-1 text-sm font-semibold ring-1 ring-inset ${storeStyle(cheapest.marketplace)}`}
                  >
                    {cheapest.marketplace} · {cheapest.price}
                  </span>
                  <span className="text-slate-300">→</span>
                  <span
                    className={`rounded-lg px-2.5 py-1 text-sm font-semibold ring-1 ring-inset ${storeStyle(priciest.marketplace)}`}
                  >
                    {priciest.marketplace} · {priciest.price}
                  </span>
                </div>

                <p className="mt-4 text-sm text-slate-400">
                  Across {validOffers.length} stores tracking this product
                </p>

              </div>
            )}

          </div>
        )}

        <div className="overflow-hidden rounded-2xl border border-surface-border bg-surface shadow-md">

          <table className="w-full">

            <thead className="bg-ink-900 text-white">

              <tr>
                <th className="px-6 py-4 text-left">Store</th>
                <th className="px-6 py-4 text-left">Price</th>
                <th className="px-6 py-4 text-left">Price Date</th>
                <th className="px-6 py-4 text-left">Visit</th>
              </tr>

            </thead>

            <tbody>

              {products.map((item, index) => (
                <tr
                  key={`${item.product_id}-${item.marketplace}-${index}`}
                  className="border-t border-surface-border transition hover:bg-brand-50/40"
                >
                  <td className="px-6 py-4">
                    <span
                      className={`inline-flex items-center rounded-lg px-2.5 py-1 text-sm font-semibold ring-1 ring-inset ${storeStyle(item.marketplace)}`}
                    >
                      {item.marketplace}
                    </span>
                  </td>

                  <td className="px-6 py-4 text-lg font-bold text-ink-900">
                    {item.price}
                    {index === 0 && (
                      <span className="ml-2 rounded-full bg-accent/10 px-2 py-0.5 text-xs font-semibold text-accent-strong">
                        Best
                      </span>
                    )}
                  </td>

                  <td className="px-6 py-4 text-sm text-slate-500">
                    {formatPriceDate(item.scraped_at)}
                  </td>

                  <td className="px-6 py-4">
                    <a
                      href={item.link}
                      target="_blank"
                      rel="noreferrer"
                      className="rounded-lg bg-ink-900 px-4 py-2 text-white transition hover:bg-brand-600"
                    >
                      Visit Store
                    </a>
                  </td>
                </tr>
              ))}

            </tbody>

          </table>

        </div>

      </div>

    </main>
  );
}
