"use client";

import { useRef, useState } from "react";

import Navbar from "@/components/Navbar";
import Hero from "@/components/Hero";
import ProductCard from "@/components/ProductCard";

import { searchProducts } from "@/lib/api";
import type { ProductGroup } from "@/types/product";

export default function Home() {
  const [products, setProducts] = useState<ProductGroup[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [stopped, setStopped] = useState(false);
  const [searched, setSearched] = useState(false);

  const controllerRef = useRef<AbortController | null>(null);

  async function handleSearch(query: string) {
    controllerRef.current?.abort();
    const controller = new AbortController();
    controllerRef.current = controller;

    setLoading(true);
    setError(null);
    setStopped(false);
    setSearched(true);

    try {
      const data = await searchProducts(query, controller.signal);
      setProducts(data);
    } catch (err) {
      if (err instanceof DOMException && err.name === "AbortError") {
        setStopped(true);
      } else {
        setProducts([]);
        setError(
          "Couldn't reach the search engine. Make sure the backend is running and try again."
        );
      }
    } finally {
      setLoading(false);
      controllerRef.current = null;
    }
  }

  function handleStop() {
    controllerRef.current?.abort();
  }

  return (
    <main className="min-h-screen bg-background">
      <Navbar />

      <Hero onSearch={handleSearch} onStop={handleStop} loading={loading} />

      <div className="mx-auto max-w-7xl px-6 pb-24">
        {loading && (
          <div className="mt-16 flex flex-col items-center gap-3 text-center text-slate-500">
            <span className="h-10 w-10 animate-spin rounded-full border-4 border-brand-100 border-t-brand-600" />
            <p className="font-medium">
              Scanning Daraz, Hukut and Oliz for the best price...
            </p>
            <p className="text-sm text-slate-400">
              New products may take up to 30 seconds to fetch live.
            </p>
          </div>
        )}

        {!loading && stopped && (
          <div className="mt-16 rounded-2xl border border-surface-border bg-surface p-6 text-center text-slate-500">
            Search stopped.
          </div>
        )}

        {!loading && error && (
          <div className="mt-16 rounded-2xl border border-red-200 bg-red-50 p-6 text-center text-red-700">
            {error}
          </div>
        )}

        {!loading && !error && !stopped && searched && products.length === 0 && (
          <div className="mt-16 rounded-2xl border border-surface-border bg-surface p-10 text-center text-slate-500">
            No products found. Try a different search term.
          </div>
        )}

        {!loading && !error && products.length > 0 && (
          <>
            <p className="mt-10 mb-4 text-sm font-medium text-slate-500">
              Comparing {products.length} product{products.length === 1 ? "" : "s"} across marketplaces
            </p>

            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {products.map((product) => (
                <ProductCard key={product.product_id} product={product} />
              ))}
            </div>
          </>
        )}
      </div>
    </main>
  );
}
