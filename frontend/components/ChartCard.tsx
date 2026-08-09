"use client";

import { useState } from "react";

export default function ChartCard({
  title,
  description,
  imageUrl,
  badge,
}: {
  title: string;
  description: string;
  imageUrl: string;
  badge?: string;
}) {
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState(false);

  return (
    <div className="rounded-2xl border border-surface-border bg-surface p-6 shadow-sm">
      <div className="flex items-start justify-between gap-3">
        <h2 className="text-lg font-semibold text-ink-900">{title}</h2>
        {badge && (
          <span className="shrink-0 rounded-full bg-amber-50 px-2.5 py-1 text-xs font-bold text-amber-700 ring-1 ring-inset ring-amber-200">
            {badge}
          </span>
        )}
      </div>
      <p className="mt-1 text-sm text-slate-500">{description}</p>

      <div className="mt-6 flex min-h-[300px] items-center justify-center">
        {!loaded && !error && (
          <div className="flex flex-col items-center gap-3 text-slate-500">
            <span className="h-8 w-8 animate-spin rounded-full border-4 border-brand-100 border-t-brand-600" />
            <p className="text-sm font-medium">Generating chart...</p>
          </div>
        )}

        {error && (
          <p className="text-sm text-red-600">
            Couldn&apos;t load this chart. Make sure the backend is running.
          </p>
        )}

        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src={imageUrl}
          alt={title}
          className={`w-full rounded-xl ${loaded ? "block" : "hidden"}`}
          onLoad={() => setLoaded(true)}
          onError={() => setError(true)}
        />
      </div>
    </div>
  );
}
