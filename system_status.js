#!/usr/bin/env node

/**
 * Smart Locker System Status Checker
 * Shows the current status of all system components
 */

const axios = require("axios");

const BACKEND_URL = "http://localhost:5172";
const FRONTEND_URL = "http://localhost:5173";

async function checkSystemStatus() {
  console.log("🔍 Smart Locker System Status Check");
  console.log("=" * 50);

  const status = {
    backend: false,
    frontend: false,
    database: false,
    rs485: false,
    lockers: false,
    authentication: false,
  };

  // Check Backend Health
  try {
    const response = await axios.get(`${BACKEND_URL}/api/health`);
    status.backend = response.status === 200;
    status.database = response.data.database === "connected";
    console.log(`✅ Backend: ${status.backend ? "RUNNING" : "DOWN"}`);
    console.log(
      `✅ Database: ${status.database ? "CONNECTED" : "DISCONNECTED"}`
    );
  } catch (error) {
    console.log(`❌ Backend: DOWN (${error.message})`);
  }

  // Check Frontend
  try {
    const response = await axios.get(FRONTEND_URL);
    status.frontend = response.status === 200;
    console.log(`✅ Frontend: ${status.frontend ? "RUNNING" : "DOWN"}`);
  } catch (error) {
    console.log(`❌ Frontend: DOWN (${error.message})`);
  }

  // Check Authentication
  try {
    const response = await axios.post(`${BACKEND_URL}/api/auth/login`, {
      username: "testadmin",
      password: "test123",
    });
    status.authentication = response.status === 200;
    console.log(
      `✅ Authentication: ${status.authentication ? "WORKING" : "FAILED"}`
    );
  } catch (error) {
    console.log(`❌ Authentication: FAILED (${error.message})`);
  }

  // Check Lockers API
  if (status.authentication) {
    try {
      const token = (
        await axios.post(`${BACKEND_URL}/api/auth/login`, {
          username: "testadmin",
          password: "test123",
        })
      ).data.token;

      const response = await axios.get(`${BACKEND_URL}/api/lockers`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      status.lockers = response.status === 200;
      console.log(`✅ Lockers API: ${status.lockers ? "WORKING" : "FAILED"}`);

      // Check RS485 functionality
      const rs485Response = await axios.get(
        `${BACKEND_URL}/api/admin/rs485/test`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      status.rs485 = rs485Response.status === 200;
      console.log(`✅ RS485 System: ${status.rs485 ? "WORKING" : "FAILED"}`);
    } catch (error) {
      console.log(`❌ Lockers API: FAILED (${error.message})`);
      console.log(`❌ RS485 System: FAILED (${error.message})`);
    }
  }

  console.log("\n📊 System Summary:");
  console.log("=" * 30);

  const workingComponents = Object.values(status).filter(Boolean).length;
  const totalComponents = Object.keys(status).length;
  const healthPercentage = (
    (workingComponents / totalComponents) *
    100
  ).toFixed(1);

  console.log(
    `Overall Health: ${healthPercentage}% (${workingComponents}/${totalComponents} components working)`
  );

  if (workingComponents === totalComponents) {
    console.log("🎉 All systems operational!");
    console.log("\n🚀 Ready for use:");
    console.log("   • Backend API: http://localhost:5172");
    console.log("   • Frontend: http://localhost:5173");
    console.log("   • RS485 integration: ACTIVE");
    console.log("   • Locker management: ACTIVE");
    console.log("\n💡 Features available:");
    console.log("   • Real open locker button (with toast notifications)");
    console.log("   • RS485 protocol frame generation");
    console.log("   • Locker editing with RS485 configuration");
    console.log("   • Automated testing suite");
  } else {
    console.log("⚠️ Some components need attention");
    console.log("\n🔧 Troubleshooting:");
    if (!status.backend)
      console.log(
        "   • Check if backend is running: python app.py --demo --port 5050"
      );
    if (!status.frontend)
      console.log("   • Check if frontend is running: npm run dev");
    if (!status.database)
      console.log("   • Check database connection and DATABASE_URL");
    if (!status.authentication)
      console.log("   • Check if demo data is loaded");
  }

  return workingComponents === totalComponents;
}

// Run status check if this script is executed directly
if (require.main === module) {
  checkSystemStatus().catch((error) => {
    console.error("❌ Status check failed:", error.message);
    process.exit(1);
  });
}

module.exports = { checkSystemStatus };
