#!/usr/bin/env python3
"""
Simple Locker Opening Test Script
This script tests opening a specific locker with real RS485 hardware.
Run this when you want to test opening a specific locker.
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

def test_open_locker(locker_id, address=None, locker_number=None):
    """Test opening a specific locker"""
    
    # Set environment for real hardware
    os.environ['RS485_MOCK_MODE'] = 'false'
    
    logger.info("=== LOCKER OPENING TEST ===")
    logger.info(f"Test started at: {datetime.now()}")
    logger.info(f"Locker ID: {locker_id}")
    logger.info(f"Address: {address}")
    logger.info(f"Locker Number: {locker_number}")
    logger.info(f"RS485_MOCK_MODE: {os.environ.get('RS485_MOCK_MODE', 'Not set')}")
    
    try:
        from backend.utils.rs485 import open_locker, generate_rs485_frame
        
        # Generate frame for logging
        if address is not None and locker_number is not None:
            frame = generate_rs485_frame(address, locker_number)
            logger.info(f"Expected frame: {frame}")
        
        # Test opening the locker
        logger.info("Attempting to open locker...")
        result = open_locker(locker_id, address=address, locker_number=locker_number)
        
        logger.info("=== RESULT ===")
        logger.info(f"Success: {result.get('success', False)}")
        logger.info(f"Message: {result.get('message', 'No message')}")
        logger.info(f"Frame used: {result.get('frame', 'No frame')}")
        logger.info(f"Address used: {result.get('rs485_address', 'Not set')}")
        logger.info(f"Locker number used: {result.get('rs485_locker_number', 'Not set')}")
        
        if result.get('error'):
            logger.error(f"Error: {result.get('error')}")
        
        return result
        
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_locker_opening.py <locker_id> [address] [locker_number]")
        print("Example: python test_locker_opening.py 1 0 1")
        print("Example: python test_locker_opening.py 2 1 2")
        sys.exit(1)
    
    locker_id = int(sys.argv[1])
    address = int(sys.argv[2]) if len(sys.argv) > 2 else None
    locker_number = int(sys.argv[3]) if len(sys.argv) > 3 else None
    
    test_open_locker(locker_id, address, locker_number) 