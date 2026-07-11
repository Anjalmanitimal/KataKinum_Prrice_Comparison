"use client";

import { useState } from "react";

export default function SearchBar({
  onSearch,
  onStop,
  loading = false,
}: {
  onSearch: (query: string) => void;
  onStop?: () => void;
  loading?: boolean;
}) {
  const [query, setQuery] = useState("");

  function submit() {
    const trimmed = query.trim();
    if (!trimmed || loading) return;
    onSearch(trimmed);
  }

  return (
    <div>
      <form
        className="group relative flex flex-col gap-3 rounded-2xl bg-gradient-to-r from-brand-400 via-accent to-brand-400 p-[2px] shadow-2xl shadow-brand-900/40 sm:flex-row sm:gap-0"
        onSubmit={(e) => {
          e.preventDefault();
          submit();
        }}
      >
        <div className="flex w-full flex-col gap-2 rounded-[calc(1rem-2px)] bg-surface p-2 sm:flex-row sm:gap-2">
          <div className="flex flex-1 items-center gap-3 px-4">
            <svg
              className="h-6 w-6 shrink-0 text-slate-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M21 21l-4.35-4.35M17 10a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
            <input
              className="w-full bg-transparent py-4 text-lg font-medium text-ink-900 placeholder:text-slate-400 focus:outline-none"
              placeholder="Search for a phone, laptop, drone..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              autoFocus
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="flex items-center justify-center gap-2 rounded-xl bg-brand-600 px-10 py-4 text-lg font-bold text-white transition hover:bg-brand-700 hover:shadow-lg hover:shadow-brand-500/40 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading && (
              <span className="h-5 w-5 animate-spin rounded-full border-2 border-white/40 border-t-white" />
            )}
            {loading ? "Searching..." : "Search"}
          </button>
        </div>
      </form>

      {loading && (
        <div className="mt-3 flex items-center gap-2 text-sm text-slate-300">
          <span>Taking a while? You can</span>
          <button
            type="button"
            onClick={onStop}
            className="font-semibold text-red-300 underline decoration-red-300/50 underline-offset-2 transition hover:text-red-200"
          >
            stop this search
          </button>
        </div>
      )}
    </div>
  );
}
