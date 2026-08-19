import Link from "next/link";

import type { ProductGroup } from "@/types/product";
import { formatPriceDate } from "@/lib/formatDate";

const STORE_STYLES: Record<string, string> = {
  Daraz: "bg-orange-50 text-orange-700 ring-orange-200",
  Hukut: "bg-sky-50 text-sky-700 ring-sky-200",
  Oliz: "bg-violet-50 text-violet-700 ring-violet-200",
};

function storeStyle(marketplace: string) {
  return STORE_STYLES[marketplace] ?? "bg-slate-100 text-slate-700 ring-slate-200";
}

export default function ProductCard({ product }: { product: ProductGroup }) {
  const cheapestOffer = product.offers[0];
  const cheapestMarketplace = cheapestOffer?.marketplace;

  return (
    <div className="group flex h-full flex-col rounded-2xl border border-surface-border bg-surface p-6 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-xl hover:shadow-brand-500/10">

      <div className="flex items-start justify-between gap-3">
        <h2 className="line-clamp-2 text-lg font-semibold leading-6 text-ink-900">
          {product.product_name}
        </h2>

        {product.store_count > 1 && (
          <span className="shrink-0 rounded-full bg-brand-50 px-2.5 py-1 text-xs font-semibold text-brand-700 ring-1 ring-inset ring-brand-100">
            {product.store_count} stores
          </span>
        )}
      </div>

      <p className="mt-4 text-4xl font-extrabold tracking-tight text-ink-900">
        {product.lowest_price_display ?? "—"}
      </p>
      <p className="mt-1 text-sm font-medium text-accent-strong">
        Lowest price{cheapestMarketplace ? ` · ${cheapestMarketplace}` : ""}
      </p>
      <p className="mt-0.5 text-xs text-slate-400">
        Price as of {formatPriceDate(cheapestOffer?.scraped_at)}
      </p>

      {product.price_anomaly === "cheap" && (
        <span className="mt-2 inline-flex w-fit items-center gap-1 rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-bold text-emerald-700 ring-1 ring-inset ring-emerald-200">
          ⚡ Great price for this category
        </span>
      )}
      {product.price_anomaly === "expensive" && (
        <span className="mt-2 inline-flex w-fit items-center gap-1 rounded-full bg-amber-50 px-2.5 py-1 text-xs font-bold text-amber-700 ring-1 ring-inset ring-amber-200">
          Priced high for this category
        </span>
      )}

      <div className="mt-5 flex flex-wrap gap-2">
        {product.offers.map((offer, index) => (
          <span
            key={`${product.product_id}-${offer.marketplace}-${offer.link ?? index}`}
            className={`inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-xs font-semibold ring-1 ring-inset ${storeStyle(offer.marketplace)}`}
          >
            {offer.marketplace}
            <span className="font-bold">{offer.price}</span>
          </span>
        ))}
      </div>

      <div className="mt-auto pt-6">
        <Link href={`/product/${product.product_id}`}>
          <button className="w-full rounded-xl bg-ink-900 px-5 py-3 font-semibold text-white transition-all duration-300 hover:bg-brand-600 hover:shadow-lg hover:shadow-brand-500/30">
            Compare Prices →
          </button>
        </Link>
      </div>

    </div>
  );
}
