import { beforeEach, describe, expect, it, vi } from "vitest";
import {
  apiClient,
  clearAccessToken,
  getAccessToken,
  setAccessToken,
} from "./apiClient";

describe("apiClient", () => {
  beforeEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  it("stores and retrieves the access token", () => {
    setAccessToken("test-token");

    expect(getAccessToken()).toBe("test-token");
  });

  it("clears the access token", () => {
    setAccessToken("test-token");

    clearAccessToken();

    expect(getAccessToken()).toBeNull();
  });

  it("adds the JWT authorization header", async () => {
    setAccessToken("test-token");

    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ status: "ok" }), {
        status: 200,
        headers: {
          "Content-Type": "application/json",
        },
      }),
    );

    await apiClient("/health");

    const [, requestOptions] = fetchMock.mock.calls[0];

    const headers = requestOptions?.headers as Headers;

    expect(headers.get("Authorization")).toBe("Bearer test-token");

    expect(headers.get("Content-Type")).toBe("application/json");
  });

  it("returns parsed JSON for successful requests", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ message: "success" }), {
        status: 200,
        headers: {
          "Content-Type": "application/json",
        },
      }),
    );

    const result = await apiClient("/health");

    expect(result).toEqual({
      message: "success",
    });
  });

  it("throws the API detail message for failed requests", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(
        JSON.stringify({
          detail: "Contract not found",
        }),
        {
          status: 404,
          headers: {
            "Content-Type": "application/json",
          },
        },
      ),
    );

    await expect(apiClient("/contracts/unknown")).rejects.toThrow(
      "Contract not found",
    );
  });

  it("clears the token when the API returns 401", async () => {
    setAccessToken("expired-token");

    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(
        JSON.stringify({
          detail: "Could not validate credentials",
        }),
        {
          status: 401,
          headers: {
            "Content-Type": "application/json",
          },
        },
      ),
    );

    await expect(apiClient("/contracts/")).rejects.toThrow(
      "Could not validate credentials",
    );

    expect(getAccessToken()).toBeNull();
  });
});
