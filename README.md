# Kata Kinum

A price comparison platform for Nepal's electronics market. Kata Kinum searches Daraz, Hukut and Oliz at once so you can find the cheapest listing for a product without checking each site separately.

## Features

- **Live multi-store search** — checks a curated dataset first, and falls back to live scraping Daraz, Hukut and Oliz when a product isn't already tracked.
- **Semantic search** — TF-IDF + cosine similarity matching so search understands reordered or loosely-worded queries, without ever substituting a different model for what you searched.
- **Automatic categorization** — K-Means clustering groups uncategorized products into sensible categories on its own.
- **Price trend prediction** — a linear regression model tracks price history per product and flags whether it's trending up, down, or holding steady.
- **Verified deal detection** — the best-deals engine cross-checks matched products for conflicting model numbers or tiers before trusting a price gap, so featured deals are real, not mismatched listings.
- **Sort & filter** — sort by price or relevance, filter by store, and set a price range on any results page.
- **Analytics** — Matplotlib-generated charts (average price by category, price trend overview) served directly from the backend.

## Tech Stack

**Backend:** Python, Flask, Pandas, scikit-learn, rapidfuzz, Selenium, Matplotlib, SQLite
**Frontend:** Next.js, React, TypeScript, Tailwind CSS

## Project Structure

```
backend/    Flask API, SQLite data access (db.py), search/category/deals/price-trend/analytics routes
matcher/    Product matching, cleaning, category clustering, and SQLite migration pipeline
scraper/    Daraz, Hukut and Oliz scrapers (batch + live search modes)
frontend/   Next.js app
data/       Processed CSV pipeline output + the SQLite database (gitignored)
```

## Running Locally

**Backend** (run from the project root, not from inside `backend/` — relative data paths depend on it):

```
python backend/app.py
```

Runs on `http://127.0.0.1:5000`.

If `data/processed/matched_products.csv` has been regenerated (e.g. after re-running the scraping/matching pipeline), migrate it into the database first:

```
python matcher/migrate_to_sqlite.py
```

**Frontend:**

```
cd frontend
npm install
npm run dev
```

Runs on `http://localhost:3000` and expects the backend running on port 5000.

## Disclaimer

Prices are collected from public store listings via periodic and on-demand scraping — they may occasionally lag behind a store's real-time price. Kata Kinum is not affiliated with Daraz, Hukut or Oliz.
