#!/usr/bin/env python3
"""
RS485 Hardware Test Script
==========================
This script tests RS485 hardware connectivity and functionality.
Use this to verify that the Smart Locker System can communicate
with real RS485 hardware on any device.

Author: Alp Alpdogan
"""

import sys
import os
import time
import logging
from typing import List, Dict, Any

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if all required dependencies are installed"""
    logger.info("=== CHECKING DEPENDENCIES ===")
    
    required_packages = [
        'serial',
        'flask',
        'psycopg2',
        'requests',
        'pandas',
        'openpyxl'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            logger.info(f"✓ {package} - OK")
        except ImportError:
            logger.error(f"✗ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"Missing packages: {missing_packages}")
        logger.error("Install missing packages with: pip install " + " ".join(missing_packages))
        return False
    
    logger.info("All dependencies are installed!")
    return True

def check_serial_ports():
    """Check available serial ports"""
    logger.info("=== CHECKING SERIAL PORTS ===")
    
    try:
        import serial.tools.list_ports
        ports = list(serial.tools.list_ports.comports())
        
        if not ports:
            logger.warning("No serial ports found!")
            return []
        
        logger.info(f"Found {len(ports)} serial port(s):")
        for port in ports:
            logger.info(f"  - {port.device}: {port.description}")
            if port.hwid:
                logger.info(f"    Hardware ID: {port.hwid}")
        
        return [port.device for port in ports]
    
    except ImportError:
        logger.error("pyserial not installed! Install with: pip install pyserial")
        return []
    except Exception as e:
        logger.error(f"Error checking serial ports: {e}")
        return []

def test_rs485_connection(port: str = "/dev/ttyUSB0"):
    """Test RS485 connection to specific port"""
    logger.info(f"=== TESTING RS485 CONNECTION TO {port} ===")
    
    try:
        import serial
        
        # Try to open the port
        logger.info(f"Attempting to connect to {port}...")
        ser = serial.Serial(
            port=port,
            baudrate=9600,
            timeout=1,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
        )
        
        logger.info(f"✓ Successfully connected to {port}")
        logger.info(f"  Baudrate: {ser.baudrate}")
        logger.info(f"  Timeout: {ser.timeout}")
        logger.info(f"  Port settings: {ser.get_settings()}")
        
        # Test basic communication
        logger.info("Testing basic communication...")
        
        # Send a test frame
        test_frame = "5A5A0000000400010104"  # Open locker 1
        logger.info(f"Sending test frame: {test_frame}")
        
        # Convert to bytes
        frame_bytes = bytes.fromhex(test_frame)
        logger.info(f"Frame bytes: {[f'{b:02X}' for b in frame_bytes]}")
        
        # Send frame
        bytes_written = ser.write(frame_bytes)
        logger.info(f"Bytes written: {bytes_written}")
        
        # Wait for response
        logger.info("Waiting for response...")
        time.sleep(0.5)
        
        # Check if data is available
        if ser.in_waiting > 0:
            response = ser.read(ser.in_waiting)
            logger.info(f"Response received: {response}")
            logger.info(f"Response hex: {[f'{b:02X}' for b in response]}")
        else:
            logger.info("No response received (this is normal for some RS485 devices)")
        
        # Close connection
        ser.close()
        logger.info("✓ RS485 connection test completed successfully")
        return True
        
    except serial.SerialException as e:
        logger.error(f"Serial connection error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False

def test_rs485_utils():
    """Test RS485 utility functions"""
    logger.info("=== TESTING RS485 UTILITIES ===")
    
    try:
        from backend.utils.rs485 import generate_rs485_frame, RS485Controller
        
        # Test frame generation
        logger.info("Testing frame generation...")
        test_cases = [
            (0, 1),   # Address 0, Locker 1
            (1, 5),   # Address 1, Locker 5
            (15, 12), # Address 15, Locker 12
            (31, 24), # Address 31, Locker 24
        ]
        
        for address, locker_number in test_cases:
            frame = generate_rs485_frame(address, locker_number)
            logger.info(f"Address {address}, Locker {locker_number}: {frame}")
            
            # Verify frame format
            if len(frame) == 20 and frame.startswith("5A5A"):
                logger.info(f"  ✓ Frame format OK")
            else:
                logger.error(f"  ✗ Invalid frame format")
        
        # Test RS485 controller
        logger.info("Testing RS485 controller...")
        controller = RS485Controller()
        
        # Test connection status
        logger.info(f"Controller connected: {controller.connected}")
        logger.info(f"Mock mode: {controller.connected == False and 'Yes' or 'No'}")
        
        # Test opening a locker
        logger.info("Testing locker opening...")
        result = controller.open_locker(1)
        
        logger.info(f"Open result: {result.get('success')}")
        logger.info(f"Frame used: {result.get('frame')}")
        logger.info(f"Message: {result.get('message')}")
        
        logger.info("✓ RS485 utilities test completed")
        return True
        
    except ImportError as e:
        logger.error(f"Import error: {e}")
        return False
    except Exception as e:
        logger.error(f"Error testing RS485 utilities: {e}")
        return False

def test_environment_configuration():
    """Test environment configuration"""
    logger.info("=== TESTING ENVIRONMENT CONFIGURATION ===")
    
    # Check RS485 mode
    rs485_mode = os.environ.get("RS485_MOCK_MODE", "Not set")
    logger.info(f"RS485_MOCK_MODE: {rs485_mode}")
    
    if rs485_mode.lower() == "true":
        logger.warning("⚠️  RS485 is in MOCK MODE - no real hardware communication")
    else:
        logger.info("✓ RS485 is in REAL HARDWARE MODE")
    
    # Check other environment variables
    env_vars = [
        "DATABASE_URL",
        "DB_HOST", 
        "DB_PORT",
        "DB_NAME",
        "DB_USER"
    ]
    
    for var in env_vars:
        value = os.environ.get(var, "Not set")
        logger.info(f"{var}: {value}")
    
    logger.info("✓ Environment configuration test completed")
    return True

def main():
    """Main test function"""
    logger.info("Smart Locker System - RS485 Hardware Test")
    logger.info("==========================================")
    logger.info("This script tests RS485 hardware connectivity")
    logger.info("")
    
    # Run all tests
    tests = [
        ("Dependencies", check_dependencies),
        ("Serial Ports", check_serial_ports),
        ("Environment", test_environment_configuration),
        ("RS485 Utilities", test_rs485_utils),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info("")
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            logger.error(f"Test {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Test RS485 connection if ports are available
    ports = check_serial_ports()
    if "/dev/ttyUSB0" in ports:
        logger.info("")
        results["RS485 Connection"] = test_rs485_connection("/dev/ttyUSB0")
    else:
        logger.warning("")
        logger.warning("⚠️  /dev/ttyUSB0 not found - skipping RS485 connection test")
        logger.warning("   This is normal if RS485 hardware is not connected")
        results["RS485 Connection"] = "Skipped"
    
    # Summary
    logger.info("")
    logger.info("=== TEST SUMMARY ===")
    for test_name, result in results.items():
        if result == True:
            logger.info(f"✓ {test_name}: PASSED")
        elif result == False:
            logger.error(f"✗ {test_name}: FAILED")
        else:
            logger.warning(f"⚠️  {test_name}: {result}")
    
    # Recommendations
    logger.info("")
    logger.info("=== RECOMMENDATIONS ===")
    
    if results.get("Dependencies") == False:
        logger.error("Install missing dependencies before proceeding")
    
    if results.get("RS485 Connection") == False:
        logger.error("RS485 hardware connection failed")
        logger.info("Check:")
        logger.info("  - Hardware is properly connected")
        logger.info("  - USB-to-RS485 converter is working")
        logger.info("  - Port permissions (may need sudo)")
        logger.info("  - No other application is using the port")
    
    if results.get("RS485 Connection") == "Skipped":
        logger.info("To test real RS485 hardware:")
        logger.info("  1. Connect USB-to-RS485 converter")
        logger.info("  2. Run: ls /dev/ttyUSB*")
        logger.info("  3. Run this script again")
    
    logger.info("")
    logger.info("For production deployment:")
    logger.info("  - Ensure RS485_MOCK_MODE is not set to 'true'")
    logger.info("  - Verify hardware connections")
    logger.info("  - Test with actual locker hardware")
    logger.info("  - Check system logs for RS485 communication")

if __name__ == "__main__":
    main() 