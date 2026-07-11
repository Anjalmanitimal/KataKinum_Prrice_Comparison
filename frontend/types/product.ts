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
