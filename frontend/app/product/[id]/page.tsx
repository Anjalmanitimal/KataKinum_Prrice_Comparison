"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { getProduct } from "@/lib/api";

export default function ProductPage() {
  const params = useParams();

  const [products, setProducts] = useState<any[]>([]);

  useEffect(() => {
    async function loadData() {
      const data = await getProduct(params.id as string);
      setProducts(data);
    }

    loadData();
  }, [params.id]);

  if (products.length === 0) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-100 text-slate-900">
        Loading...
      </div>
    );
  }

  const cheapest = products[0];

  return (
    <main className="min-h-screen bg-slate-100 px-6 py-10 text-slate-900">

      <div className="mx-auto max-w-6xl">

        <h1 className="mb-8 text-4xl font-bold text-slate-900">
          {cheapest.product_name}
        </h1>

        <div className="mb-8 rounded-2xl border border-emerald-200 bg-emerald-50 p-8 shadow-sm">

          <p className="text-sm font-semibold uppercase tracking-wider text-emerald-700">
            Best Price
          </p>

          <h2 className="mt-2 text-5xl font-extrabold text-emerald-600">
            {cheapest.price}
          </h2>

          <p className="mt-2 text-lg text-slate-700">
            {cheapest.marketplace}
          </p>

        </div>

        <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-md">

          <table className="w-full">

            <thead className="bg-slate-800 text-white">

              <tr>
                <th className="px-6 py-4 text-left">Store</th>
                <th className="px-6 py-4 text-left">Price</th>
                <th className="px-6 py-4 text-left">Visit</th>
              </tr>

            </thead>

            <tbody>

              {products.map((item) => (
                <tr
                  key={`${item.product_id}-${item.marketplace}`}
                  className="border-t border-slate-200 hover:bg-slate-50"
                >
                  <td className="px-6 py-4 font-medium text-slate-800">
                    {item.marketplace}
                  </td>

                  <td className="px-6 py-4 text-lg font-bold text-emerald-600">
                    {item.price}
                  </td>

                  <td className="px-6 py-4">
                    <a
                      href={item.link}
                      target="_blank"
                      rel="noreferrer"
                      className="rounded-lg bg-blue-600 px-4 py-2 text-white transition hover:bg-blue-700"
                    >
                      Visit Store
                    </a>
                  </td>
                </tr>
              ))}

            </tbody>

          </table>

        </div>

      </div>

    </main>
  );
}