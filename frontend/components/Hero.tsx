import SearchBar from "@/components/SearchBar";

export default function Hero({
  onSearch,
  onStop,
  loading,
}: {
  onSearch: (query: string) => void;
  onStop?: () => void;
  loading: boolean;
}) {
  return (
    <section className="bg-grid relative overflow-hidden bg-ink-900 py-20 text-white">
      <div
        className="pointer-events-none absolute inset-0"
        style={{
          background:
            "radial-gradient(circle at 20% 20%, rgba(99,102,241,0.35), transparent 45%), radial-gradient(circle at 80% 0%, rgba(16,185,129,0.25), transparent 40%)",
        }}
      />

      <div className="relative mx-auto max-w-7xl px-6">
        <span className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-1.5 text-xs font-semibold uppercase tracking-wider text-brand-300">
          <span className="h-1.5 w-1.5 animate-pulse-slow rounded-full bg-accent" />
          Live price comparison engine
        </span>

        <h1 className="mt-6 max-w-3xl text-5xl font-extrabold leading-tight tracking-tight text-white">
          Find the best price, every time.
        </h1>

        <p className="mt-4 max-w-xl text-lg text-slate-300">
          Kata Kinum scans Daraz, Hukut and Oliz in real time and ranks the
          results so you always land on the cheapest listing.
        </p>

        <div className="mt-10 max-w-2xl">
          <SearchBar onSearch={onSearch} onStop={onStop} loading={loading} />
        </div>

        <div className="mt-10 flex gap-8 text-sm text-slate-400">
          <div>
            <p className="text-2xl font-bold text-white">3</p>
            <p>Marketplaces tracked</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-white">Live</p>
            <p>Fallback scraping</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-white">Ranked</p>
            <p>By relevance &amp; price</p>
          </div>
        </div>
      </div>
    </section>
  );
}
