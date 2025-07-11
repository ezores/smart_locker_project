/**
 * Smart Locker System - MainMenu Component Tests
 *
 * @author Alp
 * @date 2024-12-XX
 * @description Tests for MainMenu component functionality
 */

import React from "react";
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
        <LanguageProvider>{component}</LanguageProvider>
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
      expect(screen.getByText(/Welcome\s*,\s*admin\s*!/i)).toBeInTheDocument();
    });

    // Check that stats are displayed (use getByText for unique values, getAllByText for ambiguous)
    await waitFor(() => {
      expect(screen.getByText("54")).toBeInTheDocument(); // Total Users
      expect(screen.getByText("101")).toBeInTheDocument(); // Total Items
      // Both total_lockers and active_borrows are 40, so check that there are two '40's
      expect(screen.getAllByText("40").length).toBeGreaterThanOrEqual(2);
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
      // Check for admin-specific menu items (match actual rendered text)
      expect(screen.getByText(/Borrow an Item/i)).toBeInTheDocument();
      expect(screen.getByText(/Return an Item/i)).toBeInTheDocument();
      expect(screen.getByText(/Admin Panel/i)).toBeInTheDocument();
      // Use a function matcher to select the <h3> with text 'Users'
      expect(
        screen.getAllByText("Users").some((el) => el.tagName === "H3")
      ).toBe(true);
      // Use a function matcher to select the <h3> with text 'Items'
      expect(
        screen.getAllByText("Items").some((el) => el.tagName === "H3")
      ).toBe(true);
      // Use a function matcher to select the <h3> with text 'Lockers'
      expect(
        screen.getAllByText("Lockers").some((el) => el.tagName === "H3")
      ).toBe(true);
      expect(screen.getByText(/Logs/i)).toBeInTheDocument();
      // Use a function matcher to select the <h3> with text 'Active Borrows'
      expect(
        screen.getAllByText("Active Borrows").some((el) => el.tagName === "H3")
      ).toBe(true);
      // Use a function matcher to select the <h3> with text 'Payments'
      expect(
        screen.getAllByText("Payments").some((el) => el.tagName === "H3")
      ).toBe(true);
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
      expect(screen.getByText(/Welcome\s*,\s*admin\s*!/i)).toBeInTheDocument();
    });

    // Stats should show 0 when API fails (there are four '0's)
    await waitFor(() => {
      expect(screen.getAllByText("0").length).toBeGreaterThanOrEqual(4);
    });
  });

  test("does not show admin stats for non-admin user", async () => {
    // Temporarily mock useAuth to return a student user for this test
    const { useAuth } = require("../contexts/AuthContext");
    const spy = jest
      .spyOn(require("../contexts/AuthContext"), "useAuth")
      .mockImplementation(() => ({
        user: {
          username: "student",
          role: "student",
        },
      }));
    renderWithProviders(<MainMenu />);

    await waitFor(() => {
      expect(
        screen.getByText(/Welcome\s*,\s*student\s*!/i)
      ).toBeInTheDocument();
    });

    // Should not show admin stats section
    expect(screen.queryByText(/quick overview/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/total users/i)).not.toBeInTheDocument();
    spy.mockRestore();
  });
});
