import Navbar from "@/components/Navbar";

const FEATURES = [
  {
    icon: "🔍",
    title: "Live multi-store scraping",
    description:
      "Searches Daraz, Hukut and Oliz in real time when a product isn't already tracked, so results stay current instead of relying on a stale catalog.",
  },
  {
    icon: "🧠",
    title: "Semantic search",
    description:
      "Goes beyond exact keyword matching using TF-IDF and cosine similarity, so reordered or loosely-worded searches still find the right product — without ever substituting a different model.",
  },
  {
    icon: "🗂️",
    title: "Automatic categorization",
    description:
      "K-Means clustering groups uncategorized products into sensible categories on its own, filling in the gaps left by inconsistent store-provided tags.",
  },
  {
    icon: "📈",
    title: "Price trend prediction",
    description:
      "A linear regression model tracks each product's price over time and flags whether it's trending up, down, or holding steady — once enough real data has been collected.",
  },
  {
    icon: "🏷️",
    title: "Verified deal detection",
    description:
      "The best-deals engine cross-checks matched products for conflicting model numbers or tiers before trusting a price gap, so featured deals are real, not mismatched listings.",
  },
];

const TECH_STACK = [
  { group: "Backend", items: ["Python", "Flask", "Pandas", "scikit-learn"] },
  { group: "Frontend", items: ["Next.js", "React", "TypeScript", "Tailwind CSS"] },
];

export default function AboutPage() {
  return (
    <main className="min-h-screen bg-background">
      <Navbar />

      <div className="mx-auto max-w-4xl px-6 py-16">
        <h1 className="text-4xl font-bold text-ink-900">About Kata Kinum</h1>

        <p className="mt-4 text-lg leading-relaxed text-slate-600">
          Kata Kinum is a price comparison platform for Nepal&apos;s electronics
          market. Instead of checking Daraz, Hukut and Oliz separately every
          time you want to buy something, Kata Kinum searches all three at
          once and shows you exactly where it&apos;s cheapest.
        </p>

        <p className="mt-4 leading-relaxed text-slate-600">
          Nepal&apos;s online electronics market is fragmented — the same
          product is often listed at noticeably different prices across
          stores, with no easy way to compare them side by side. Kata Kinum
          exists to close that gap: one search, every store, the real
          cheapest price.
        </p>

        <h2 className="mt-14 text-2xl font-bold text-ink-900">How it works</h2>
        <p className="mt-2 text-slate-500">
          A few things happen behind the scenes to make the comparisons
          trustworthy, not just fast.
        </p>

        <div className="mt-8 grid gap-5 sm:grid-cols-2">
          {FEATURES.map((feature) => (
            <div
              key={feature.title}
              className="rounded-2xl border border-surface-border bg-surface p-6 shadow-sm"
            >
              <span className="text-2xl">{feature.icon}</span>
              <h3 className="mt-3 font-semibold text-ink-900">
                {feature.title}
              </h3>
              <p className="mt-1.5 text-sm leading-relaxed text-slate-500">
                {feature.description}
              </p>
            </div>
          ))}
        </div>

        <h2 className="mt-14 text-2xl font-bold text-ink-900">Built with</h2>

        <div className="mt-6 flex flex-wrap gap-8">
          {TECH_STACK.map((stack) => (
            <div key={stack.group}>
              <p className="text-sm font-semibold uppercase tracking-wider text-slate-400">
                {stack.group}
              </p>
              <div className="mt-3 flex flex-wrap gap-2">
                {stack.items.map((item) => (
                  <span
                    key={item}
                    className="rounded-lg bg-brand-50 px-3 py-1.5 text-sm font-medium text-brand-700"
                  >
                    {item}
                  </span>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div className="mt-14 rounded-2xl border border-surface-border bg-surface p-6 text-sm leading-relaxed text-slate-500">
          Prices are collected from public store listings and refreshed
          through periodic and on-demand scraping — they may occasionally lag
          behind a store&apos;s real-time price. Kata Kinum is not affiliated
          with Daraz, Hukut or Oliz; all trademarks belong to their respective
          owners.
        </div>
      </div>
    </main>
  );
}
