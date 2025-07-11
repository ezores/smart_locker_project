#!/usr/bin/env node

const puppeteer = require("puppeteer");

async function testLockers() {
  console.log("Testing Lockers Module...");

  const browser = await puppeteer.launch({
    headless: "new",
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
    await page.waitForSelector("xpath///h1[contains(text(), 'Main Menu')]", {
      timeout: 10000,
    });
    console.log("Logged in successfully");

    // Navigate to lockers page
    await page.click('a[href="/lockers"]');
    await page.waitForSelector("xpath///h1[contains(text(), 'Lockers')]", {
      timeout: 10000,
    });
    console.log("Navigated to lockers page");

    // Test creating a new locker
    await page.waitForSelector(
      "xpath///button[contains(text(), 'New Locker')]",
      { timeout: 5000 }
    );
    await page.click('button:contains("New Locker")');
    await page.waitForSelector('input[name="locker_number"]', {
      timeout: 10000,
    });
    console.log("New locker modal opened");

    // Fill locker form
    await page.type('input[name="locker_number"]', "999");
    await page.type('input[name="location"]', "Test Area");
    await page.select('select[name="status"]', "available");
    await page.click('button:contains("Create")');

    // Wait for success message or redirect
    await new Promise((resolve) => setTimeout(resolve, 3000));
    console.log("Created new locker");

    // Test editing a locker
    const editButtons = await page.$$('button:contains("Edit")');
    if (editButtons.length > 0) {
      await editButtons[0].click();
      await page.waitForSelector('input[name="location"]', { timeout: 10000 });
      console.log("Edit modal opened");

      // Update location
      await page.click('input[name="location"]', { clickCount: 3 });
      await page.type('input[name="location"]', " - Updated by automated test");
      await page.click('button:contains("Update")');

      await new Promise((resolve) => setTimeout(resolve, 2000));
      console.log("Updated locker");
    }

    // Test deleting a locker
    const deleteButtons = await page.$$('button:contains("Delete")');
    if (deleteButtons.length > 0) {
      await deleteButtons[0].click();

      // Handle confirmation dialog if present
      try {
        await page.waitForSelector(".modal", { timeout: 3000 });
        await page.click('button:contains("Confirm")');
      } catch (e) {
        // No confirmation dialog, continue
      }

      await new Promise((resolve) => setTimeout(resolve, 2000));
      console.log("Deleted locker");
    }

    // Test filtering and search
    await page.type('input[placeholder*="search"]', "test");
    await new Promise((resolve) => setTimeout(resolve, 1000));
    console.log("Tested search functionality");

    // Clear search
    await page.click('input[placeholder*="search"]', { clickCount: 3 });
    await page.keyboard.press("Backspace");

    // Test status filtering
    const statusSelects = await page.$$('select[name="status"]');
    if (statusSelects.length > 0) {
      await statusSelects[0].select("available");
      await new Promise((resolve) => setTimeout(resolve, 1000));
      console.log("Tested status filtering");
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
