/**
 * Smart Locker System - MainMenu Component Tests
 *
 * @author Alp
 * @date 2024-12-XX
 * @description Tests for MainMenu component functionality
 */

import { render, screen, waitFor } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { AuthProvider } from "../contexts/AuthContext";
import { LanguageProvider } from "../contexts/LanguageContext";
import { DarkModeProvider } from "../contexts/DarkModeContext";
import MainMenu from "./MainMenu";

// Mock the AuthContext
jest.mock("../contexts/AuthContext", () => ({
  useAuth: () => ({
    user: {
      username: "admin",
      role: "admin",
    },
  }),
}));

// Mock the API functions
jest.mock("../utils/api", () => ({
  getStats: jest.fn(),
}));

const mockGetStats = require("../utils/api").getStats;

const renderWithProviders = (component) => {
  return render(
    <BrowserRouter>
      <DarkModeProvider>
        <LanguageProvider>
          <AuthProvider>{component}</AuthProvider>
        </LanguageProvider>
      </DarkModeProvider>
    </BrowserRouter>
  );
};

describe("MainMenu Component", () => {
  beforeEach(() => {
    // Reset all mocks before each test
    jest.clearAllMocks();
  });

  test("renders welcome message for admin user", async () => {
    // Mock admin user
    const mockUser = {
      username: "admin",
      role: "admin",
    };

    // Mock successful API response
    mockGetStats.mockResolvedValue({
      total_users: 54,
      total_items: 101,
      total_lockers: 40,
      active_borrows: 40,
    });

    renderWithProviders(<MainMenu />);

    // Wait for the component to load and API call to complete
    await waitFor(() => {
      expect(screen.getByText(/Welcome, admin!/i)).toBeInTheDocument();
    });

    // Check that stats are displayed
    await waitFor(() => {
      expect(screen.getByText("54")).toBeInTheDocument(); // Total Users
      expect(screen.getByText("101")).toBeInTheDocument(); // Total Items
      expect(screen.getByText("40")).toBeInTheDocument(); // Total Lockers & Active Borrows
    });
  });

  test("renders menu items for admin user", async () => {
    const mockUser = {
      username: "admin",
      role: "admin",
    };

    mockGetStats.mockResolvedValue({
      total_users: 54,
      total_items: 101,
      total_lockers: 40,
      active_borrows: 40,
    });

    renderWithProviders(<MainMenu />);

    await waitFor(() => {
      // Check for admin-specific menu items
      expect(screen.getByText(/borrow item/i)).toBeInTheDocument();
      expect(screen.getByText(/return item/i)).toBeInTheDocument();
      expect(screen.getByText(/admin panel/i)).toBeInTheDocument();
      expect(screen.getByText(/users/i)).toBeInTheDocument();
      expect(screen.getByText(/items/i)).toBeInTheDocument();
      expect(screen.getByText(/lockers/i)).toBeInTheDocument();
      expect(screen.getByText(/logs/i)).toBeInTheDocument();
      expect(screen.getByText(/active borrows/i)).toBeInTheDocument();
      expect(screen.getByText(/payments/i)).toBeInTheDocument();
    });
  });

  test("handles API error gracefully", async () => {
    const mockUser = {
      username: "admin",
      role: "admin",
    };

    // Mock API error
    mockGetStats.mockRejectedValue(new Error("API Error"));

    renderWithProviders(<MainMenu />);

    // Should still render the component even if API fails
    await waitFor(() => {
      expect(screen.getByText(/Welcome, admin!/i)).toBeInTheDocument();
    });

    // Stats should show 0 when API fails
    await waitFor(() => {
      expect(screen.getByText("0")).toBeInTheDocument(); // Default values
    });
  });

  test("does not show admin stats for non-admin user", async () => {
    const mockUser = {
      username: "student",
      role: "student",
    };

    renderWithProviders(<MainMenu />);

    await waitFor(() => {
      expect(screen.getByText(/Welcome, student!/i)).toBeInTheDocument();
    });

    // Should not show admin stats section
    expect(screen.queryByText(/quick overview/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/total users/i)).not.toBeInTheDocument();
  });
});
