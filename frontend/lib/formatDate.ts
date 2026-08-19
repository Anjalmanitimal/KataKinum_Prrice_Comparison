export function formatPriceDate(scrapedAt: string | null | undefined): string {
  if (!scrapedAt) {
    return "Date unknown";
  }

  // Backend sends "YYYY-MM-DD HH:MM:SS" (space, not "T"). Safari and
  // older engines don't parse that format reliably via `new Date(...)`.
  const parsed = new Date(scrapedAt.replace(" ", "T"));

  if (isNaN(parsed.getTime())) {
    return "Date unknown";
  }

  const now = new Date();
  const isSameDay =
    parsed.getFullYear() === now.getFullYear() &&
    parsed.getMonth() === now.getMonth() &&
    parsed.getDate() === now.getDate();

  if (isSameDay) {
    return "Today";
  }

  const yesterday = new Date(now);
  yesterday.setDate(now.getDate() - 1);
  const isYesterday =
    parsed.getFullYear() === yesterday.getFullYear() &&
    parsed.getMonth() === yesterday.getMonth() &&
    parsed.getDate() === yesterday.getDate();

  if (isYesterday) {
    return "Yesterday";
  }

  return parsed.toLocaleDateString("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}
