#!/usr/bin/env node

/**
 * Automated System Test for Smart Locker System
 * Tests backend API, frontend functionality, and RS485 integration
 */

const axios = require("axios");
const { exec } = require("child_process");
const { promisify } = require("util");

const execAsync = promisify(exec);

// Configuration
const BACKEND_URL = "http://localhost:5172";
const FRONTEND_URL = "http://localhost:5173";

// Test results
let testResults = {
  passed: 0,
  failed: 0,
  errors: [],
};

// Utility functions
function log(message, type = "INFO") {
  const timestamp = new Date().toISOString();
  console.log(`[${timestamp}] [${type}] ${message}`);
}

function addResult(testName, passed, error = null) {
  if (passed) {
    testResults.passed++;
    log(`${testName} - PASSED`, "PASS");
  } else {
    testResults.failed++;
    log(`❌ ${testName} - FAILED`, "FAIL");
    if (error) {
      testResults.errors.push({
        test: testName,
        error: error.message || error,
      });
      log(`   Error: ${error.message || error}`, "ERROR");
    }
  }
}

// Test functions
async function testBackendHealth() {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/health`);
    const isHealthy =
      response.status === 200 && response.data.status === "healthy";
    addResult("Backend Health Check", isHealthy);
    return isHealthy;
  } catch (error) {
    addResult("Backend Health Check", false, error);
    return false;
  }
}

async function testBackendLogin() {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/auth/login`, {
      username: "student1",
      password: "student123",
    });
    const hasToken = response.status === 200 && response.data.token;
    addResult("Backend Login", hasToken);
    return response.data.token;
  } catch (error) {
    addResult("Backend Login", false, error);
    return null;
  }
}

async function testAdminLogin() {
  try {
    const response = await axios.post(`${BACKEND_URL}/api/auth/login`, {
      username: "admin",
      password: "admin123",
    });
    const hasToken = response.status === 200 && response.data.token;
    addResult("Admin Login", hasToken);
    return response.data.token;
  } catch (error) {
    addResult("Admin Login", false, error);
    return null;
  }
}

async function testLockersAPI(token) {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/lockers`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    const hasLockers = response.status === 200 && Array.isArray(response.data);
    addResult("Lockers API", hasLockers);

    // Test RS485 fields in locker data
    if (hasLockers && response.data.length > 0) {
      const firstLocker = response.data[0];
      const hasRS485Fields =
        firstLocker.hasOwnProperty("rs485_address") &&
        firstLocker.hasOwnProperty("rs485_locker_number");
      addResult("RS485 Fields in Lockers", hasRS485Fields);
    }

    return hasLockers;
  } catch (error) {
    addResult("Lockers API", false, error);
    return false;
  }
}

async function testOpenLockerAPI(studentToken, adminToken) {
  try {
    // Create a test locker first
    const createData = {
      name: "Test Locker for Opening",
      location: "Test Location",
      status: "available",
      rs485_address: 8,
      rs485_locker_number: 16,
    };

    const createResponse = await axios.post(
      `${BACKEND_URL}/api/admin/lockers`,
      createData,
      {
        headers: { Authorization: `Bearer ${adminToken}` },
      }
    );

    if (createResponse.status !== 201) {
      addResult("Open Locker API", false, "Failed to create test locker");
      return false;
    }

    const lockerId = createResponse.data.locker.id;
    const response = await axios.post(
      `${BACKEND_URL}/api/lockers/${lockerId}/open`,
      {},
      {
        headers: { Authorization: `Bearer ${adminToken}` },
      }
    );

    const success = response.status === 200 && response.data.message;
    addResult("Open Locker API", success);

    // Test RS485 result in response
    if (success && response.data.rs485_result) {
      const hasRS485Result =
        response.data.rs485_result.hasOwnProperty("frame") &&
        response.data.rs485_result.hasOwnProperty("rs485_address") &&
        response.data.rs485_result.hasOwnProperty("rs485_locker_number");
      addResult("RS485 Result in Open Response", hasRS485Result);
    }

    // Clean up - delete the test locker
    await axios.delete(`${BACKEND_URL}/api/admin/lockers/${lockerId}`, {
      headers: { Authorization: `Bearer ${adminToken}` },
    });

    return success;
  } catch (error) {
    addResult("Open Locker API", false, error);
    return false;
  }
}

async function testAdminLockersAPI(adminToken) {
  try {
    // Test creating a locker with RS485 fields
    const createData = {
      name: "Test Locker RS485",
      location: "Test Location",
      status: "available",
      rs485_address: 5,
      rs485_locker_number: 12,
    };

    const createResponse = await axios.post(
      `${BACKEND_URL}/api/admin/lockers`,
      createData,
      {
        headers: { Authorization: `Bearer ${adminToken}` },
      }
    );

    const createSuccess = createResponse.status === 201;
    addResult("Create Locker with RS485", createSuccess);

    if (createSuccess) {
      const lockerId = createResponse.data.locker.id;

      // Test updating the locker
      const updateData = {
        name: "Updated Test Locker",
        rs485_address: 10,
        rs485_locker_number: 15,
      };

      const updateResponse = await axios.put(
        `${BACKEND_URL}/api/admin/lockers/${lockerId}`,
        updateData,
        {
          headers: { Authorization: `Bearer ${adminToken}` },
        }
      );

      const updateSuccess = updateResponse.status === 200;
      addResult("Update Locker RS485 Fields", updateSuccess);

      // Test deleting the locker
      const deleteResponse = await axios.delete(
        `${BACKEND_URL}/api/admin/lockers/${lockerId}`,
        {
          headers: { Authorization: `Bearer ${adminToken}` },
        }
      );

      const deleteSuccess = deleteResponse.status === 200;
      addResult("Delete Locker", deleteSuccess);
    }

    return createSuccess;
  } catch (error) {
    addResult("Admin Lockers API", false, error);
    return false;
  }
}

async function testRS485FrameGeneration(adminToken) {
  try {
    // Test the RS485 frame generation by calling the backend
    const response = await axios.get(`${BACKEND_URL}/api/admin/rs485/test`, {
      headers: { Authorization: `Bearer ${adminToken}` },
    });
    const success = response.status === 200;
    addResult("RS485 Test Endpoint", success);
    return success;
  } catch (error) {
    addResult("RS485 Test Endpoint", false, error);
    return false;
  }
}

async function testFrontendAccessibility() {
  try {
    const response = await axios.get(FRONTEND_URL);
    const success =
      response.status === 200 && response.data.includes("Smart Locker System");
    addResult("Frontend Accessibility", success);
    return success;
  } catch (error) {
    addResult("Frontend Accessibility", false, error);
    return false;
  }
}

async function testSystemIntegration() {
  try {
    // Test that the backend and frontend can communicate
    const backendHealth = await testBackendHealth();
    const frontendAccess = await testFrontendAccessibility();

    const integrationSuccess = backendHealth && frontendAccess;
    addResult("System Integration", integrationSuccess);

    return integrationSuccess;
  } catch (error) {
    addResult("System Integration", false, error);
    return false;
  }
}

// Main test runner
async function runAllTests() {
  log("Starting Smart Locker System Automated Tests", "START");
  log("=" * 60);

  // Test backend functionality
  log("Testing Backend Functionality...", "SECTION");
  const backendHealth = await testBackendHealth();

  if (!backendHealth) {
    log("❌ Backend is not healthy. Stopping tests.", "ERROR");
    return;
  }

  const studentToken = await testBackendLogin();
  if (!studentToken) {
    log("❌ Cannot authenticate as student. Stopping tests.", "ERROR");
    return;
  }

  const adminToken = await testAdminLogin();
  if (!adminToken) {
    log("❌ Cannot authenticate as admin. Stopping tests.", "ERROR");
    return;
  }

  await testLockersAPI(studentToken);
  await testOpenLockerAPI(studentToken, adminToken);
  await testAdminLockersAPI(adminToken);
  await testRS485FrameGeneration(adminToken);

  // Test frontend functionality
  log("Testing Frontend Functionality...", "SECTION");
  await testFrontendAccessibility();

  // Test system integration
  log("Testing System Integration...", "SECTION");
  await testSystemIntegration();

  // Print results
  log("=" * 60);
  log("Test Results Summary:", "SUMMARY");
  log(`Passed: ${testResults.passed}`, "SUMMARY");
  log(`❌ Failed: ${testResults.failed}`, "SUMMARY");
  log(
    `Success Rate: ${(
      (testResults.passed / (testResults.passed + testResults.failed)) *
      100
    ).toFixed(1)}%`,
    "SUMMARY"
  );

  if (testResults.errors.length > 0) {
    log("📋 Error Details:", "ERRORS");
    testResults.errors.forEach((error, index) => {
      log(`${index + 1}. ${error.test}: ${error.error}`, "ERROR");
    });
  }

  const overallSuccess = testResults.failed === 0;
  log(
    overallSuccess ? "All tests passed!" : "Some tests failed.",
    overallSuccess ? "SUCCESS" : "WARNING"
  );

  return overallSuccess;
}

// Run tests if this script is executed directly
if (require.main === module) {
  runAllTests().catch((error) => {
    log(`❌ Test runner failed: ${error.message}`, "FATAL");
    process.exit(1);
  });
}

module.exports = { runAllTests, testResults };
