#!/usr/bin/env node

const { testAuthFlow } = require("./test_auth_flow");
const { testReservations } = require("./test_reservations");
const { testLockers } = require("./test_lockers");
const { testAdminDashboard } = require("./test_admin_dashboard");
const { testItems } = require("./test_items");

async function runAllTests() {
  console.log("Starting Comprehensive Smart Locker System Tests");
  console.log("==================================================");

  const tests = [
    { name: "Authentication Flow", fn: testAuthFlow },
    { name: "Reservations Module", fn: testReservations },
    { name: "Lockers Module", fn: testLockers },
    { name: "Admin Dashboard", fn: testAdminDashboard },
    { name: "Items Module", fn: testItems },
  ];

  const results = [];

  for (const test of tests) {
    console.log(`\nRunning ${test.name}...`);
    console.log("─".repeat(50));

    const startTime = Date.now();

    try {
      await test.fn();
      const duration = Date.now() - startTime;
      results.push({ name: test.name, status: "PASS", duration });
      console.log(`${test.name} completed successfully (${duration}ms)`);
    } catch (error) {
      const duration = Date.now() - startTime;
      results.push({
        name: test.name,
        status: "FAIL",
        duration,
        error: error.message,
      });
      console.log(`${test.name} failed (${duration}ms): ${error.message}`);
    }
  }

  // Print summary
  console.log("\nTest Results Summary");
  console.log("=======================");

  const passed = results.filter((r) => r.status === "PASS").length;
  const failed = results.filter((r) => r.status === "FAIL").length;
  const total = results.length;

  console.log(`Total Tests: ${total}`);
  console.log(`Passed: ${passed}`);
  console.log(`Failed: ${failed}`);
  console.log(`Success Rate: ${((passed / total) * 100).toFixed(1)}%`);

  if (failed > 0) {
    console.log("\nFailed Tests:");
    results
      .filter((r) => r.status === "FAIL")
      .forEach((result) => {
        console.log(`  - ${result.name}: ${result.error}`);
      });
  }

  console.log("\nTest Durations:");
  results.forEach((result) => {
    const status = result.status === "PASS" ? "PASS" : "FAIL";
    console.log(`  ${status} ${result.name}: ${result.duration}ms`);
  });

  if (failed === 0) {
    console.log(
      "\nAll tests passed! The Smart Locker System is working correctly."
    );
  } else {
    console.log("\nSome tests failed. Please check the system configuration.");
    process.exit(1);
  }
}

// Health check function to ensure system is ready
async function healthCheck() {
  console.log("Performing system health check...");

  try {
    // Check if Puppeteer is available
    try {
      require("puppeteer");
      console.log("Puppeteer is available");
    } catch (error) {
      console.error("Puppeteer not found. Installing...");
      const { execSync } = require("child_process");
      execSync("cd frontend && npm install puppeteer", { stdio: "inherit" });
      console.log("Puppeteer installed successfully");
    }

    const { default: fetch } = await import("node-fetch");

    // Check backend health
    const backendResponse = await fetch("http://localhost:5172/api/health");
    if (!backendResponse.ok) {
      throw new Error("Backend is not responding");
    }
    console.log("Backend is healthy");

    // Check frontend health
    const frontendResponse = await fetch("http://localhost:5173");
    if (!frontendResponse.ok) {
      throw new Error("Frontend is not responding");
    }
    console.log("Frontend is healthy");

    return true;
  } catch (error) {
    console.error("Health check failed:", error.message);
    console.log("\nMake sure the system is running with:");
    console.log("   ./start.sh --demo --reset-db --verbose");
    return false;
  }
}

async function main() {
  try {
    // Perform health check first
    const isHealthy = await healthCheck();
    if (!isHealthy) {
      process.exit(1);
    }

    // Run all tests
    await runAllTests();
  } catch (error) {
    console.error("Test runner failed:", error.message);
    process.exit(1);
  }
}

if (require.main === module) {
  main();
}

module.exports = { runAllTests, healthCheck };
