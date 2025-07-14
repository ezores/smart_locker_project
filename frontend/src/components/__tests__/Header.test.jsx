import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import Header from "../Header";

// Mock the AuthContext
jest.mock("../../contexts/AuthContext", () => ({
  useAuth: () => ({
    user: { username: "testuser", role: "user" },
    logout: jest.fn(),
  }),
}));

// Mock the LanguageContext
jest.mock("../../contexts/LanguageContext", () => ({
  useLanguage: () => ({
    t: (key) => key,
    currentLanguage: "en",
    setLanguage: jest.fn(),
  }),
}));

// Mock the DarkModeContext
jest.mock("../../contexts/DarkModeContext", () => ({
  useDarkMode: () => ({
    isDarkMode: false,
    toggleDarkMode: jest.fn(),
  }),
}));

const renderWithRouter = (component) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe("Header Component", () => {
  test("renders header with logo", () => {
    renderWithRouter(<Header />);

    // Check if the header contains the logo
    const logo = screen.getByAltText(/logo/i);
    expect(logo).toBeInTheDocument();
  });

  test("renders navigation menu", () => {
    renderWithRouter(<Header />);

    // Check if the hamburger menu button is present by class
    const buttons = screen.getAllByRole("button");
    // The last button in the header is the hamburger menu
    expect(buttons[buttons.length - 1]).toBeInTheDocument();
  });

  test("renders user information", () => {
    renderWithRouter(<Header />);

    // Check if user info is displayed
    expect(screen.getByText("testuser")).toBeInTheDocument();
  });
});
