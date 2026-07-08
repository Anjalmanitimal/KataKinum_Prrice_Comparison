"use client";

import { useState } from "react";

import Navbar from "@/components/Navbar"
import Hero from "@/components/Hero";
import SearchBar from "@/components/SearchBar";
import ProductCard from "@/components/ProductCard";

import { searchProducts } from "@/lib/api";

export default function Home() {
  const [products, setProducts] = useState<any[]>([]);

  async function handleSearch(query: string) {
    if (!query) return;

    const data = await searchProducts(query);

    setProducts(data);
  }

  return (
    <main className="min-h-screen bg-gray-100">
      <Navbar />

      <Hero />

      <div className="mx-auto max-w-7xl px-6">
        <SearchBar onSearch={handleSearch} />
      </div>

      <div className="mx-auto mt-10 grid max-w-7xl gap-6 px-6 md:grid-cols-2 lg:grid-cols-3">
        {products.map((product) => (
          <ProductCard
            key={product.product_id}
            product={product}
          />
        ))}
      </div>
    </main>
  );
}