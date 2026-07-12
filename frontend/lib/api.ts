import type { Category, Deal, PriceTrend, ProductGroup } from "@/types/product";

const API = "http://127.0.0.1:5000";

export async function searchProducts(
  query: string,
  signal?: AbortSignal
): Promise<ProductGroup[]> {
  const response = await fetch(
    `${API}/search?q=${encodeURIComponent(query)}`,
    { signal }
  );

  if (!response.ok) {
    throw new Error(`Search failed with status ${response.status}`);
  }

  return await response.json();
}

export async function getDeals(): Promise<Deal[]> {
  const response = await fetch(`${API}/deals`);

  if (!response.ok) {
    throw new Error(`Deals failed with status ${response.status}`);
  }

  return await response.json();
}

export async function getCategories(): Promise<Category[]> {
  const response = await fetch(`${API}/categories`);

  if (!response.ok) {
    throw new Error(`Categories failed with status ${response.status}`);
  }

  return await response.json();
}

export async function getCategoryProducts(
  category: string
): Promise<ProductGroup[]> {
  const response = await fetch(
    `${API}/category/${encodeURIComponent(category)}`
  );

  if (!response.ok) {
    throw new Error(`Category lookup failed with status ${response.status}`);
  }

  return await response.json();
}

export async function getPriceTrend(productId: string): Promise<PriceTrend> {
  const response = await fetch(
    `${API}/product/${encodeURIComponent(productId)}/trend`
  );

  if (!response.ok) {
    throw new Error(`Price trend failed with status ${response.status}`);
  }

  return await response.json();
}

export async function getProduct(productId: string) {
  const response = await fetch(
    `${API}/product/${encodeURIComponent(productId)}`
  );

  if (!response.ok) {
    throw new Error(`Product lookup failed with status ${response.status}`);
  }

  return await response.json();
}
