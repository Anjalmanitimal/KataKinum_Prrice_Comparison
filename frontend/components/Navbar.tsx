import Link from "next/link";

export default function Navbar() {
  return (
    <nav className="sticky top-0 z-50 w-full border-b border-white/10 bg-ink-900/95 text-white shadow-lg backdrop-blur">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-8 py-5">

        <Link href="/" className="flex items-center gap-2">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-brand-400 to-brand-600 text-sm font-black text-white">
            K
          </span>
          <span className="text-xl font-bold tracking-tight text-white">
            Kata Kinum
          </span>
        </Link>

        <div className="flex items-center gap-8 text-sm font-medium text-slate-300">
          <Link href="/" className="transition hover:text-brand-300">
            Home
          </Link>
          <Link href="/categories" className="transition hover:text-brand-300">
            Categories
          </Link>
          <Link href="/deals" className="transition hover:text-brand-300">
            Deals
          </Link>
          <Link href="/about" className="transition hover:text-brand-300">
            About
          </Link>
        </div>

      </div>
    </nav>
  );
}
