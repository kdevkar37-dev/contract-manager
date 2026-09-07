import { apiClient } from "./apiClient";

export function healthCheck() {
  return apiClient("/health");
}
