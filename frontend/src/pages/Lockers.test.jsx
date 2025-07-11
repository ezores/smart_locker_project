import { render, screen, waitFor } from "@testing-library/react";
import Lockers from "./Lockers";
import { LanguageProvider } from "../contexts/LanguageContext";
import { DarkModeProvider } from "../contexts/DarkModeContext";
import axios from "axios";

jest.mock("axios");

describe("Lockers", () => {
  it("renders lockers management and displays lockers", async () => {
    axios.get.mockImplementation((url) => {
      if (url.includes("/api/lockers")) {
        return Promise.resolve({
          data: [
            { id: 1, name: "Locker 1", location: "A", status: "available" },
            { id: 2, name: "Locker 2", location: "B", status: "occupied" },
          ],
        });
      }
      if (url.includes("/api/items")) {
        return Promise.resolve({ data: [] });
      }
      return Promise.resolve({ data: [] });
    });
    render(
      <LanguageProvider>
        <DarkModeProvider>
          <Lockers />
        </DarkModeProvider>
      </LanguageProvider>
    );
    await waitFor(() => {
      expect(screen.getByText("Locker 1")).toBeInTheDocument();
      expect(screen.getByText("Locker 2")).toBeInTheDocument();
    });
  });
});
