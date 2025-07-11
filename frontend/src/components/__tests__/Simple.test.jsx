import React from "react";
import { render, screen } from "@testing-library/react";

// Simple test component
const SimpleComponent = () => {
  return <div data-testid="simple-component">Hello World</div>;
};

describe("Simple Component", () => {
  test("renders hello world", () => {
    render(<SimpleComponent />);
    expect(screen.getByTestId("simple-component")).toBeInTheDocument();
    expect(screen.getByText("Hello World")).toBeInTheDocument();
  });

  test("basic math works", () => {
    expect(2 + 2).toBe(4);
    expect(3 * 3).toBe(9);
  });

  test("string operations work", () => {
    const testString = "Smart Locker";
    expect(testString.length).toBe(12);
    expect(testString.includes("Smart")).toBe(true);
  });
});
