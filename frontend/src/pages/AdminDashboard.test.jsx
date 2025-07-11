import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import AdminDashboard from "./AdminDashboard";
import { LanguageProvider } from "../contexts/LanguageContext";
import { DarkModeProvider } from "../contexts/DarkModeContext";
import axios from "axios";

jest.mock("axios");
jest.mock("../utils/api", () => ({
  getStats: jest.fn(() =>
    Promise.resolve({
      total_users: 5,
      total_items: 10,
      total_lockers: 3,
      active_borrows: 2,
    })
  ),
  getRecentActivity: jest.fn(() => Promise.resolve([])),
}));

describe("AdminDashboard", () => {
  it("renders dashboard and displays stats", async () => {
    axios.get.mockImplementation((url) => {
      if (url.includes("/api/admin/stats")) {
        return Promise.resolve({
          data: {
            totalUsers: 5,
            totalItems: 10,
            totalLockers: 3,
            activeBorrows: 2,
          },
        });
      }
      if (url.includes("/api/admin/recent-activity")) {
        return Promise.resolve({ data: [] });
      }
      return Promise.resolve({ data: {} });
    });
    render(
      <LanguageProvider>
        <DarkModeProvider>
          <AdminDashboard />
        </DarkModeProvider>
      </LanguageProvider>
    );
    await waitFor(() => {
      expect(screen.getByText("5")).toBeInTheDocument();
      expect(screen.getByText("10")).toBeInTheDocument();
      expect(screen.getByText("3")).toBeInTheDocument();
      expect(screen.getByText("2")).toBeInTheDocument();
    });
  });
});
