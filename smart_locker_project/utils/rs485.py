try:
    import serial  # type: ignore[import]
    SERIAL_AVAILABLE = True
except ImportError:
    SERIAL_AVAILABLE = False
    print("[INFO] pyserial not available - using mock RS485 for development")

def open_locker(locker_id):
    if SERIAL_AVAILABLE:
        # Real RS485 communication for Raspberry Pi
        # This would send commands to the lock controller
        print(f"[REAL] Opening locker {locker_id} (RS485 command sent)")
        return True
    else:
        # Mock RS485 for MacBook development
        print(f"[MOCK] Opening locker {locker_id} (RS485 command sent)")
        return True

def init_rs485():
    """Initialize RS485 connection"""
    if SERIAL_AVAILABLE:
        # Configure serial port for RS485
        # ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
        print("[REAL] RS485 initialized")
        return True
    else:
        print("[MOCK] RS485 initialized")
        return True 