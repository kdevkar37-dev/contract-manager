import { beforeEach, describe, expect, it } from "vitest";
import { fireEvent, render, screen } from "@testing-library/react";

import App from "./App";
import { setAccessToken } from "./services/apiClient";

describe("App authentication routing", () => {
  beforeEach(() => {
    localStorage.clear();
    window.history.pushState({}, "", "/");
  });

  it("redirects unauthenticated users to the login page", () => {
    window.history.pushState({}, "", "/dashboard");

    render(<App />);

    expect(
      screen.getByRole("heading", {
        name: "Contract Manager",
      }),
    ).toBeTruthy();
  });

  it("allows authenticated users to access the dashboard", () => {
    setAccessToken("test-access-token");

    window.history.pushState({}, "", "/dashboard");

    render(<App />);

    expect(
      screen.getByRole("heading", {
        name: "Contract Dashboard",
      }),
    ).toBeTruthy();
  });

  it("logs the user out and redirects to login", () => {
    setAccessToken("test-access-token");

    window.history.pushState({}, "", "/dashboard");

    render(<App />);

    const logoutButton = screen.getByRole("button", {
      name: /logout/i,
    });

    fireEvent.click(logoutButton);

    expect(
      screen.getByRole("heading", {
        name: "Contract Manager",
      }),
    ).toBeTruthy();

    expect(localStorage.getItem("contract_manager_access_token")).toBeNull();
  });
});
