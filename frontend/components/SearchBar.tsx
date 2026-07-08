"use client";

import { useState } from "react";

export default function SearchBar({
    onSearch,
}: {
    onSearch: (query: string) => void;
}) {

    const [query, setQuery] = useState("");

    return (

        <div className="flex gap-4 mt-10">

            <input
                className="flex-1 rounded-xl border border-gray-300 bg-white text-black p-4 focus:outline-none focus:ring-2 focus:ring-black"
                placeholder="Search laptops, phones..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
            />

            <button
                className="bg-black text-white px-8 rounded-xl hover:bg-gray-800 transition"
                onClick={() => onSearch(query)}
            >
                Search
            </button>

        </div>

    );
}