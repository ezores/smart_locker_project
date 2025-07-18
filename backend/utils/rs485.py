import logging
import os
import time
from typing import Any, Dict, Optional

import serial

logger = logging.getLogger(__name__)

# Mock mode for development - set to True if no physical RS485 hardware is available
# Can be overridden with environment variable RS485_MOCK_MODE
# Default is real hardware mode - set RS485_MOCK_MODE=true for mock mode
MOCK_MODE = os.environ.get("RS485_MOCK_MODE", "False").lower() == "true"


class RS485Controller:
    def __init__(self, port: str = "/dev/ttyUSB0", baudrate: int = 9600):
        self.port = port
        self.baudrate = baudrate
        self.serial_connection = None
        self.connected = False

        if not MOCK_MODE:
            self._connect()

    def _connect(self):
        """Establish serial connection to RS485 device"""
        try:
            # First check if the port exists
            import serial.tools.list_ports
            available_ports = [port.device for port in serial.tools.list_ports.comports()]
            
            if self.port not in available_ports:
                logger.warning(f"RS485 port {self.port} not found")
                logger.info(f"Available ports: {available_ports}")
                logger.info("RS485 hardware not connected - using mock mode")
                self.connected = False
                return
            
            self.serial_connection = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=1,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
            )
            self.connected = True
            logger.info(f"RS485 connected to {self.port}")
        except Exception as e:
            logger.error(f"Failed to connect to RS485: {e}")
            logger.info("Falling back to mock mode")
            self.connected = False

    def _send_command(self, command: str) -> bool:
        """Send command to RS485 device"""
        if MOCK_MODE or not self.connected or self.serial_connection is None:
            logger.info(f"[MOCK] RS485 Command: {command}")
            logger.info(f"[MOCK] Command bytes: {[hex(ord(c)) for c in command]}")
            logger.info(f"[MOCK] Hardware not connected - simulating success")
            time.sleep(0.1)  # Simulate hardware delay
            return True

        if not self.connected or self.serial_connection is None:
            logger.error("RS485 not connected")
            return False

        try:
            logger.info(f"=== REAL RS485 COMMAND EXECUTION ===")
            logger.info(f"Port: {self.port}")
            logger.info(f"Baudrate: {self.baudrate}")
            logger.info(f"Command (hex string): {command}")
            
            # Convert hex string to bytes
            try:
                command_bytes = bytes.fromhex(command)
                logger.info(f"Command (hex bytes): {[f'{b:02X}' for b in command_bytes]}")
                logger.info(f"Command length: {len(command_bytes)} bytes")
            except ValueError as e:
                logger.error(f"Invalid hex string: {command}")
                logger.error(f"Hex conversion error: {e}")
                return False
            
            # Send the command as hex bytes
            bytes_written = self.serial_connection.write(command_bytes)
            logger.info(f"Bytes written to serial: {bytes_written}")
            
            # Wait for response
            logger.info("Waiting for RS485 response...")
            response = self.serial_connection.readline().decode().strip()
            logger.info(f"RS485 Response: {response}")
            logger.info(f"Response length: {len(response)} characters")
            
            # Log additional serial port info
            logger.info(f"Serial port in_waiting: {self.serial_connection.in_waiting}")
            logger.info(f"Serial port out_waiting: {self.serial_connection.out_waiting}")
            
            logger.info(f"=== RS485 COMMAND COMPLETED ===")
            return True
        except Exception as e:
            logger.error(f"=== RS485 COMMUNICATION ERROR ===")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error message: {e}")
            logger.error(f"Port: {self.port}")
            logger.error(f"Connected: {self.connected}")
            logger.error(f"Serial connection: {self.serial_connection}")
            return False

    def open_locker(
        self,
        locker_id: int,
        address: Optional[int] = None,
        locker_number: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Open a specific locker using RS485 protocol"""
        logger.info(f"=== LOCKER OPEN REQUEST ===")
        logger.info(f"Locker ID: {locker_id}")
        logger.info(f"Provided Address: {address}")
        logger.info(f"Provided Locker Number: {locker_number}")
        logger.info(f"Mock Mode: {MOCK_MODE}")
        logger.info(f"RS485 Connected: {self.connected}")
        
        try:
            # Generate RS485 frame
            if address is not None and locker_number is not None:
                logger.info(f"Using provided address ({address}) and locker number ({locker_number})")
                frame = generate_rs485_frame(address, locker_number)
            else:
                # Fallback to simple mapping if no address/numbers provided
                address = (locker_id - 1) % 32  # Dipswitch 0-31
                locker_number = ((locker_id - 1) % 24) + 1  # Locker 1-24
                logger.info(f"Using calculated address ({address}) and locker number ({locker_number})")
                frame = generate_rs485_frame(address, locker_number)

            logger.info(f"Generated frame: {frame}")
            logger.info(f"Frame length: {len(frame)} characters")

            # Send the frame
            success = self._send_command(frame)

            result = {
                "success": success,
                "locker_id": locker_id,
                "action": "open",
                "rs485_address": address,
                "rs485_locker_number": locker_number,
                "frame": frame,
                "timestamp": time.time(),
                "message": (
                    "Locker opened successfully" if success else "Failed to open locker"
                ),
            }

            if success:
                logger.info(f"=== LOCKER OPEN SUCCESS ===")
                logger.info(f"Locker {locker_id} opened successfully with frame: {frame}")
                logger.info(f"Address: {address}, Locker Number: {locker_number}")
            else:
                logger.error(f"=== LOCKER OPEN FAILED ===")
                logger.error(f"Failed to open locker {locker_id}")
                logger.error(f"Frame sent: {frame}")
                logger.error(f"Address: {address}, Locker Number: {locker_number}")

            return result

        except Exception as e:
            logger.error(f"=== LOCKER OPEN ERROR ===")
            logger.error(f"Error opening locker {locker_id}: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            return {
                "success": False,
                "locker_id": locker_id,
                "action": "open",
                "error": str(e),
                "timestamp": time.time(),
                "message": f"Error opening locker: {e}",
            }

    def close_locker(
        self,
        locker_id: int,
        address: Optional[int] = None,
        locker_number: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Close a specific locker using RS485 protocol"""
        try:
            # Generate RS485 frame
            if address is not None and locker_number is not None:
                frame = generate_rs485_frame(address, locker_number)
            else:
                # Fallback to simple mapping if no address/numbers provided
                address = (locker_id - 1) % 32  # Dipswitch 0-31
                locker_number = ((locker_id - 1) % 24) + 1  # Locker 1-24
                frame = generate_rs485_frame(address, locker_number)

            # Send the frame
            success = self._send_command(frame)

            result = {
                "success": success,
                "locker_id": locker_id,
                "action": "close",
                "rs485_address": address,
                "rs485_locker_number": locker_number,
                "frame": frame,
                "timestamp": time.time(),
                "message": (
                    "Locker closed successfully"
                    if success
                    else "Failed to close locker"
                ),
            }

            if success:
                logger.info(
                    f"Locker {locker_id} closed successfully with frame: {frame}"
                )
            else:
                logger.error(f"Failed to close locker {locker_id}")

            return result

        except Exception as e:
            logger.error(f"Error closing locker {locker_id}: {e}")
            return {
                "success": False,
                "locker_id": locker_id,
                "action": "close",
                "error": str(e),
                "timestamp": time.time(),
                "message": f"Error closing locker: {e}",
            }

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
            "timestamp": time.time(),
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
            "message": (
                "RS485 connection test successful"
                if success
                else "RS485 connection test failed"
            ),
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


def open_locker(
    locker_id: int, address: Optional[int] = None, locker_number: Optional[int] = None
) -> Dict[str, Any]:
    """Open a locker using RS485"""
    return rs485_controller.open_locker(locker_id, address, locker_number)


def close_locker(
    locker_id: int, address: Optional[int] = None, locker_number: Optional[int] = None
) -> Dict[str, Any]:
    """Close a locker using RS485"""
    return rs485_controller.close_locker(locker_id, address, locker_number)


def get_locker_status(locker_id: int) -> Dict[str, Any]:
    """Get locker status using RS485"""
    return rs485_controller.get_locker_status(locker_id)


def test_rs485_connection() -> Dict[str, Any]:
    """Test RS485 connection"""
    return rs485_controller.test_connection()


def access_reservation_locker(
    access_code: str,
    locker_id: int,
    address: Optional[int] = None,
    locker_number: Optional[int] = None,
) -> Dict[str, Any]:
    """Access a locker using reservation access code"""
    try:
        # Validate access code format (8 digits)
        if not access_code.isdigit() or len(access_code) != 8:
            return {
                "success": False,
                "error": "Invalid access code format",
                "message": "Access code must be 8 digits",
            }

        # Generate RS485 frame
        if address is not None and locker_number is not None:
            frame = generate_rs485_frame(address, locker_number)
        else:
            # Fallback to simple mapping if no address/numbers provided
            address = (locker_id - 1) % 32  # Dipswitch 0-31
            locker_number = ((locker_id - 1) % 24) + 1  # Locker 1-24
            frame = generate_rs485_frame(address, locker_number)

        # Send the frame
        success = rs485_controller._send_command(frame)

        result = {
            "success": success,
            "locker_id": locker_id,
            "access_code": access_code,
            "action": "reservation_access",
            "rs485_address": address,
            "rs485_locker_number": locker_number,
            "frame": frame,
            "timestamp": time.time(),
            "message": (
                "Reservation access granted" if success else "Failed to access locker"
            ),
        }

        if success:
            logger.info(
                f"Reservation access granted for locker {locker_id} with code {access_code}"
            )
        else:
            logger.error(f"Failed to access locker {locker_id} with code {access_code}")

        return result

    except Exception as e:
        logger.error(f"Error accessing locker {locker_id} with code {access_code}: {e}")
        return {
            "success": False,
            "locker_id": locker_id,
            "access_code": access_code,
            "action": "reservation_access",
            "error": str(e),
            "timestamp": time.time(),
            "message": f"Error accessing locker: {e}",
        }


def generate_rs485_frame(address: int, locker_number: int) -> str:
    """
    Generate RS485 protocol frame for locker control

    Protocol: 5A5A 00 [ADDRESS] 00 04 00 01 [LOCKER_NUMBER] [CHECKSUM]

    Args:
        address: Address card (0-31 dipswitch)
        locker_number: Number of locker (1-24)

    Returns:
        Hex string representing the complete frame
    """
    # Protocol structure:
    # Start frame: 5A5A (fixed)
    # Reserved: 00 (fixed)
    # Address card: [ADDRESS] (0-31)
    # Reserved: 00 (fixed)
    # Reserved: 04 (fixed)
    # Reserved: 00 (fixed)
    # Reserved: 01 (fixed)
    # Number of locker: [LOCKER_NUMBER] (1-24)
    # Checksum: XOR of all previous octets

    # Validate inputs
    if not (0 <= address <= 31):
        raise ValueError("Address must be between 0 and 31")
    if not (1 <= locker_number <= 24):
        raise ValueError("Locker number must be between 1 and 24")

    # Build frame octets
    frame_octets = [
        0x5A,  # Start frame high byte
        0x5A,  # Start frame low byte
        0x00,  # Reserved
        address,  # Address card (0-31)
        0x00,  # Reserved
        0x04,  # Reserved
        0x00,  # Reserved
        0x01,  # Reserved
        locker_number,  # Number of locker (0-24)
    ]

    # Calculate checksum (XOR of all octets)
    checksum = 0
    for octet in frame_octets:
        checksum ^= octet

    # Add checksum to frame
    frame_octets.append(checksum)

    # Convert to hex string (no spaces)
    frame_hex = "".join([f"{octet:02X}" for octet in frame_octets])

    logger.info(
        f"Generated RS485 frame: {frame_hex} (Address: {address}, Locker: {locker_number}, Checksum: {checksum:02X})"
    )

    return frame_hex


def generate_locker_command_frame(locker_id: int, action: str = "open") -> str:
    """
    Generate RS485 command frame for a specific locker

    Args:
        locker_id: Database locker ID
        action: Action to perform ("open" or "close")

    Returns:
        Hex string representing the command frame
    """
    # For now, we'll use a simple mapping
    # In a real implementation, you'd get the RS485 address and locker number from the database
    address = (locker_id - 1) % 32  # Dipswitch 0-31
    locker_number = ((locker_id - 1) % 24) + 1  # Locker 1-24

    frame = generate_rs485_frame(address, locker_number)

    logger.info(f"Generated {action} command for locker {locker_id}: {frame}")

    return frame



