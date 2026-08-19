import type { ProductGroup } from "@/types/product";

export type SortOption = "relevance" | "price_asc" | "price_desc";

export interface FilterState {
  sort: SortOption;
  store: string;
  minPrice: string;
  maxPrice: string;
  search: string;
  // Types the user has toggled OFF. Empty means every type present in
  // the results is shown, matching "if shown mobile only keep mobile
  // only, if shown mobile and case keep both" by default.
  excludedTypes: string[];
}

export const DEFAULT_FILTERS: FilterState = {
  sort: "relevance",
  store: "all",
  minPrice: "",
  maxPrice: "",
  search: "",
  excludedTypes: [],
};

export function applyFilters(
  products: ProductGroup[],
  filters: FilterState
): ProductGroup[] {
  let result: ProductGroup[] = products;

  if (filters.search.trim()) {
    const query = filters.search.trim().toLowerCase();
    result = result.filter((p) =>
      p.product_name.toLowerCase().includes(query)
    );
  }

  if (filters.excludedTypes.length > 0) {
    result = result.filter(
      (p) => !p.listing_type || !filters.excludedTypes.includes(p.listing_type)
    );
  }

  if (filters.store !== "all") {
    result = result
      .map((product) => {
        const offers = product.offers.filter(
          (offer) => offer.marketplace === filters.store
        );

        if (offers.length === 0) return null;

        const cheapest = offers.reduce((a, b) =>
          (a.price_numeric ?? Infinity) < (b.price_numeric ?? Infinity) ? a : b
        );

        const withFilteredOffer: ProductGroup = {
          ...product,
          offers,
          lowest_price: cheapest.price_numeric,
          lowest_price_display: cheapest.price,
          store_count: offers.length,
        };

        return withFilteredOffer;
      })
      .filter((p): p is ProductGroup => p !== null);
  }

  const min = filters.minPrice ? Number(filters.minPrice) : null;
  const max = filters.maxPrice ? Number(filters.maxPrice) : null;

  if (min !== null) {
    result = result.filter(
      (p) => p.lowest_price !== null && p.lowest_price >= min
    );
  }

  if (max !== null) {
    result = result.filter(
      (p) => p.lowest_price !== null && p.lowest_price <= max
    );
  }

  if (filters.sort === "price_asc") {
    result = [...result].sort(
      (a, b) => (a.lowest_price ?? Infinity) - (b.lowest_price ?? Infinity)
    );
  } else if (filters.sort === "price_desc") {
    result = [...result].sort(
      (a, b) => (b.lowest_price ?? -Infinity) - (a.lowest_price ?? -Infinity)
    );
  }

  return result;
}
