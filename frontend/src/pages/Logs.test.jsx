import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import Logs from "./Logs";
import { LanguageProvider } from "../contexts/LanguageContext";
import { DarkModeProvider } from "../contexts/DarkModeContext";
import axios from "axios";

jest.mock("axios");

describe("Logs", () => {
  it("renders logs management and displays logs", async () => {
    axios.get.mockImplementation((url) => {
      if (url.includes("/api/logs")) {
        return Promise.resolve({
          data: [
            {
              id: 1,
              action: "borrow",
              user_id: 1,
              item_id: 1,
              locker_id: 1,
              description: "Borrowed Laptop",
              timestamp: new Date().toISOString(),
            },
            {
              id: 2,
              action: "return",
              user_id: 2,
              item_id: 2,
              locker_id: 2,
              description: "Returned Tablet",
              timestamp: new Date().toISOString(),
            },
          ],
        });
      }
      if (url.includes("/api/users")) {
        return Promise.resolve({
          data: [
            { id: 1, username: "admin" },
            { id: 2, username: "john.doe" },
          ],
        });
      }
      if (url.includes("/api/items")) {
        return Promise.resolve({
          data: [
            { id: 1, name: "Laptop" },
            { id: 2, name: "Tablet" },
          ],
        });
      }
      if (url.includes("/api/lockers")) {
        return Promise.resolve({
          data: [
            { id: 1, name: "Locker 1" },
            { id: 2, name: "Locker 2" },
          ],
        });
      }
      return Promise.resolve({ data: [] });
    });
    render(
      <LanguageProvider>
        <DarkModeProvider>
          <Logs />
        </DarkModeProvider>
      </LanguageProvider>
    );
    await waitFor(() => {
      expect(screen.getByText("Borrowed Laptop")).toBeInTheDocument();
      expect(screen.getByText("Returned Tablet")).toBeInTheDocument();
    });
  });
});
