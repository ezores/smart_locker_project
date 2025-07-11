#!/usr/bin/env node

const puppeteer = require("puppeteer");

async function testAdminDashboard() {
  console.log("Testing Admin Dashboard...");

  const browser = await puppeteer.launch({
    headless: "new",
    defaultViewport: null,
    args: ["--start-maximized"],
  });

  try {
    const page = await browser.newPage();

    // Login as admin
    await page.goto("http://localhost:5173");
    await page.waitForSelector('input[name="username"]', { timeout: 10000 });
    await page.type('input[name="username"]', "admin");
    await page.type('input[name="password"]', "admin123");
    await page.click('button[type="submit"]');
    await page.waitForSelector("xpath///h1[contains(text(), 'Main Menu')]", {
      timeout: 10000,
    });
    console.log("Logged in as admin");

    // Navigate to admin dashboard
    await page.click('a[href="/admin"]');
    await page.waitForSelector("xpath///h1[contains(text(), 'Admin')]", {
      timeout: 10000,
    });
    console.log("Navigated to admin dashboard");

    // Test dashboard overview
    const statsCards = await page.$$(
      ".stats-card, .bg-blue-600, .bg-green-600, .bg-yellow-600, .bg-red-600"
    );
    console.log(`Found ${statsCards.length} statistics cards`);

    // Test user management section
    const userManagementLink = await page.$(
      'a[href="/users"], button:contains("Users")'
    );
    if (userManagementLink) {
      await userManagementLink.click();
      await page.waitForSelector("xpath///h1[contains(text(), 'Users')]", {
        timeout: 10000,
      });
      console.log("Navigated to user management");

      // Test creating a new user
      const newUserButton = await page.$(
        'button:contains("New User"), button:contains("Add User")'
      );
      if (newUserButton) {
        await newUserButton.click();
        await page.waitForSelector('input[name="username"]', {
          timeout: 10000,
        });
        console.log("New user modal opened");

        // Fill user form
        await page.type('input[name="username"]', "testuser");
        await page.type('input[name="email"]', "test@example.com");
        await page.type('input[name="first_name"]', "Test");
        await page.type('input[name="last_name"]', "User");
        await page.select('select[name="role"]', "user");
        await page.type('input[name="password"]', "password123");
        await page.click('button:contains("Create")');

        await new Promise((resolve) => setTimeout(resolve, 2000));
        console.log("Created new user");
      }

      // Go back to admin dashboard
      await page.click('a[href="/admin"]');
      await page.waitForSelector("xpath///h1[contains(text(), 'Admin')]", {
        timeout: 10000,
      });
    }

    // Test reports section
    const reportsLink = await page.$(
      'a[href="/reports"], button:contains("Reports")'
    );
    if (reportsLink) {
      await reportsLink.click();
      await page.waitForSelector("xpath///h1[contains(text(), 'Reports')]", {
        timeout: 10000,
      });
      console.log("Navigated to reports page");

      // Test generating a report
      const generateButton = await page.$(
        'button:contains("Generate"), button:contains("Export")'
      );
      if (generateButton) {
        await generateButton.click();
        await new Promise((resolve) => setTimeout(resolve, 2000));
        console.log("Tested report generation");
      }

      // Go back to admin dashboard
      await page.click('a[href="/admin"]');
      await page.waitForSelector("xpath///h1[contains(text(), 'Admin')]", {
        timeout: 10000,
      });
    }

    // Test system settings
    const settingsLink = await page.$(
      'a[href="/settings"], button:contains("Settings")'
    );
    if (settingsLink) {
      await settingsLink.click();
      await page.waitForSelector("xpath///h1[contains(text(), 'Settings')]", {
        timeout: 10000,
      });
      console.log("Navigated to settings page");

      // Test updating settings
      const saveButton = await page.$(
        'button:contains("Save"), button:contains("Update")'
      );
      if (saveButton) {
        await saveButton.click();
        await new Promise((resolve) => setTimeout(resolve, 1000));
        console.log("Tested settings update");
      }

      // Go back to admin dashboard
      await page.click('a[href="/admin"]');
      await page.waitForSelector("xpath///h1[contains(text(), 'Admin')]", {
        timeout: 10000,
      });
    }

    // Test logs section
    const logsLink = await page.$('a[href="/logs"], button:contains("Logs")');
    if (logsLink) {
      await logsLink.click();
      await page.waitForSelector("xpath///h1[contains(text(), 'Logs')]", {
        timeout: 10000,
      });
      console.log("Navigated to logs page");

      // Test log filtering
      const filterInput = await page.$(
        'input[placeholder*="filter"], input[placeholder*="search"]'
      );
      if (filterInput) {
        await filterInput.type("login");
        await new Promise((resolve) => setTimeout(resolve, 1000));
        console.log("Tested log filtering");
      }

      // Go back to admin dashboard
      await page.click('a[href="/admin"]');
      await page.waitForSelector("xpath///h1[contains(text(), 'Admin')]", {
        timeout: 10000,
      });
    }

    console.log("Admin dashboard tests completed successfully!");
  } catch (error) {
    console.error("Admin dashboard test failed:", error.message);
    throw error;
  } finally {
    await browser.close();
  }
}

if (require.main === module) {
  testAdminDashboard().catch(console.error);
}

module.exports = { testAdminDashboard };
