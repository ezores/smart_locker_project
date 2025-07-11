#!/usr/bin/env node

const http = require("http");
const https = require("https");

const BACKEND_URL = "http://localhost:5172";
const FRONTEND_URL = "http://localhost:5173";

// Colors for console output
const colors = {
  green: "\x1b[32m",
  red: "\x1b[31m",
  yellow: "\x1b[33m",
  blue: "\x1b[34m",
  reset: "\x1b[0m",
};

function log(message, color = "reset") {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function makeRequest(url, options = {}) {
  return new Promise((resolve, reject) => {
    const urlObj = new URL(url);
    const isHttps = urlObj.protocol === "https:";
    const client = isHttps ? https : http;

    const requestOptions = {
      hostname: urlObj.hostname,
      port: urlObj.port,
      path: urlObj.pathname + urlObj.search,
      method: options.method || "GET",
      headers: options.headers || {},
    };

    const req = client.request(requestOptions, (res) => {
      let data = "";
      res.on("data", (chunk) => {
        data += chunk;
      });
      res.on("end", () => {
        resolve({
          statusCode: res.statusCode,
          headers: res.headers,
          data: data,
        });
      });
    });

    req.on("error", (err) => {
      reject(err);
    });

    if (options.body) {
      req.write(options.body);
    }
    req.end();
  });
}

async function testBackendHealth() {
  log("\n🔍 Testing Backend Health...", "blue");

  try {
    const response = await makeRequest(`${BACKEND_URL}/api/health`);
    if (response.statusCode === 200) {
      const healthData = JSON.parse(response.data);
      log("✅ Backend is healthy!", "green");
      log(`   Status: ${healthData.status}`, "green");
      log(`   Database: ${healthData.database}`, "green");
      log(`   Timestamp: ${healthData.timestamp}`, "green");
      return true;
    } else {
      log(`❌ Backend health check failed: ${response.statusCode}`, "red");
      return false;
    }
  } catch (error) {
    log(`❌ Backend connection failed: ${error.message}`, "red");
    return false;
  }
}

async function testFrontendHealth() {
  log("\n🔍 Testing Frontend Health...", "blue");

  try {
    const response = await makeRequest(FRONTEND_URL);
    if (response.statusCode === 200) {
      log("✅ Frontend is healthy!", "green");
      log(`   Status: ${response.statusCode}`, "green");
      return true;
    } else {
      log(`❌ Frontend health check failed: ${response.statusCode}`, "red");
      return false;
    }
  } catch (error) {
    log(`❌ Frontend connection failed: ${error.message}`, "red");
    return false;
  }
}

async function testLogin() {
  log("\n🔍 Testing Login API...", "blue");

  try {
    const loginData = {
      username: "admin",
      password: "admin123",
    };

    const response = await makeRequest(`${BACKEND_URL}/api/auth/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(loginData),
    });

    if (response.statusCode === 200) {
      const loginResponse = JSON.parse(response.data);
      log("✅ Login successful!", "green");
      log(`   User: ${loginResponse.user.username}`, "green");
      log(`   Role: ${loginResponse.user.role}`, "green");
      log(`   Token: ${loginResponse.token.substring(0, 20)}...`, "green");
      return loginResponse.token;
    } else {
      log(`❌ Login failed: ${response.statusCode}`, "red");
      log(`   Response: ${response.data}`, "red");
      return null;
    }
  } catch (error) {
    log(`❌ Login request failed: ${error.message}`, "red");
    return null;
  }
}

async function testProtectedAPI(token) {
  if (!token) {
    log("⚠️  Skipping protected API test (no token)", "yellow");
    return false;
  }

  log("\n🔍 Testing Protected API...", "blue");

  try {
    const response = await makeRequest(`${BACKEND_URL}/api/lockers`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (response.statusCode === 200) {
      const lockers = JSON.parse(response.data);
      log("✅ Protected API access successful!", "green");
      log(`   Found ${lockers.length} lockers`, "green");
      return true;
    } else {
      log(`❌ Protected API access failed: ${response.statusCode}`, "red");
      log(`   Response: ${response.data}`, "red");
      return false;
    }
  } catch (error) {
    log(`❌ Protected API request failed: ${error.message}`, "red");
    return false;
  }
}

async function runTests() {
  log("🚀 Smart Locker System Health Check", "blue");
  log("=====================================", "blue");

  const results = {
    backend: await testBackendHealth(),
    frontend: await testFrontendHealth(),
    login: await testLogin(),
    protected: false,
  };

  if (results.login) {
    results.protected = await testProtectedAPI(results.login);
  }

  // Summary
  log("\n📊 Test Results Summary:", "blue");
  log("========================", "blue");
  log(
    `Backend Health: ${results.backend ? "✅ PASS" : "❌ FAIL"}`,
    results.backend ? "green" : "red"
  );
  log(
    `Frontend Health: ${results.frontend ? "✅ PASS" : "❌ FAIL"}`,
    results.frontend ? "green" : "red"
  );
  log(
    `Login API: ${results.login ? "✅ PASS" : "❌ FAIL"}`,
    results.login ? "green" : "red"
  );
  log(
    `Protected API: ${results.protected ? "✅ PASS" : "❌ FAIL"}`,
    results.protected ? "green" : "red"
  );

  const allPassed =
    results.backend && results.frontend && results.login && results.protected;

  if (allPassed) {
    log("\n🎉 All tests passed! System is running correctly.", "green");
    log("\n📋 System Information:", "blue");
    log(`   Backend URL: ${BACKEND_URL}`, "blue");
    log(`   Frontend URL: ${FRONTEND_URL}`, "blue");
    log(`   Health Check: ${BACKEND_URL}/api/health`, "blue");
    log("\n🔑 Demo Credentials:", "blue");
    log("   Username: admin", "blue");
    log("   Password: admin123", "blue");
  } else {
    log("\n❌ Some tests failed. Please check the system.", "red");
    process.exit(1);
  }
}

// Run the tests
runTests().catch((error) => {
  log(`\n💥 Test runner error: ${error.message}`, "red");
  process.exit(1);
});
