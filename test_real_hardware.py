#!/usr/bin/env python3
"""
Real Hardware Test Script
This script tests the real RS485 hardware with the current configuration.
The system is now configured to use real hardware by default.
"""

import os
import sys
import time
import logging
from datetime import datetime

# Add backend to path
sys.path.append('backend')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_real_hardware():
    """Test real RS485 hardware with current configuration"""
    
    logger.info("=== REAL HARDWARE TEST ===")
    logger.info(f"Test started at: {datetime.now()}")
    logger.info(f"RS485_MOCK_MODE: {os.environ.get('RS485_MOCK_MODE', 'Not set')}")
    
    try:
        from backend.utils.rs485 import RS485Controller, generate_rs485_frame, test_rs485_connection
        
        # Test connection
        logger.info("Testing RS485 connection...")
        connection_result = test_rs485_connection()
        logger.info(f"Connection test result: {connection_result}")
        
        # Create controller
        controller = RS485Controller()
        logger.info(f"Controller created. Connected: {controller.connected}")
        logger.info(f"Port: {controller.port}")
        logger.info(f"Baudrate: {controller.baudrate}")
        
        if not controller.connected:
            logger.error("RS485 controller is not connected!")
            logger.error("Please check:")
            logger.error("1. USB-to-RS485 converter is connected")
            logger.error("2. Device is on /dev/ttyUSB0")
            logger.error("3. User has permission to access the device")
            return False
        
        # Test specific locker opening
        test_cases = [
            {"locker_id": 1, "address": 0, "locker_number": 1},
            {"locker_id": 2, "address": 1, "locker_number": 2},
        ]
        
        for test_case in test_cases:
            logger.info(f"\n=== TESTING LOCKER {test_case['locker_id']} ===")
            logger.info(f"Address: {test_case['address']}, Locker Number: {test_case['locker_number']}")
            
            # Generate frame
            frame = generate_rs485_frame(test_case['address'], test_case['locker_number'])
            logger.info(f"Generated frame: {frame}")
            
            # Test opening
            result = controller.open_locker(
                test_case['locker_id'],
                address=test_case['address'],
                locker_number=test_case['locker_number']
            )
            
            logger.info(f"Open result: {result}")
            
            # Wait between tests
            time.sleep(2)
        
        logger.info("\n=== REAL HARDWARE TEST COMPLETED ===")
        logger.info("Check the logs above for detailed information")
        return True
        
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = test_real_hardware()
    if success:
        print("\nReal hardware test completed successfully!")
        print("You can now use the 'Open Locker (Real)' button in the web interface.")
    else:
        print("\nReal hardware test failed!")
        print("Please check the hardware connection and try again.") 