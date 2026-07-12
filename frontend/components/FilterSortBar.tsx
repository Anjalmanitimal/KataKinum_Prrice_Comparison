"use client";

import type { FilterState, SortOption } from "@/lib/filterProducts";

const STORES = ["Daraz", "Hukut", "Oliz"];

export default function FilterSortBar({
  filters,
  onChange,
  resultCount,
}: {
  filters: FilterState;
  onChange: (filters: FilterState) => void;
  resultCount: number;
}) {
  return (
    <div className="mb-6 flex flex-wrap items-center gap-3 rounded-2xl border border-surface-border bg-surface p-4">
      <select
        value={filters.sort}
        onChange={(e) =>
          onChange({ ...filters, sort: e.target.value as SortOption })
        }
        className="rounded-xl border border-surface-border bg-background px-3 py-2 text-sm font-medium text-ink-900 focus:outline-none focus:ring-2 focus:ring-brand-400"
      >
        <option value="relevance">Sort: Relevance</option>
        <option value="price_asc">Price: Low to High</option>
        <option value="price_desc">Price: High to Low</option>
      </select>

      <select
        value={filters.store}
        onChange={(e) => onChange({ ...filters, store: e.target.value })}
        className="rounded-xl border border-surface-border bg-background px-3 py-2 text-sm font-medium text-ink-900 focus:outline-none focus:ring-2 focus:ring-brand-400"
      >
        <option value="all">All Stores</option>
        {STORES.map((store) => (
          <option key={store} value={store}>
            {store}
          </option>
        ))}
      </select>

      <div className="flex items-center gap-2">
        <input
          type="number"
          inputMode="numeric"
          placeholder="Min Rs"
          value={filters.minPrice}
          onChange={(e) => onChange({ ...filters, minPrice: e.target.value })}
          className="w-24 rounded-xl border border-surface-border bg-background px-3 py-2 text-sm text-ink-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-400"
        />
        <span className="text-slate-300">–</span>
        <input
          type="number"
          inputMode="numeric"
          placeholder="Max Rs"
          value={filters.maxPrice}
          onChange={(e) => onChange({ ...filters, maxPrice: e.target.value })}
          className="w-24 rounded-xl border border-surface-border bg-background px-3 py-2 text-sm text-ink-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-400"
        />
      </div>

      <span className="ml-auto text-sm font-medium text-slate-500">
        {resultCount} result{resultCount === 1 ? "" : "s"}
      </span>
    </div>
  );
}
