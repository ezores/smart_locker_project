#!/usr/bin/env python3
"""
RS485 Real Hardware Test Script
This script helps test real RS485 hardware with comprehensive logging.
Run this script when you want to test locker opening with real hardware.
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
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('rs485_test.log')
    ]
)

logger = logging.getLogger(__name__)

def test_rs485_real():
    """Test RS485 real hardware functionality"""
    
    # Set environment for real hardware
    os.environ['RS485_MOCK_MODE'] = 'false'
    
    logger.info("=== RS485 REAL HARDWARE TEST ===")
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
        
        # Test specific locker opening
        test_cases = [
            {"locker_id": 1, "address": 0, "locker_number": 1},
            {"locker_id": 2, "address": 1, "locker_number": 2},
            {"locker_id": 3, "address": 2, "locker_number": 3},
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
        
        logger.info("\n=== RS485 TEST COMPLETED ===")
        logger.info("Check the logs above for detailed information")
        logger.info("Check rs485_test.log file for complete log")
        
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")

if __name__ == "__main__":
    test_rs485_real() 