#!/usr/bin/env node

const puppeteer = require("puppeteer");

async function testAuthFlow() {
  console.log("Testing Authentication Flow...");

  const browser = await puppeteer.launch({
    headless: "new",
    defaultViewport: null,
    args: ["--start-maximized"],
  });

  try {
    const page = await browser.newPage();

    // Navigate to the frontend
    await page.goto("http://localhost:5173");
    console.log("Loaded frontend page");

    // Wait for the login form to appear
    await page.waitForSelector('input[name="username"]', { timeout: 10000 });
    console.log("Login form found");

    // Test invalid login
    await page.type('input[name="username"]', "invalid_user");
    await page.type('input[name="password"]', "wrong_password");
    await page.click('button[type="submit"]');

    // Wait for error message
    await new Promise((resolve) => setTimeout(resolve, 2000));
    console.log("Tested invalid login");

    // Clear form and test valid login
    await page.click('input[name="username"]', { clickCount: 3 });
    await page.type('input[name="username"]', "admin");
    await page.click('input[name="password"]', { clickCount: 3 });
    await page.type('input[name="password"]', "admin123");
    await page.click('button[type="submit"]');

    // Wait for redirect to main menu - use XPath instead of :contains
    await page.waitForSelector("xpath///h1[contains(text(), 'Main Menu')]", {
      timeout: 10000,
    });
    console.log("Login successful");

    // Test session persistence by refreshing page
    await page.reload();
    await page.waitForSelector("xpath///h1[contains(text(), 'Main Menu')]", {
      timeout: 10000,
    });
    console.log("Session persistence verified");

    // Test logout
    await page.waitForSelector("xpath///button[contains(text(), 'Logout')]", {
      timeout: 5000,
    });
    await page.click('button:contains("Logout")');
    await page.waitForSelector('input[name="username"]', { timeout: 10000 });
    console.log("Logout successful");

    // Test that we can't access protected pages after logout
    await page.goto("http://localhost:5173/reservations");
    await page.waitForSelector('input[name="username"]', { timeout: 10000 });
    console.log("Protected route redirect after logout");

    console.log("Authentication flow tests completed successfully!");
  } catch (error) {
    console.error("Authentication flow test failed:", error.message);
    throw error;
  } finally {
    await browser.close();
  }
}

if (require.main === module) {
  testAuthFlow().catch(console.error);
}

module.exports = { testAuthFlow };
