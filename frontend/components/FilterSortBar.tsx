"use client";

import type { FilterState, SortOption } from "@/lib/filterProducts";

const STORES = ["Daraz", "Hukut", "Oliz"];

export default function FilterSortBar({
  filters,
  onChange,
  resultCount,
  availableTypes = [],
}: {
  filters: FilterState;
  onChange: (filters: FilterState) => void;
  resultCount: number;
  availableTypes?: string[];
}) {
  function toggleType(type: string) {
    const isExcluded = filters.excludedTypes.includes(type);
    onChange({
      ...filters,
      excludedTypes: isExcluded
        ? filters.excludedTypes.filter((t) => t !== type)
        : [...filters.excludedTypes, type],
    });
  }

  return (
    <div className="mb-6 flex flex-col gap-3 rounded-2xl border border-surface-border bg-surface p-4">
      <div className="flex flex-wrap items-center gap-3">
        <input
          type="text"
          placeholder="Search these results..."
          value={filters.search}
          onChange={(e) => onChange({ ...filters, search: e.target.value })}
          className="min-w-[180px] flex-1 rounded-xl border border-surface-border bg-background px-3 py-2 text-sm text-ink-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-400"
        />

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

      {availableTypes.length > 1 && (
        <div className="flex flex-wrap items-center gap-2 border-t border-surface-border pt-3">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
            Show:
          </span>
          {availableTypes.map((type) => {
            const isActive = !filters.excludedTypes.includes(type);

            return (
              <button
                key={type}
                type="button"
                onClick={() => toggleType(type)}
                className={`rounded-full px-3 py-1 text-xs font-semibold ring-1 ring-inset transition ${
                  isActive
                    ? "bg-brand-50 text-brand-700 ring-brand-200"
                    : "bg-slate-100 text-slate-400 ring-slate-200"
                }`}
              >
                {type}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
