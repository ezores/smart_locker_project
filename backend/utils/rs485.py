import serial
import time
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Mock mode for development
MOCK_MODE = True

class RS485Controller:
    def __init__(self, port: str = '/dev/ttyUSB0', baudrate: int = 9600):
        self.port = port
        self.baudrate = baudrate
        self.serial_connection = None
        self.connected = False
        
        if not MOCK_MODE:
            self._connect()
    
    def _connect(self):
        """Establish serial connection to RS485 device"""
        try:
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            self.connected = True
            logger.info(f"RS485 connected to {self.port}")
        except Exception as e:
            logger.error(f"Failed to connect to RS485: {e}")
            self.connected = False
    
    def _send_command(self, command: str) -> bool:
        """Send command to RS485 device"""
        if MOCK_MODE:
            logger.info(f"[MOCK] RS485 Command: {command}")
            time.sleep(0.1)  # Simulate hardware delay
            return True
        
        if not self.connected or self.serial_connection is None:
            logger.error("RS485 not connected")
            return False
        
        try:
            self.serial_connection.write(command.encode())
            response = self.serial_connection.readline().decode().strip()
            logger.info(f"RS485 Response: {response}")
            return True
        except Exception as e:
            logger.error(f"RS485 communication error: {e}")
            return False
    
    def open_locker(self, locker_id: int) -> Dict[str, Any]:
        """Open a specific locker"""
        command = f"OPEN:{locker_id:03d}\n"
        success = self._send_command(command)
        
        result = {
            "success": success,
            "locker_id": locker_id,
            "action": "open",
            "timestamp": time.time(),
            "message": "Locker opened successfully" if success else "Failed to open locker"
        }
        
        if success:
            logger.info(f"Locker {locker_id} opened successfully")
        else:
            logger.error(f"Failed to open locker {locker_id}")
        
        return result
    
    def close_locker(self, locker_id: int) -> Dict[str, Any]:
        """Close a specific locker"""
        command = f"CLOSE:{locker_id:03d}\n"
        success = self._send_command(command)
        
        result = {
            "success": success,
            "locker_id": locker_id,
            "action": "close",
            "timestamp": time.time(),
            "message": "Locker closed successfully" if success else "Failed to close locker"
        }
        
        if success:
            logger.info(f"Locker {locker_id} closed successfully")
        else:
            logger.error(f"Failed to close locker {locker_id}")
        
        return result
    
    def get_locker_status(self, locker_id: int) -> Dict[str, Any]:
        """Get status of a specific locker"""
        command = f"STATUS:{locker_id:03d}\n"
        success = self._send_command(command)
        
        # Mock status response
        if MOCK_MODE:
            status = "closed"  # Mock status
        else:
            status = "unknown"
        
        result = {
            "success": success,
            "locker_id": locker_id,
            "status": status,
            "timestamp": time.time()
        }
        
        return result
    
    def test_connection(self) -> Dict[str, Any]:
        """Test RS485 connection"""
        command = "TEST\n"
        success = self._send_command(command)
        
        result = {
            "success": success,
            "connected": self.connected,
            "port": self.port,
            "baudrate": self.baudrate,
            "mock_mode": MOCK_MODE,
            "message": "RS485 connection test successful" if success else "RS485 connection test failed"
        }
        
        return result
    
    def disconnect(self):
        """Close serial connection"""
        if self.serial_connection and self.connected:
            self.serial_connection.close()
            self.connected = False
            logger.info("RS485 connection closed")

# Global RS485 controller instance
rs485_controller = RS485Controller()

def open_locker(locker_id: int) -> Dict[str, Any]:
    """Open a locker using RS485"""
    return rs485_controller.open_locker(locker_id)

def close_locker(locker_id: int) -> Dict[str, Any]:
    """Close a locker using RS485"""
    return rs485_controller.close_locker(locker_id)

def get_locker_status(locker_id: int) -> Dict[str, Any]:
    """Get locker status using RS485"""
    return rs485_controller.get_locker_status(locker_id)

def test_rs485_connection() -> Dict[str, Any]:
    """Test RS485 connection"""
    return rs485_controller.test_connection() 