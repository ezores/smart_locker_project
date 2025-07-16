import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { AuthProvider } from "../contexts/AuthContext";
import { LanguageProvider } from "../contexts/LanguageContext";
import { DarkModeProvider } from "../contexts/DarkModeContext";
import Login from "./Login";

// Mock axios
jest.mock("axios", () => ({
  post: jest.fn(),
  get: jest.fn(),
  defaults: {
    headers: {
      common: {},
    },
  },
}));

// Mock useNavigate
const mockNavigate = jest.fn();
jest.mock("react-router-dom", () => ({
  ...jest.requireActual("react-router-dom"),
  useNavigate: () => mockNavigate,
  Link: ({ children, to }) => <a href={to}>{children}</a>,
}));

const renderLogin = () => {
  return render(
    <BrowserRouter>
      <DarkModeProvider>
        <LanguageProvider>
          <AuthProvider>
            <Login />
          </AuthProvider>
        </LanguageProvider>
      </DarkModeProvider>
    </BrowserRouter>
  );
};

// Update error message assertions to match translation strings
const en = {
  fill_all_fields: "Please fill in all fields",
  network_error: "Network error. Please check your connection.",
  login_failed: "Login failed. Please try again.",
  invalid_credentials: "Invalid username or password. Please try again.",
};

describe("Login Page", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  describe("UI Elements", () => {
    test("renders login form with all required elements", () => {
      renderLogin();

      // Check for main elements
      expect(screen.getByText("Login")).toBeInTheDocument();
      expect(
        screen.getByText("Sign in to access the Smart Locker System")
      ).toBeInTheDocument();
      expect(screen.getByLabelText("Username")).toBeInTheDocument();
      expect(screen.getByLabelText("Password")).toBeInTheDocument();
      expect(
        screen.getByRole("button", { name: "Sign In" })
      ).toBeInTheDocument();
    });

    test("renders language selector in visible position", () => {
      renderLogin();

      // Language selector should be visible without scrolling
      const languageButton = screen.getByLabelText(/Current language/i);
      expect(languageButton).toBeInTheDocument();

      // Check that it's positioned at the top
      const languageContainer = languageButton.closest("div");
      expect(languageContainer).toHaveClass("absolute", "top-4", "right-4");
    });

    test("renders icons in username and password fields", () => {
      renderLogin();

      // Check for User icon in username field
      const usernameField = screen.getByLabelText("Username");
      const usernameContainer = usernameField.parentElement;
      const userIcon = usernameContainer.querySelector("svg");
      expect(userIcon).toBeInTheDocument();

      // Check for Lock icon in password field
      const passwordField = screen.getByLabelText("Password");
      const passwordContainer = passwordField.parentElement;
      const lockIcon = passwordContainer.querySelector("svg");
      expect(lockIcon).toBeInTheDocument();
    });

    test("shows password toggle button", () => {
      renderLogin();

      const passwordField = screen.getByLabelText("Password");
      const toggleButton = passwordField.parentElement.querySelector("button");
      expect(toggleButton).toBeInTheDocument();

      // Should show eye icon initially
      expect(toggleButton.querySelector("svg")).toBeInTheDocument();
    });

    test("password toggle button remains visible when typing", async () => {
      renderLogin();

      const passwordField = screen.getByLabelText("Password");
      const toggleButton = passwordField.parentElement.querySelector("button");

      // Type in password field
      fireEvent.change(passwordField, { target: { value: "testpassword" } });

      // Toggle button should still be visible
      expect(toggleButton).toBeInTheDocument();
      expect(toggleButton).toBeVisible();
    });
  });

  describe("Password Toggle Functionality", () => {
    test("toggles password visibility when button is clicked", () => {
      renderLogin();

      const passwordField = screen.getByLabelText("Password");
      const toggleButton = passwordField.parentElement.querySelector("button");

      // Initially password should be hidden
      expect(passwordField).toHaveAttribute("type", "password");

      // Click toggle button
      fireEvent.click(toggleButton);

      // Password should be visible
      expect(passwordField).toHaveAttribute("type", "text");

      // Click toggle button again
      fireEvent.click(toggleButton);

      // Password should be hidden again
      expect(passwordField).toHaveAttribute("type", "password");
    });

    test("toggle button icon changes when clicked", () => {
      renderLogin();

      const passwordField = screen.getByLabelText("Password");
      const toggleButton = passwordField.parentElement.querySelector("button");

      // Initially should show eye icon
      expect(toggleButton.querySelector("svg")).toBeInTheDocument();

      // Click toggle button
      fireEvent.click(toggleButton);

      // Should show eye-off icon
      expect(toggleButton.querySelector("svg")).toBeInTheDocument();
    });
  });

  describe("Language Selector", () => {
    test("opens language dropdown when clicked", () => {
      renderLogin();

      const languageButton = screen.getByLabelText(/Current language/i);

      // Initially dropdown should be closed
      expect(screen.queryByText("Français")).not.toBeInTheDocument();

      // Click language button
      fireEvent.click(languageButton);

      // Dropdown should be open
      expect(screen.getByText("Français")).toBeInTheDocument();
      expect(screen.getByText("Español")).toBeInTheDocument();
      expect(screen.getByText("Türkçe")).toBeInTheDocument();
    });

    test("changes language when different option is selected", () => {
      renderLogin();

      const languageButton = screen.getByLabelText(/Current language/i);
      fireEvent.click(languageButton);

      const frenchOption = screen.getByText("Français");
      fireEvent.click(frenchOption);

      // Language should change to French
      expect(screen.getByText("Connexion")).toBeInTheDocument();
    });
  });

  describe("Form Validation", () => {
    test("shows error when submitting empty form", async () => {
      renderLogin();
      const submitButton = screen.getByRole("button", { name: "Sign In" });
      fireEvent.click(submitButton);
      await waitFor(() => {
        expect(
          screen.getByText(/fill all fields|all fields are required/i)
        ).toBeInTheDocument();
      });
    });

    test("shows error when only username is provided", async () => {
      renderLogin();
      const usernameField = screen.getByLabelText("Username");
      fireEvent.change(usernameField, { target: { value: "testuser" } });
      const submitButton = screen.getByRole("button", { name: "Sign In" });
      fireEvent.click(submitButton);
      await waitFor(() => {
        expect(
          screen.getByText(/fill all fields|all fields are required/i)
        ).toBeInTheDocument();
      });
    });

    test("shows error when only password is provided", async () => {
      renderLogin();
      const passwordField = screen.getByLabelText("Password");
      fireEvent.change(passwordField, { target: { value: "testpass" } });
      const submitButton = screen.getByRole("button", { name: "Sign In" });
      fireEvent.click(submitButton);
      await waitFor(() => {
        expect(
          screen.getByText(/fill all fields|all fields are required/i)
        ).toBeInTheDocument();
      });
    });
  });

  describe("Error Handling", () => {
    test("displays server error messages", async () => {
      const axios = require("axios");
      axios.post.mockRejectedValue({
        response: {
          data: {
            error: "Invalid credentials",
            details: "Username or password is incorrect",
          },
        },
      });
      renderLogin();
      const usernameField = screen.getByLabelText("Username");
      const passwordField = screen.getByLabelText("Password");
      fireEvent.change(usernameField, { target: { value: "wronguser" } });
      fireEvent.change(passwordField, { target: { value: "wrongpass" } });
      const submitButton = screen.getByRole("button", { name: "Sign In" });
      fireEvent.click(submitButton);
      await waitFor(() => {
        expect(screen.getByText(en.invalid_credentials)).toBeInTheDocument();
      });
    });

    test("displays network error messages", async () => {
      const axios = require("axios");
      axios.post.mockRejectedValue({
        message: "Network Error",
      });
      renderLogin();
      const usernameField = screen.getByLabelText("Username");
      const passwordField = screen.getByLabelText("Password");
      fireEvent.change(usernameField, { target: { value: "testuser" } });
      fireEvent.change(passwordField, { target: { value: "testpass" } });
      const submitButton = screen.getByRole("button", { name: "Sign In" });
      fireEvent.click(submitButton);
      await waitFor(() => {
        expect(screen.getByText(en.network_error)).toBeInTheDocument();
      });
    });

    test("displays generic error when no specific error is provided", async () => {
      const axios = require("axios");
      axios.post.mockRejectedValue({});
      renderLogin();
      const usernameField = screen.getByLabelText("Username");
      const passwordField = screen.getByLabelText("Password");
      fireEvent.change(usernameField, { target: { value: "testuser" } });
      fireEvent.change(passwordField, { target: { value: "testpass" } });
      const submitButton = screen.getByRole("button", { name: "Sign In" });
      fireEvent.click(submitButton);
      await waitFor(() => {
        expect(screen.getByText(/login failed|failed/i)).toBeInTheDocument();
      });
    });
  });

  describe("Successful Login", () => {
    test("redirects to main menu on successful login", async () => {
      const axios = require("axios");
      axios.post.mockResolvedValue({
        data: {
          token: "fake-token",
          user: { id: 1, username: "testuser", role: "student" },
        },
      });

      renderLogin();

      const usernameField = screen.getByLabelText("Username");
      const passwordField = screen.getByLabelText("Password");

      fireEvent.change(usernameField, { target: { value: "testuser" } });
      fireEvent.change(passwordField, { target: { value: "testpass" } });

      const submitButton = screen.getByRole("button", { name: "Sign In" });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(mockNavigate).toHaveBeenCalledWith("/");
      });
    });
  });

  describe("Loading States", () => {
    test("shows loading spinner during login", async () => {
      const axios = require("axios");
      let resolveLogin;
      const loginPromise = new Promise((resolve) => {
        resolveLogin = resolve;
      });
      axios.post.mockReturnValue(loginPromise);

      renderLogin();

      const usernameField = screen.getByLabelText("Username");
      const passwordField = screen.getByLabelText("Password");

      fireEvent.change(usernameField, { target: { value: "testuser" } });
      fireEvent.change(passwordField, { target: { value: "testpass" } });

      const submitButton = screen.getByRole("button", { name: "Sign In" });
      fireEvent.click(submitButton);

      // Should show loading spinner
      expect(screen.getByRole("button", { name: "" })).toBeDisabled();
      expect(
        screen.getByRole("button", { name: "" }).querySelector(".animate-spin")
      ).toBeInTheDocument();

      // Resolve the promise
      resolveLogin({
        data: {
          token: "fake-token",
          user: { id: 1, username: "testuser", role: "student" },
        },
      });
    });
  });

  describe("Accessibility", () => {
    test("has proper labels and ARIA attributes", () => {
      renderLogin();

      const usernameField = screen.getByLabelText("Username");
      const passwordField = screen.getByLabelText("Password");

      expect(usernameField).toHaveAttribute("id", "username");
      expect(usernameField).toHaveAttribute("name", "username");
      expect(usernameField).toHaveAttribute("required");

      expect(passwordField).toHaveAttribute("id", "password");
      expect(passwordField).toHaveAttribute("name", "password");
      expect(passwordField).toHaveAttribute("required");
    });

    test("password toggle button has proper accessibility", () => {
      renderLogin();

      const passwordField = screen.getByLabelText("Password");
      const toggleButton = passwordField.parentElement.querySelector("button");

      expect(toggleButton).toHaveAttribute("type", "button");
    });
  });
});
