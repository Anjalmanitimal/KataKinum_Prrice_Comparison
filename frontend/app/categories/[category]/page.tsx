"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";

import Navbar from "@/components/Navbar";
import ProductCard from "@/components/ProductCard";
import FilterSortBar from "@/components/FilterSortBar";
import { getCategoryProducts } from "@/lib/api";
import type { ProductGroup } from "@/types/product";
import { applyFilters, DEFAULT_FILTERS, type FilterState } from "@/lib/filterProducts";

const CATEGORY_LABELS: Record<string, string> = {
  smartphone: "Smartphones",
  laptop: "Laptops",
  tablet: "Tablets",
  smartwatch: "Smartwatches",
  earphone: "Earphones",
  bag: "Bags & Backpacks",
  watch: "Watches",
  camera_gear: "Drones & Camera Gear",
  powerbank: "Power Banks & Chargers",
  audio: "Speakers & Audio",
  appliance: "Home Appliances",
};

export default function CategoryPage() {
  const params = useParams();
  const category = params.category as string;

  const [products, setProducts] = useState<ProductGroup[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<FilterState>(DEFAULT_FILTERS);

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError(null);
      setFilters(DEFAULT_FILTERS);

      try {
        const data = await getCategoryProducts(category);
        setProducts(data);
      } catch {
        setError("Couldn't load this category. Make sure the backend is running.");
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [category]);

  const label = CATEGORY_LABELS[category] ?? category;

  return (
    <main className="min-h-screen bg-background">
      <Navbar />

      <div className="mx-auto max-w-7xl px-6 py-16">
        <Link
          href="/categories"
          className="mb-6 inline-flex items-center gap-1 text-sm font-medium text-slate-500 transition hover:text-brand-600"
        >
          ← All categories
        </Link>

        <h1 className="text-4xl font-bold text-ink-900">{label}</h1>

        {loading && (
          <div className="mt-16 flex flex-col items-center gap-3 text-center text-slate-500">
            <span className="h-10 w-10 animate-spin rounded-full border-4 border-brand-100 border-t-brand-600" />
            <p className="font-medium">Loading {label.toLowerCase()}...</p>
          </div>
        )}

        {!loading && error && (
          <div className="mt-16 rounded-2xl border border-red-200 bg-red-50 p-6 text-center text-red-700">
            {error}
          </div>
        )}

        {!loading && !error && products.length === 0 && (
          <div className="mt-16 rounded-2xl border border-surface-border bg-surface p-10 text-center text-slate-500">
            No products found in this category.
          </div>
        )}

        {!loading && !error && products.length > 0 && (() => {
          const filtered = applyFilters(products, filters);

          return (
            <div className="mt-4">
              <FilterSortBar
                filters={filters}
                onChange={setFilters}
                resultCount={filtered.length}
              />

              {filtered.length === 0 ? (
                <div className="rounded-2xl border border-surface-border bg-surface p-10 text-center text-slate-500">
                  No products match these filters. Try widening your range.
                </div>
              ) : (
                <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
                  {filtered.map((product) => (
                    <ProductCard key={product.product_id} product={product} />
                  ))}
                </div>
              )}
            </div>
          );
        })()}
      </div>
    </main>
  );
}
