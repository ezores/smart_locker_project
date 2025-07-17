// Copy Logs Script
// Run this in the browser console to copy all logs

(function () {
  // Create a function to copy logs
  function copyAllLogs() {
    // Get all console logs (this is a simplified approach)
    const logs = [];

    // Add current timestamp
    logs.push(`=== LOG COPY TIMESTAMP ===`);
    logs.push(`Copied at: ${new Date().toISOString()}`);
    logs.push(`URL: ${window.location.href}`);
    logs.push(`User Agent: ${navigator.userAgent}`);
    logs.push(``);

    // Note: Browser console logs are not directly accessible via JavaScript
    // This is a helper script to format the logs you manually copy

    logs.push(`=== INSTRUCTIONS ===`);
    logs.push(
      `1. Open browser console (F12 or right-click -> Inspect -> Console)`
    );
    logs.push(`2. Click "Open Locker (Real)" button on any locker`);
    logs.push(`3. Copy all the console output (Ctrl+A, Ctrl+C in console)`);
    logs.push(`4. Paste the logs below this message`);
    logs.push(`5. Send the complete log to help diagnose the issue`);
    logs.push(``);

    logs.push(`=== EXPECTED LOG FORMAT ===`);
    logs.push(`When you click "Open Locker (Real)", you should see:`);
    logs.push(`- LOCKER OPEN REQUEST (REAL)`);
    logs.push(`- Locker details (ID, Name, RS485 settings)`);
    logs.push(`- API request details`);
    logs.push(`- Response or error details`);
    logs.push(`- RS485 communication logs (from backend)`);
    logs.push(``);

    logs.push(`=== TROUBLESHOOTING CHECKLIST ===`);
    logs.push(`- Is the USB-to-RS485 converter connected?`);
    logs.push(`- Is the device on /dev/ttyUSB0?`);
    logs.push(`- Do you have permission to access the device?`);
    logs.push(`- Are the RS485 address and locker number correct?`);
    logs.push(`- Is the hardware responding to the commands?`);
    logs.push(``);

    // Copy to clipboard
    const text = logs.join("\n");

    if (navigator.clipboard) {
      navigator.clipboard.writeText(text).then(() => {
        console.log("Log instructions copied to clipboard!");
        console.log('Now click "Open Locker (Real)" and copy the actual logs.');
      });
    } else {
      // Fallback for older browsers
      const textArea = document.createElement("textarea");
      textArea.value = text;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand("copy");
      document.body.removeChild(textArea);
      console.log("Log instructions copied to clipboard!");
      console.log('Now click "Open Locker (Real)" and copy the actual logs.');
    }
  }

  // Add the function to window for easy access
  window.copyLogInstructions = copyAllLogs;

  // Auto-run the function
  copyAllLogs();

  console.log("=== LOG COPY SCRIPT LOADED ===");
  console.log("Run copyLogInstructions() anytime to copy log instructions");
  console.log(
    'After clicking "Open Locker (Real)", copy all console output manually'
  );
})();
