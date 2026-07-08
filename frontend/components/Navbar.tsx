export default function Navbar() {
  return (
    <nav className="w-full bg-slate-900 text-white shadow-md">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-8 py-5">

        <h1 className="text-3xl font-bold text-blue-400">
          Kata Kinum
        </h1>

        <div className="flex gap-8 text-gray-700 font-medium">
          <button className="hover:text-blue-600 transition">
            Home
          </button>

          <button className="hover:text-blue-600 transition">
            Categories
          </button>

          <button className="hover:text-blue-600 transition">
            About
          </button>
        </div>

      </div>
    </nav>
  );
}