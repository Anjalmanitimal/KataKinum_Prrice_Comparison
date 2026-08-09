import Navbar from "@/components/Navbar";
import ChartCard from "@/components/ChartCard";

const API = "http://127.0.0.1:5000";

export default function AnalyticsPage() {
  return (
    <main className="min-h-screen bg-background">
      <Navbar />

      <div className="mx-auto max-w-5xl px-6 py-16">
        <h1 className="text-4xl font-bold text-ink-900">Analytics</h1>
        <p className="mt-2 text-slate-500">
          A look at the pricing landscape across everything Kata Kinum
          tracks.
        </p>

        <div className="mt-10 flex flex-col gap-6">
          <ChartCard
            title="Average Price by Category"
            description="Where the money goes — average price per category across all tracked products, generated live from the real dataset."
            imageUrl={`${API}/analytics/average-price-by-category.png`}
          />

          <ChartCard
            title="Price Trend Overview"
            description="How many tracked products are trending up, down, or holding steady. Real price tracking is still early (see any product page for live, honest 'still gathering data' status) — this chart uses simulated multi-week history to demonstrate what it will look like once real tracking has run for longer."
            imageUrl={`${API}/analytics/price-trend-overview.png`}
            badge="Simulated data"
          />
        </div>
      </div>
    </main>
  );
}
