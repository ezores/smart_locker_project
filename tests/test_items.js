#!/usr/bin/env node

const puppeteer = require("puppeteer");

async function testItems() {
  console.log("Testing Items Module...");

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

    // Navigate to items page
    await page.click('a[href="/items"]');
    await page.waitForSelector("xpath///h1[contains(text(), 'Items')]", {
      timeout: 10000,
    });
    console.log("Navigated to items page");

    // Test creating a new item
    await page.waitForSelector("xpath///button[contains(text(), 'New Item')]", {
      timeout: 5000,
    });
    await page.click('button:contains("New Item")');
    await page.waitForSelector('input[name="name"]', { timeout: 10000 });
    console.log("New item modal opened");

    // Fill item form
    await page.type('input[name="name"]', "Test Item");
    await page.type(
      'input[name="description"]',
      "Test item from automated test"
    );
    await page.type('input[name="quantity"]', "5");
    await page.select('select[name="category"]', "electronics");
    await page.click('button:contains("Create")');

    // Wait for success message or redirect
    await new Promise((resolve) => setTimeout(resolve, 3000));
    console.log("Created new item");

    // Test editing an item
    const editButtons = await page.$$('button:contains("Edit")');
    if (editButtons.length > 0) {
      await editButtons[0].click();
      await page.waitForSelector('input[name="description"]', {
        timeout: 10000,
      });
      console.log("Edit modal opened");

      // Update description
      await page.click('input[name="description"]', { clickCount: 3 });
      await page.type(
        'input[name="description"]',
        " - Updated by automated test"
      );
      await page.click('button:contains("Update")');

      await new Promise((resolve) => setTimeout(resolve, 2000));
      console.log("Updated item");
    }

    // Test deleting an item
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
      console.log("Deleted item");
    }

    // Test filtering and search
    await page.type('input[placeholder*="search"]', "test");
    await new Promise((resolve) => setTimeout(resolve, 1000));
    console.log("Tested search functionality");

    // Clear search
    await page.click('input[placeholder*="search"]', { clickCount: 3 });
    await page.keyboard.press("Backspace");

    // Test category filtering
    const categorySelects = await page.$$('select[name="category"]');
    if (categorySelects.length > 0) {
      await categorySelects[0].select("electronics");
      await new Promise((resolve) => setTimeout(resolve, 1000));
      console.log("Tested category filtering");
    }

    console.log("Items module tests completed successfully!");
  } catch (error) {
    console.error("Items test failed:", error.message);
    throw error;
  } finally {
    await browser.close();
  }
}

if (require.main === module) {
  testItems().catch(console.error);
}

module.exports = { testItems };
