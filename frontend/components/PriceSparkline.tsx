import type { PricePoint } from "@/types/product";

export default function PriceSparkline({
  points,
  color = "#4f46e5",
}: {
  points: PricePoint[];
  color?: string;
}) {
  const width = 240;
  const height = 60;
  const padding = 6;

  const prices = points.map((p) => p.price);
  const min = Math.min(...prices);
  const max = Math.max(...prices);
  const range = max - min || 1;

  const coords = points.map((p, i) => {
    const x =
      points.length === 1
        ? width / 2
        : padding + (i / (points.length - 1)) * (width - padding * 2);
    const y =
      height - padding - ((p.price - min) / range) * (height - padding * 2);
    return { x, y };
  });

  const path = coords
    .map((c, i) => `${i === 0 ? "M" : "L"}${c.x.toFixed(1)},${c.y.toFixed(1)}`)
    .join(" ");

  return (
    <svg
      width={width}
      height={height}
      viewBox={`0 0 ${width} ${height}`}
      className="overflow-visible"
    >
      <path d={path} fill="none" stroke={color} strokeWidth={2} />
      {coords.map((c, i) => (
        <circle key={i} cx={c.x} cy={c.y} r={3} fill={color} />
      ))}
    </svg>
  );
}
