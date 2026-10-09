const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const TOKEN_KEY = "contract_manager_access_token";

export function getAccessToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setAccessToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearAccessToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}

export async function apiClient(endpoint: string, options?: RequestInit) {
  const headers = new Headers(options?.headers);
  const token = getAccessToken();
  const body = options?.body;

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  if (body instanceof FormData) {
    // Let the browser set Content-Type including the multipart boundary.
    headers.delete("Content-Type");
  } else if (body instanceof URLSearchParams) {
    headers.set("Content-Type", "application/x-www-form-urlencoded");
  } else {
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
      } else if (Array.isArray(errorData?.detail)) {
        errorMessage = errorData.detail
          .map((item: { msg?: string }) => item.msg || "Validation error")
          .join(", ");
      }
    } catch {
      // Keep the default error message.
    }

    if (response.status === 401) {
      clearAccessToken();
    }

    throw new Error(errorMessage);
  }

  return response.json();
}
