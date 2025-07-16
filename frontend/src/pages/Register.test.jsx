import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import Register from "./Register";
import { LanguageProvider } from "../contexts/LanguageContext";
import { DarkModeProvider } from "../contexts/DarkModeContext";
import * as api from "../utils/api";

// Mock the API module
jest.mock("../utils/api");

// Mock react-router-dom
const mockNavigate = jest.fn();
jest.mock("react-router-dom", () => ({
  ...jest.requireActual("react-router-dom"),
  useNavigate: () => mockNavigate,
}));

// Mock translations
const mockTranslations = {
  create_account: "Create Account",
  register_description: "Create your account to get started",
  username: "Username",
  username_placeholder: "Enter your username",
  email: "Email",
  email_placeholder: "Enter your email",
  first_name: "First Name",
  first_name_placeholder: "Enter your first name",
  last_name: "Last Name",
  last_name_placeholder: "Enter your last name",
  student_id: "Student ID",
  student_id_placeholder: "Enter your 10-digit student ID",
  password: "Password",
  password_placeholder: "Enter your password",
  confirm_password: "Confirm Password",
  confirm_password_placeholder: "Confirm your password",
  register: "Register",
  already_have_account: "Already have an account?",
  sign_in: "Sign in",
  generate_test_id: "Generate Test ID",
  scan_card_description: "Or scan your student card",
  password_requirements: "Password Requirements:",
  min_8_characters: "At least 8 characters",
  one_uppercase: "One uppercase letter",
  one_lowercase: "One lowercase letter",
  one_number: "One number",
  one_special: "One special character",
  all_fields_required: "All fields are required",
  passwords_dont_match: "Passwords don't match",
  password_requirements_not_met: "Password requirements not met",
  invalid_email: "Invalid email address",
  registration_successful: "Registration successful! Please log in.",
  registration_failed: "Registration failed. Please try again.",
};

// Mock the language context
jest.mock("../contexts/LanguageContext", () => ({
  ...jest.requireActual("../contexts/LanguageContext"),
  useLanguage: () => ({
    t: (key) => mockTranslations[key] || key,
    currentLanguage: "en",
    changeLanguage: jest.fn(),
    availableLanguages: ["en", "fr", "es", "tr"],
  }),
}));

// Mock the dark mode context
jest.mock("../contexts/DarkModeContext", () => ({
  ...jest.requireActual("../contexts/DarkModeContext"),
  useDarkMode: () => ({
    isDarkMode: false,
  }),
}));

const renderRegister = () => {
  return render(
    <BrowserRouter>
      <LanguageProvider>
        <DarkModeProvider>
          <Register />
        </DarkModeProvider>
      </LanguageProvider>
    </BrowserRouter>
  );
};

describe("Register Component", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockNavigate.mockClear();
  });

  describe("UI Elements", () => {
    test("renders all form fields with icons", () => {
      renderRegister();

      // Check for form fields with icons
      expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/first name/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/last name/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/student id/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/^password$/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/confirm password/i)).toBeInTheDocument();

      // Check for icons (using aria-describedby attributes)
      expect(screen.getByLabelText(/username/i)).toHaveAttribute(
        "aria-describedby",
        "username-icon"
      );
      expect(screen.getByLabelText(/email/i)).toHaveAttribute(
        "aria-describedby",
        "email-icon"
      );
      expect(screen.getByLabelText(/first name/i)).toHaveAttribute(
        "aria-describedby",
        "first-name-icon"
      );
      expect(screen.getByLabelText(/last name/i)).toHaveAttribute(
        "aria-describedby",
        "last-name-icon"
      );
      expect(screen.getByLabelText(/student id/i)).toHaveAttribute(
        "aria-describedby",
        "student-id-icon"
      );
      expect(screen.getByLabelText(/^password$/i)).toHaveAttribute(
        "aria-describedby",
        "password-icon password-toggle"
      );
      expect(screen.getByLabelText(/confirm password/i)).toHaveAttribute(
        "aria-describedby",
        "confirm-password-icon confirm-password-toggle"
      );
    });

    test("renders language selector in top-right corner", () => {
      renderRegister();

      const languageButton = screen.getByLabelText(/current language/i);
      expect(languageButton).toBeInTheDocument();
      expect(languageButton.closest("div")).toHaveClass(
        "fixed",
        "top-4",
        "right-4"
      );
    });

    test("renders password strength indicators", () => {
      renderRegister();

      expect(screen.getByText("Password Requirements:")).toBeInTheDocument();
      expect(screen.getByText("At least 8 characters")).toBeInTheDocument();
      expect(screen.getByText("One uppercase letter")).toBeInTheDocument();
      expect(screen.getByText("One lowercase letter")).toBeInTheDocument();
      expect(screen.getByText("One number")).toBeInTheDocument();
      expect(screen.getByText("One special character")).toBeInTheDocument();
    });

    test("renders show/hide password buttons", () => {
      renderRegister();

      const passwordToggle = screen.getByLabelText("Show password");
      const confirmPasswordToggle = screen.getByLabelText(
        "Show confirm password"
      );

      expect(passwordToggle).toBeInTheDocument();
      expect(confirmPasswordToggle).toBeInTheDocument();
    });

    test("renders generate test student ID button", () => {
      renderRegister();

      const generateButton = screen.getByText("Generate Test ID");
      expect(generateButton).toBeInTheDocument();
      expect(generateButton).toHaveClass("inline-flex", "items-center");
    });
  });

  describe("Form Validation", () => {
    test("shows error for empty required fields", async () => {
      renderRegister();

      const submitButton = screen.getByRole("button", { name: /register/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(
          screen.getByTestId("register-error-message")
        ).toBeInTheDocument();
      });

      // Check for error message (be flexible with the exact text)
      const errorMessage = screen.getByTestId("register-error-message");
      expect(errorMessage).toHaveTextContent(/required|fields/i);
    });

    test("shows error for invalid email format", async () => {
      renderRegister();

      const emailInput = screen.getByLabelText(/email/i);
      const submitButton = screen.getByRole("button", { name: /register/i });

      fireEvent.change(emailInput, { target: { value: "invalid-email" } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(
          screen.getByTestId("register-error-message")
        ).toBeInTheDocument();
      });

      const errorMessage = screen.getByTestId("register-error-message");
      expect(errorMessage).toHaveTextContent(/email|invalid/i);
    });

    test("shows error for non-matching passwords", async () => {
      renderRegister();

      const passwordInput = screen.getByLabelText(/^password$/i);
      const confirmPasswordInput = screen.getByLabelText("Confirm Password");
      const submitButton = screen.getByRole("button", { name: /register/i });

      fireEvent.change(passwordInput, { target: { value: "Password123!" } });
      fireEvent.change(confirmPasswordInput, {
        target: { value: "DifferentPassword123!" },
      });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(
          screen.getByTestId("register-error-message")
        ).toBeInTheDocument();
      });

      const errorMessage = screen.getByTestId("register-error-message");
      expect(errorMessage).toHaveTextContent(/password|match/i);
    });

    test("shows error for weak password", async () => {
      renderRegister();

      const passwordInput = screen.getByLabelText(/^password$/i);
      const submitButton = screen.getByRole("button", { name: /register/i });

      // Use a truly weak password that fails multiple requirements
      fireEvent.change(passwordInput, { target: { value: "weak" } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(
          screen.getByTestId("register-error-message")
        ).toBeInTheDocument();
      });

      const errorMessage = screen.getByTestId("register-error-message");
      expect(errorMessage).toHaveTextContent(/password|requirements/i);
    });
  });

  describe("Password Strength Indicators", () => {
    test("updates password strength indicators correctly", () => {
      renderRegister();

      const passwordInput = screen.getByLabelText(/^password$/i);

      // Start with weak password
      fireEvent.change(passwordInput, { target: { value: "weak" } });

      // Check that some indicators show as failed
      const xCircles = screen.getAllByTestId("x-circle");
      expect(xCircles.length).toBeGreaterThan(0);

      // Change to strong password
      fireEvent.change(passwordInput, {
        target: { value: "StrongPassword123!" },
      });

      // Check that all indicators show as passed
      const checkCircles = screen.getAllByTestId("check-circle");
      expect(checkCircles.length).toBeGreaterThan(0);
    });

    test("shows correct indicators for partial password strength", () => {
      renderRegister();

      const passwordInput = screen.getByLabelText(/^password$/i);

      // Password with some requirements met
      fireEvent.change(passwordInput, { target: { value: "Password123" } });

      // Should show some check circles and some x circles
      const checkCircles = screen.getAllByTestId("check-circle");
      const xCircles = screen.getAllByTestId("x-circle");

      expect(checkCircles.length).toBeGreaterThan(0);
      expect(xCircles.length).toBeGreaterThan(0);
    });
  });

  describe("Student ID Generation", () => {
    test("generates 10-digit student ID when button is clicked", () => {
      renderRegister();

      const generateButton = screen.getByText("Generate Test ID");
      const studentIdInput = screen.getByLabelText(/student id/i);

      fireEvent.click(generateButton);

      const generatedId = studentIdInput.value;
      expect(generatedId).toMatch(/^\d{10}$/);
    });

    test("generated student ID is unique on multiple clicks", () => {
      renderRegister();

      const generateButton = screen.getByText("Generate Test ID");
      const studentIdInput = screen.getByLabelText(/student id/i);

      fireEvent.click(generateButton);
      const firstId = studentIdInput.value;

      fireEvent.click(generateButton);
      const secondId = studentIdInput.value;

      // IDs should be different (though there's a small chance they could be the same)
      expect(firstId).not.toBe(secondId);
    });
  });

  describe("Password Visibility Toggle", () => {
    test("toggles password visibility", () => {
      renderRegister();

      const passwordInput = screen.getByLabelText(/^password$/i);
      const passwordToggle = screen.getByLabelText("Show password");

      // Initially password should be hidden
      expect(passwordInput).toHaveAttribute("type", "password");

      // Click toggle to show password
      fireEvent.click(passwordToggle);
      expect(passwordInput).toHaveAttribute("type", "text");
      expect(passwordToggle).toHaveAttribute("aria-label", "Hide password");

      // Click toggle to hide password again
      fireEvent.click(passwordToggle);
      expect(passwordInput).toHaveAttribute("type", "password");
      expect(passwordToggle).toHaveAttribute("aria-label", "Show password");
    });

    test("toggles confirm password visibility", () => {
      renderRegister();

      const confirmPasswordInput = screen.getByLabelText("Confirm Password");
      const confirmPasswordToggle = screen.getByLabelText(
        "Show confirm password"
      );

      // Initially password should be hidden
      expect(confirmPasswordInput).toHaveAttribute("type", "password");

      // Click toggle to show password
      fireEvent.click(confirmPasswordToggle);
      expect(confirmPasswordInput).toHaveAttribute("type", "text");
      expect(confirmPasswordToggle).toHaveAttribute(
        "aria-label",
        "Hide confirm password"
      );

      // Click toggle to hide password again
      fireEvent.click(confirmPasswordToggle);
      expect(confirmPasswordInput).toHaveAttribute("type", "password");
      expect(confirmPasswordToggle).toHaveAttribute(
        "aria-label",
        "Show confirm password"
      );
    });
  });

  describe("Successful Registration", () => {
    test("submits form with valid data", async () => {
      const mockRegister = jest
        .fn()
        .mockResolvedValue({ data: { message: "Success" } });
      api.register = mockRegister;

      renderRegister();

      // Fill form with valid data
      fireEvent.change(screen.getByLabelText(/username/i), {
        target: { value: "testuser" },
      });
      fireEvent.change(screen.getByLabelText(/email/i), {
        target: { value: "test@example.com" },
      });
      fireEvent.change(screen.getByLabelText(/first name/i), {
        target: { value: "Test" },
      });
      fireEvent.change(screen.getByLabelText(/last name/i), {
        target: { value: "User" },
      });
      fireEvent.change(screen.getByLabelText(/student id/i), {
        target: { value: "1234567890" },
      });
      fireEvent.change(screen.getByLabelText(/^password$/i), {
        target: { value: "StrongPassword123!" },
      });
      fireEvent.change(screen.getByLabelText("Confirm Password"), {
        target: { value: "StrongPassword123!" },
      });

      const submitButton = screen.getByRole("button", { name: /register/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(mockRegister).toHaveBeenCalledWith({
          username: "testuser",
          email: "test@example.com",
          password: "StrongPassword123!",
          first_name: "Test",
          last_name: "User",
          student_id: "1234567890",
          role: "student",
        });
      });
    });

    test("shows success message and redirects after successful registration", async () => {
      const mockRegister = jest
        .fn()
        .mockResolvedValue({ data: { message: "Success" } });
      api.register = mockRegister;

      renderRegister();

      // Fill form with valid data
      fireEvent.change(screen.getByLabelText(/username/i), {
        target: { value: "testuser" },
      });
      fireEvent.change(screen.getByLabelText(/email/i), {
        target: { value: "test@example.com" },
      });
      fireEvent.change(screen.getByLabelText(/first name/i), {
        target: { value: "Test" },
      });
      fireEvent.change(screen.getByLabelText(/last name/i), {
        target: { value: "User" },
      });
      fireEvent.change(screen.getByLabelText(/student id/i), {
        target: { value: "1234567890" },
      });
      fireEvent.change(screen.getByLabelText(/^password$/i), {
        target: { value: "StrongPassword123!" },
      });
      fireEvent.change(screen.getByLabelText("Confirm Password"), {
        target: { value: "StrongPassword123!" },
      });

      const submitButton = screen.getByRole("button", { name: /register/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(
          screen.getByText(/registration successful/i)
        ).toBeInTheDocument();
      });

      // Wait for redirect
      await waitFor(
        () => {
          expect(mockNavigate).toHaveBeenCalledWith("/login");
        },
        { timeout: 3000 }
      );
    });
  });

  describe("Error Handling", () => {
    test("displays API error messages", async () => {
      const mockRegister = jest.fn().mockRejectedValue({
        response: { data: { error: "Username already exists" } },
      });
      api.register = mockRegister;

      renderRegister();

      // Fill form with valid data
      fireEvent.change(screen.getByLabelText(/username/i), {
        target: { value: "testuser" },
      });
      fireEvent.change(screen.getByLabelText(/email/i), {
        target: { value: "test@example.com" },
      });
      fireEvent.change(screen.getByLabelText(/first name/i), {
        target: { value: "Test" },
      });
      fireEvent.change(screen.getByLabelText(/last name/i), {
        target: { value: "User" },
      });
      fireEvent.change(screen.getByLabelText(/student id/i), {
        target: { value: "1234567890" },
      });
      fireEvent.change(screen.getByLabelText(/^password$/i), {
        target: { value: "StrongPassword123!" },
      });
      fireEvent.change(screen.getByLabelText("Confirm Password"), {
        target: { value: "StrongPassword123!" },
      });

      const submitButton = screen.getByRole("button", { name: /register/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(
          screen.getByTestId("register-error-message")
        ).toBeInTheDocument();
        expect(screen.getByText("Username already exists")).toBeInTheDocument();
      });
    });

    test("displays generic error for network failures", async () => {
      const mockRegister = jest
        .fn()
        .mockRejectedValue(new Error("Network error"));
      api.register = mockRegister;

      renderRegister();

      // Fill form with valid data
      fireEvent.change(screen.getByLabelText(/username/i), {
        target: { value: "testuser" },
      });
      fireEvent.change(screen.getByLabelText(/email/i), {
        target: { value: "test@example.com" },
      });
      fireEvent.change(screen.getByLabelText(/first name/i), {
        target: { value: "Test" },
      });
      fireEvent.change(screen.getByLabelText(/last name/i), {
        target: { value: "User" },
      });
      fireEvent.change(screen.getByLabelText(/student id/i), {
        target: { value: "1234567890" },
      });
      fireEvent.change(screen.getByLabelText(/^password$/i), {
        target: { value: "StrongPassword123!" },
      });
      fireEvent.change(screen.getByLabelText("Confirm Password"), {
        target: { value: "StrongPassword123!" },
      });

      const submitButton = screen.getByRole("button", { name: /register/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(
          screen.getByTestId("register-error-message")
        ).toBeInTheDocument();
        expect(screen.getByText(/registration failed/i)).toBeInTheDocument();
      });
    });
  });

  describe("Accessibility", () => {
    test("has proper ARIA labels and descriptions", () => {
      renderRegister();

      // Check for proper ARIA attributes
      expect(screen.getByLabelText(/username/i)).toHaveAttribute(
        "aria-describedby",
        "username-icon"
      );
      expect(screen.getByLabelText(/email/i)).toHaveAttribute(
        "aria-describedby",
        "email-icon"
      );
      expect(screen.getByLabelText(/first name/i)).toHaveAttribute(
        "aria-describedby",
        "first-name-icon"
      );
      expect(screen.getByLabelText(/last name/i)).toHaveAttribute(
        "aria-describedby",
        "last-name-icon"
      );
      expect(screen.getByLabelText(/student id/i)).toHaveAttribute(
        "aria-describedby",
        "student-id-icon"
      );
      expect(screen.getByLabelText(/^password$/i)).toHaveAttribute(
        "aria-describedby",
        "password-icon password-toggle"
      );
      expect(screen.getByLabelText("Confirm Password")).toHaveAttribute(
        "aria-describedby",
        "confirm-password-icon confirm-password-toggle"
      );
    });

    test("password toggle buttons have proper aria-labels", () => {
      renderRegister();

      const passwordToggle = screen.getByLabelText("Show password");
      const confirmPasswordToggle = screen.getByLabelText(
        "Show confirm password"
      );

      expect(passwordToggle).toHaveAttribute("aria-label", "Show password");
      expect(confirmPasswordToggle).toHaveAttribute(
        "aria-label",
        "Show confirm password"
      );
    });

    test("language selector has proper aria-label", () => {
      renderRegister();

      const languageButton = screen.getByLabelText(/current language/i);
      expect(languageButton).toHaveAttribute(
        "aria-label",
        "Current language: English"
      );
    });
  });

  describe("Navigation", () => {
    test("has link to login page", () => {
      renderRegister();

      const loginLink = screen.getByRole("link", { name: /sign in/i });
      expect(loginLink).toBeInTheDocument();
      expect(loginLink).toHaveAttribute("href", "/login");
    });
  });

  describe("Loading States", () => {
    test("shows loading spinner during form submission", async () => {
      const mockRegister = jest
        .fn()
        .mockImplementation(
          () => new Promise((resolve) => setTimeout(resolve, 100))
        );
      api.register = mockRegister;

      renderRegister();

      // Fill form with valid data
      fireEvent.change(screen.getByLabelText(/username/i), {
        target: { value: "testuser" },
      });
      fireEvent.change(screen.getByLabelText(/email/i), {
        target: { value: "test@example.com" },
      });
      fireEvent.change(screen.getByLabelText(/first name/i), {
        target: { value: "Test" },
      });
      fireEvent.change(screen.getByLabelText(/last name/i), {
        target: { value: "User" },
      });
      fireEvent.change(screen.getByLabelText(/student id/i), {
        target: { value: "1234567890" },
      });
      fireEvent.change(screen.getByLabelText(/^password$/i), {
        target: { value: "StrongPassword123!" },
      });
      fireEvent.change(screen.getByLabelText("Confirm Password"), {
        target: { value: "StrongPassword123!" },
      });

      const submitButton = screen.getByRole("button", { name: /register/i });
      fireEvent.click(submitButton);

      // Check for loading spinner
      expect(screen.getByRole("button", { name: /register/i })).toBeDisabled();
    });
  });
});
