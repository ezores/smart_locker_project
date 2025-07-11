#!/usr/bin/env node

const puppeteer = require("puppeteer");

async function testReservations() {
  console.log("Testing Reservations Module...");

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

    // Navigate to reservations page
    await page.click('a[href="/reservations"]');
    await page.waitForSelector('h1:contains("Reservations")', {
      timeout: 10000,
    });
    console.log("Navigated to reservations page");

    // Test creating a new reservation
    await page.click('button:contains("New Reservation")');
    await page.waitForSelector('input[name="locker_id"]', { timeout: 10000 });
    console.log("New reservation modal opened");

    // Fill reservation form
    await page.select('select[name="locker_id"]', "1");
    await page.type('input[name="start_time"]', "2025-07-15T10:00");
    await page.type('input[name="end_time"]', "2025-07-16T10:00");
    await page.type(
      'input[name="notes"]',
      "Test reservation from automated test"
    );
    await page.click('button:contains("Create")');

    // Wait for success message or redirect
    await page.waitForTimeout(3000);
    console.log("Created new reservation");

    // Test editing a reservation
    const editButtons = await page.$$('button:contains("Edit")');
    if (editButtons.length > 0) {
      await editButtons[0].click();
      await page.waitForSelector('input[name="notes"]', { timeout: 10000 });
      console.log("Edit modal opened");

      // Update notes
      await page.click('input[name="notes"]', { clickCount: 3 });
      await page.type('input[name="notes"]', " - Updated by automated test");
      await page.click('button:contains("Update")');

      await page.waitForTimeout(2000);
      console.log("Updated reservation");
    }

    // Test canceling a reservation
    const cancelButtons = await page.$$('button:contains("Cancel")');
    if (cancelButtons.length > 0) {
      await cancelButtons[0].click();

      // Handle confirmation dialog if present
      try {
        await page.waitForSelector(".modal", { timeout: 3000 });
        await page.click('button:contains("Confirm")');
      } catch (e) {
        // No confirmation dialog, continue
      }

      await page.waitForTimeout(2000);
      console.log("Canceled reservation");
    }

    // Test filtering and search
    await page.type('input[placeholder*="search"]', "test");
    await page.waitForTimeout(1000);
    console.log("Tested search functionality");

    // Clear search
    await page.click('input[placeholder*="search"]', { clickCount: 3 });
    await page.keyboard.press("Backspace");

    // Test date filtering
    const dateInputs = await page.$$('input[type="date"]');
    if (dateInputs.length > 0) {
      await dateInputs[0].type("2025-07-15");
      await page.waitForTimeout(1000);
      console.log("Tested date filtering");
    }

    console.log("Reservations module tests completed successfully!");
  } catch (error) {
    console.error("Reservations test failed:", error.message);
    throw error;
  } finally {
    await browser.close();
  }
}

if (require.main === module) {
  testReservations().catch(console.error);
}

module.exports = { testReservations };
