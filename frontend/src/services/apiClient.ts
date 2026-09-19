const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export async function apiClient(endpoint: string, options?: RequestInit) {
  const headers = new Headers(options?.headers);

  if (!(options?.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorMessage = `API request failed: ${response.status}`;

    try {
      const errorData = await response.json();

      if (typeof errorData?.detail === "string") {
        errorMessage = errorData.detail;
      }
    } catch {
      // Keep the default error message.
    }

    throw new Error(errorMessage);
  }

  return response.json();
}
