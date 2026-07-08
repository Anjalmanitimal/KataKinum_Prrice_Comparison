import Link from "next/link";

type Product = {
  product_id: string;
  product_name: string;
  marketplace: string;
  price: string;
};

export default function ProductCard({ product }: { product: Product }) {
  return (
    <div className="group rounded-2xl border border-slate-200 bg-white p-6 shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-xl">

      <h2 className="line-clamp-3 text-lg font-bold leading-7 text-slate-900">
        {product.product_name}
      </h2>

      <div className="mt-4 flex items-center gap-2">
        <span className="rounded-full bg-slate-100 px-3 py-1 text-sm font-medium text-slate-700">
          {product.marketplace}
        </span>
      </div>

      <p className="mt-5 text-4xl font-extrabold text-emerald-600">
        {product.price}
      </p>

      <p className="mt-2 text-sm text-slate-500">
        Best available price
      </p>

      <Link href={`/product/${product.product_id}`}>
        <button className="mt-6 w-full rounded-xl bg-blue-600 px-5 py-3 font-semibold text-white transition-all duration-300 hover:bg-blue-700 hover:shadow-lg">
          Compare Prices →
        </button>
      </Link>

    </div>
  );
}