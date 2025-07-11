#!/usr/bin/env node

const puppeteer = require("puppeteer");

async function testLockers() {
  console.log("Testing Lockers Module...");

  const browser = await puppeteer.launch({
    headless: false,
    defaultViewport: null,
    args: ["--start-maximized"],
  });

  try {
    const page = await browser.newPage();

    // Login first
    await page.goto("http://localhost:5173");
    await page.waitForSelector('input[name="username"]', { timeout: 10000 });
    await page.type('input[name="username"]', "admin");
    await page.type('input[name="password"]', "admin123");
    await page.click('button[type="submit"]');
    await page.waitForSelector('h1:contains("Main Menu")', { timeout: 10000 });
    console.log("Logged in successfully");

    // Navigate to lockers page
    await page.click('a[href="/lockers"]');
    await page.waitForSelector('h1:contains("Lockers")', { timeout: 10000 });
    console.log("Navigated to lockers page");

    // Wait for lockers to load
    await page.waitForTimeout(2000);

    // Test locker status display
    const lockerCards = await page.$$(".locker-card, .bg-gray-800");
    console.log(`Found ${lockerCards.length} lockers`);

    // Test filtering by status
    const statusFilters = await page.$$(
      'button:contains("Active"), button:contains("Reserved"), button:contains("Maintenance")'
    );
    if (statusFilters.length > 0) {
      await statusFilters[0].click();
      await page.waitForTimeout(1000);
      console.log("Tested status filtering");
    }

    // Test search functionality
    const searchInput = await page.$(
      'input[placeholder*="search"], input[placeholder*="Search"]'
    );
    if (searchInput) {
      await searchInput.type("Locker 1");
      await page.waitForTimeout(1000);
      console.log("Tested search functionality");

      // Clear search
      await searchInput.click({ clickCount: 3 });
      await page.keyboard.press("Backspace");
    }

    // Test viewing locker details
    const firstLocker = await page.$(".locker-card, .bg-gray-800");
    if (firstLocker) {
      await firstLocker.click();
      await page.waitForTimeout(1000);
      console.log("Tested viewing locker details");
    }

    // Test sorting options
    const sortSelect = await page.$('select[name="sort"]');
    if (sortSelect) {
      await sortSelect.select("name");
      await page.waitForTimeout(1000);
      console.log("Tested sorting by name");

      await sortSelect.select("status");
      await page.waitForTimeout(1000);
      console.log("Tested sorting by status");
    }

    // Test pagination if present
    const paginationButtons = await page.$$(
      'button:contains("Next"), button:contains("Previous")'
    );
    if (paginationButtons.length > 0) {
      await paginationButtons[0].click();
      await page.waitForTimeout(1000);
      console.log("Tested pagination");
    }

    console.log("Lockers module tests completed successfully!");
  } catch (error) {
    console.error("Lockers test failed:", error.message);
    throw error;
  } finally {
    await browser.close();
  }
}

if (require.main === module) {
  testLockers().catch(console.error);
}

module.exports = { testLockers };
