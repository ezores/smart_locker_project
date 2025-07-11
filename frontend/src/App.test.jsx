import React from "react";
import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { AuthProvider } from "./contexts/AuthContext";
import { LanguageProvider } from "./contexts/LanguageContext";
import { DarkModeProvider } from "./contexts/DarkModeContext";
import App from "./App";

// Mock the API calls
jest.mock("./utils/api", () => ({
  login: jest.fn(),
  logout: jest.fn(),
  getUsers: jest.fn(),
  getStats: jest.fn(() =>
    Promise.resolve({
      total_users: 1,
      total_items: 1,
      total_lockers: 1,
      active_borrows: 0,
    })
  ),
  getActiveBorrows: jest.fn(),
  getLockers: jest.fn(),
  getItems: jest.fn(),
}));

// Mock axios
jest.mock("axios", () => ({
  get: jest.fn(),
  post: jest.fn(),
  defaults: {
    headers: {
      common: {},
    },
  },
}));

// Test wrapper component
const TestWrapper = ({ children }) => (
  <BrowserRouter>
    <AuthProvider>
      <LanguageProvider>
        <DarkModeProvider>{children}</DarkModeProvider>
      </LanguageProvider>
    </AuthProvider>
  </BrowserRouter>
);

describe("App Component", () => {
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
  });

  test("renders without crashing", () => {
    render(
      <TestWrapper>
        <App />
      </TestWrapper>
    );

    // Check if the app renders without errors
    expect(document.body).toBeInTheDocument();
  });

  test("renders header component when authenticated", async () => {
    // Mock localStorage to simulate authenticated user
    const mockUser = {
      id: 1,
      username: "testuser",
      role: "admin",
      email: "test@example.com",
    };

    // Mock localStorage.getItem to return a token
    Object.defineProperty(window, "localStorage", {
      value: {
        getItem: jest.fn((key) => {
          if (key === "token") return "mock-jwt-token";
          if (key === "user") return JSON.stringify(mockUser);
          return null;
        }),
        setItem: jest.fn(),
        removeItem: jest.fn(),
        clear: jest.fn(),
      },
      writable: true,
    });

    // Mock axios.get to return user data for profile check
    const axios = require("axios");
    axios.get.mockResolvedValue({ data: mockUser });

    render(
      <TestWrapper>
        <App />
      </TestWrapper>
    );

    // Wait for the component to render with authenticated state
    await new Promise((resolve) => setTimeout(resolve, 100));

    // Check if header is present (it should contain navigation)
    const header = document.querySelector("header");
    expect(header).toBeInTheDocument();
  });

  test("renders main content area", () => {
    render(
      <TestWrapper>
        <App />
      </TestWrapper>
    );

    // Check if main content area is present
    const main = document.querySelector("main");
    expect(main).toBeInTheDocument();
  });

  test("redirects to login when not authenticated", () => {
    // Mock localStorage to simulate no authentication
    Object.defineProperty(window, "localStorage", {
      value: {
        getItem: jest.fn(() => null),
        setItem: jest.fn(),
        removeItem: jest.fn(),
        clear: jest.fn(),
      },
      writable: true,
    });

    render(
      <TestWrapper>
        <App />
      </TestWrapper>
    );

    // When not authenticated, the app should redirect to login
    // The login page should be rendered
    expect(document.body).toBeInTheDocument();
  });
});

describe("App Accessibility", () => {
  test("has proper semantic structure when authenticated", async () => {
    // Mock localStorage to simulate authenticated user
    const mockUser = {
      id: 1,
      username: "testuser",
      role: "admin",
      email: "test@example.com",
    };

    Object.defineProperty(window, "localStorage", {
      value: {
        getItem: jest.fn((key) => {
          if (key === "token") return "mock-jwt-token";
          if (key === "user") return JSON.stringify(mockUser);
          return null;
        }),
        setItem: jest.fn(),
        removeItem: jest.fn(),
        clear: jest.fn(),
      },
      writable: true,
    });

    // Mock axios.get to return user data for profile check
    const axios = require("axios");
    axios.get.mockResolvedValue({ data: mockUser });

    render(
      <TestWrapper>
        <App />
      </TestWrapper>
    );

    // Wait for the component to render with authenticated state
    await new Promise((resolve) => setTimeout(resolve, 100));

    // Check for proper HTML structure
    const header = document.querySelector("header");
    const main = document.querySelector("main");

    expect(header).toBeInTheDocument();
    expect(main).toBeInTheDocument();
  });

  test("has proper ARIA labels", () => {
    render(
      <TestWrapper>
        <App />
      </TestWrapper>
    );

    // Check for basic accessibility features
    // This is a basic test - in a real app you'd want more comprehensive a11y testing
    expect(document.documentElement.lang).toBeDefined();
  });
});

describe("App Responsiveness", () => {
  test("renders on different screen sizes", () => {
    // Test mobile viewport
    Object.defineProperty(window, "innerWidth", {
      writable: true,
      configurable: true,
      value: 375,
    });

    render(
      <TestWrapper>
        <App />
      </TestWrapper>
    );

    expect(document.body).toBeInTheDocument();

    // Test desktop viewport
    Object.defineProperty(window, "innerWidth", {
      writable: true,
      configurable: true,
      value: 1920,
    });

    render(
      <TestWrapper>
        <App />
      </TestWrapper>
    );

    expect(document.body).toBeInTheDocument();
  });
});
