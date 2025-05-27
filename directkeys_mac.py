import time
from Quartz.CoreGraphics import CGEventCreateKeyboardEvent, kCGEventKeyDown, kCGEventKeyUp, CGEventPost, kCGHIDEventTap

# Define the keycode for SPACE on macOS
SPACE_KEY = 49  # macOS uses keycode 49 for Spacebar

def PressKey(macKeyCode):
    """Simulate a key press on macOS."""
    event = CGEventCreateKeyboardEvent(None, macKeyCode, True)  # True for key down
    CGEventPost(kCGHIDEventTap, event)

def ReleaseKey(macKeyCode):
    """Simulate a key release on macOS."""
    event = CGEventCreateKeyboardEvent(None, macKeyCode, False)  # False for key up
    CGEventPost(kCGHIDEventTap, event)

if __name__ == '__main__':
    print("Pressing space...")
    PressKey(SPACE_KEY)
    time.sleep(1)
    print("Releasing space...")
    ReleaseKey(SPACE_KEY)
    time.sleep(1)