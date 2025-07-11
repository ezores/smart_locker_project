try:
    import evdev  # type: ignore[import]

    EVDEV_AVAILABLE = True
except ImportError:
    EVDEV_AVAILABLE = False
    print("[INFO] evdev not available - using mock RFID for development")


def read_rfid():
    if EVDEV_AVAILABLE:
        # Real RFID reading logic for Raspberry Pi
        # This would scan for RFID devices and read tags
        print("[REAL] Reading RFID tag...")
        return "REAL_RFID_TAG"
    else:
        # Mock RFID for MacBook development
        print("[MOCK] Reading RFID tag...")
        return "FAKE_RFID_TAG"


def get_rfid_devices():
    """Get list of available RFID devices"""
    if EVDEV_AVAILABLE:
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        return [
            d for d in devices if "rfid" in d.name.lower() or "card" in d.name.lower()
        ]
    else:
        return []
