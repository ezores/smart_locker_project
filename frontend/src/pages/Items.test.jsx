import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import Items from "./Items";
import { LanguageProvider } from "../contexts/LanguageContext";
import { DarkModeProvider } from "../contexts/DarkModeContext";
import axios from "axios";

jest.mock("axios");

describe("Items", () => {
  it("renders items management and displays items", async () => {
    axios.get.mockImplementation((url) => {
      if (url.includes("/api/items")) {
        return Promise.resolve({
          data: [
            { id: 1, name: "Laptop", locker_id: 1 },
            { id: 2, name: "Tablet", locker_id: 2 },
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
          <Items />
        </DarkModeProvider>
      </LanguageProvider>
    );
    await waitFor(() => {
      expect(screen.getByText("Laptop")).toBeInTheDocument();
      expect(screen.getByText("Tablet")).toBeInTheDocument();
    });
  });
});
