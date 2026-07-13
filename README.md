# Kata Kinum

A price comparison platform for Nepal's electronics market. Kata Kinum searches Daraz, Hukut and Oliz at once so you can find the cheapest listing for a product without checking each site separately.

## Features

- **Live multi-store search** — checks a curated dataset first, and falls back to live scraping Daraz, Hukut and Oliz when a product isn't already tracked.
- **Semantic search** — TF-IDF + cosine similarity matching so search understands reordered or loosely-worded queries, without ever substituting a different model for what you searched.
- **Automatic categorization** — K-Means clustering groups uncategorized products into sensible categories on its own.
- **Price trend prediction** — a linear regression model tracks price history per product and flags whether it's trending up, down, or holding steady.
- **Verified deal detection** — the best-deals engine cross-checks matched products for conflicting model numbers or tiers before trusting a price gap, so featured deals are real, not mismatched listings.
- **Sort & filter** — sort by price or relevance, filter by store, and set a price range on any results page.

## Tech Stack

**Backend:** Python, Flask, Pandas, scikit-learn, rapidfuzz, Selenium
**Frontend:** Next.js, React, TypeScript, Tailwind CSS

## Project Structure

```
backend/    Flask API, search/category/deals/price-trend routes
matcher/    Product matching, cleaning, and category clustering pipeline
scraper/    Daraz, Hukut and Oliz scrapers (batch + live search modes)
frontend/   Next.js app
data/       Processed CSV datasets (gitignored)
```

## Running Locally

**Backend:**

```
cd backend
python app.py
```

Runs on `http://127.0.0.1:5000`.

**Frontend:**

```
cd frontend
npm install
npm run dev
```

Runs on `http://localhost:3000` and expects the backend running on port 5000.

## Disclaimer

Prices are collected from public store listings via periodic and on-demand scraping — they may occasionally lag behind a store's real-time price. Kata Kinum is not affiliated with Daraz, Hukut or Oliz.
