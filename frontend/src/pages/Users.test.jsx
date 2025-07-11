import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import Users from "./Users";
import { LanguageProvider } from "../contexts/LanguageContext";
import { DarkModeProvider } from "../contexts/DarkModeContext";
import axios from "axios";

jest.mock("axios");

describe("Users", () => {
  it("renders user management and displays users", async () => {
    axios.get.mockImplementation((url) => {
      if (url.includes("/api/admin/users")) {
        return Promise.resolve({
          data: [
            { id: 1, username: "admin", role: "admin" },
            { id: 2, username: "john.doe", role: "student" },
          ],
        });
      }
      return Promise.resolve({ data: [] });
    });
    render(
      <LanguageProvider>
        <DarkModeProvider>
          <Users />
        </DarkModeProvider>
      </LanguageProvider>
    );
    await waitFor(() => {
      expect(screen.getByText("admin")).toBeInTheDocument();
      expect(screen.getByText("john.doe")).toBeInTheDocument();
    });
  });
});
