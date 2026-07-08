const API = "http://127.0.0.1:5000";

export async function searchProducts(query: string) {
  const response = await fetch(
    `http://127.0.0.1:5000/search?q=${query}`
  );

  return await response.json();
}

export async function getProduct(productId: string) {
  const res = await fetch(
    `${API}/product/${productId}`
  );

  return await res.json();
}