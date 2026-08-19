"""
robots.txt Compliance Checker
------------------------------
Standalone, read-only diagnostic script - checks whether the URL paths
our scrapers actually use are allowed by each store's robots.txt.

This file is NOT imported by app.py, routes.py, services.py or any of
the scraper/ modules - running it (or not) has zero effect on the live
app or the scrapers' behavior. It only reports what each site's
robots.txt currently says, for the Ethics & Data Collection section of
the project report.

Run directly:
    python matcher/check_robots_compliance.py
"""

import urllib.request
from urllib.robotparser import RobotFileParser

# The exact paths our scrapers hit today - see scraper/daraz_scraper.py,
# scraper/hukut_scraper.py, scraper/oliz_scraper.py. Kept in sync by hand
# since this script deliberately has no import-time dependency on them.
SITES = {
    "Daraz": {
        "robots_url": "https://www.daraz.com.np/robots.txt",
        "paths": {
            "Category scrape + live search": "/catalog/?q=laptop",
        },
    },
    "Hukut": {
        "robots_url": "https://hukut.com/robots.txt",
        "paths": {
            "Category scrape (mobile-phones)": "/mobile-phones",
            "Category scrape (laptops)": "/laptops",
            "Category scrape (smartwatches)": "/smartwatches",
            "Category scrape (earbuds)": "/earbuds",
            "Category scrape (tablets)": "/tablets",
            "Live search": "/search?q=laptop",
        },
    },
    "Oliz": {
        "robots_url": "https://olizstore.com/robots.txt",
        "paths": {
            "Category scrape (all products)": "/products",
            "Live search": "/search?q=laptop",
        },
    },
}

USER_AGENT = "*"

# RobotFileParser.read() fetches with no User-Agent header at all, which
# some sites (Oliz, behind Cloudflare) silently block - the request
# fails, and robotparser then defaults to "disallow everything" as a
# safe fallback rather than raising, which looks identical to a real
# blanket Disallow unless you notice entries/default_entry are empty.
# Fetching manually with a normal browser User-Agent first, then feeding
# the real content to parser.parse(), avoids that false reading.
FETCH_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"


def check_site(name, config):
    print(f"\n{name}  ({config['robots_url']})")

    parser = RobotFileParser()

    try:
        request = urllib.request.Request(
            config["robots_url"], headers={"User-Agent": FETCH_USER_AGENT}
        )
        with urllib.request.urlopen(request, timeout=10) as response:
            content = response.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  Could not fetch robots.txt: {e}")
        return

    parser.parse(content.splitlines())

    for label, path in config["paths"].items():
        allowed = parser.can_fetch(USER_AGENT, path)
        status = "ALLOWED" if allowed else "DISALLOWED"
        print(f"  [{status:10}] {label:35} -> {path}")


def main():
    print("robots.txt compliance check (read-only, does not affect scraping)")

    for name, config in SITES.items():
        check_site(name, config)

    print(
        "\nNote: robots.txt is a voluntary convention, not a technical "
        "access control - a DISALLOWED path here is not automatically "
        "enforced by the site, and our scrapers are unaffected by "
        "running or not running this script. See docs/thesis_summary.md "
        "for how this is discussed as a disclosed, honest limitation "
        "rather than a functional block."
    )


if __name__ == "__main__":
    main()
