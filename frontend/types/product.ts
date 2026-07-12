export interface StoreOffer {
  marketplace: string;
  price: string;
  price_numeric: number | null;
  link: string;
}

export interface ProductGroup {
  product_id: string;
  product_name: string;
  clean_name: string | null;
  offers: StoreOffer[];
  lowest_price: number | null;
  lowest_price_display: string | null;
  store_count: number;
}

export interface Category {
  category: string;
  label: string;
  count: number;
}

export interface PricePoint {
  date: string;
  price: number;
}

export interface PriceTrend {
  status: "ok" | "insufficient_data";
  points: PricePoint[];
  message?: string;
  trend?: "falling" | "rising" | "stable";
  recommendation?: string;
  lowest_recorded?: number;
  highest_recorded?: number;
  current?: number | null;
  first_tracked?: string | null;
  points_needed?: number;
}

export interface Deal {
  product_id: string;
  product_name: string;
  best_store: string;
  best_price: number;
  best_price_display: string;
  highest_store: string;
  highest_price: number;
  highest_price_display: string;
  savings: number;
  savings_percent: number;
  store_count: number;
  price_trend: "falling" | "rising" | "stable" | null;
}
