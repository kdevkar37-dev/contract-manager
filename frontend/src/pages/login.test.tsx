import { beforeEach, describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";

import Login from "./login";
import * as apiClientModule from "../services/apiClient";

vi.mock("../services/apiClient", () => ({
  apiClient: vi.fn(),
  setAccessToken: vi.fn(),
}));

const mockedApiClient = vi.mocked(apiClientModule.apiClient);
const mockedSetAccessToken = vi.mocked(apiClientModule.setAccessToken);

describe("Login page", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  function renderLogin() {
    return render(
      <MemoryRouter>
        <Login />
      </MemoryRouter>,
    );
  }

  it("renders the login form", () => {
    renderLogin();

    expect(
      screen.getByRole("heading", {
        name: "Contract Manager",
      }),
    ).toBeTruthy();

    expect(screen.getByLabelText("Email")).toBeTruthy();

    expect(screen.getByLabelText("Password")).toBeTruthy();

    expect(
      screen.getByRole("button", {
        name: "Sign In",
      }),
    ).toBeTruthy();
  });

  it("shows validation error when fields are empty", async () => {
    renderLogin();

    fireEvent.click(
      screen.getByRole("button", {
        name: "Sign In",
      }),
    );

    const error = await screen.findByText("Email and password are required.");

    expect(error).toBeTruthy();
    expect(mockedApiClient).not.toHaveBeenCalled();
  });

  it("submits credentials to the login API", async () => {
    mockedApiClient.mockResolvedValue({
      access_token: "test-access-token",
      token_type: "bearer",
    });

    renderLogin();

    fireEvent.change(screen.getByLabelText("Email"), {
      target: {
        value: "manager@example.com",
      },
    });

    fireEvent.change(screen.getByLabelText("Password"), {
      target: {
        value: "password123",
      },
    });

    fireEvent.click(
      screen.getByRole("button", {
        name: "Sign In",
      }),
    );

    await waitFor(() => {
      expect(mockedApiClient).toHaveBeenCalledWith("/auth/login", {
        method: "POST",
        body: JSON.stringify({
          email: "manager@example.com",
          password: "password123",
        }),
      });
    });
  });

  it("stores the access token after successful login", async () => {
    mockedApiClient.mockResolvedValue({
      access_token: "test-access-token",
      token_type: "bearer",
    });

    renderLogin();

    fireEvent.change(screen.getByLabelText("Email"), {
      target: {
        value: "manager@example.com",
      },
    });

    fireEvent.change(screen.getByLabelText("Password"), {
      target: {
        value: "password123",
      },
    });

    fireEvent.click(
      screen.getByRole("button", {
        name: "Sign In",
      }),
    );

    await waitFor(() => {
      expect(mockedSetAccessToken).toHaveBeenCalledWith("test-access-token");
    });
  });

  it("displays the API error when login fails", async () => {
    mockedApiClient.mockRejectedValue(new Error("Invalid email or password"));

    renderLogin();

    fireEvent.change(screen.getByLabelText("Email"), {
      target: {
        value: "manager@example.com",
      },
    });

    fireEvent.change(screen.getByLabelText("Password"), {
      target: {
        value: "wrong-password",
      },
    });

    fireEvent.click(
      screen.getByRole("button", {
        name: "Sign In",
      }),
    );

    const error = await screen.findByText("Invalid email or password");

    expect(error).toBeTruthy();
  });
});
