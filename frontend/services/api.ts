const API = "http://127.0.0.1:5000";

export async function searchProducts(query: string) {

    if (!query) return [];

    const response = await fetch(
        `${API}/search?q=${encodeURIComponent(query)}`
    );

    return await response.json();
}