import time
from pynput.keyboard import Controller, Key, KeyCode

keyboard = Controller()

# Space key constant for Linux
SPACE_KEY = ' '


def _to_keycode(key):
    """Convert common representations to a pynput Key or KeyCode."""
    if isinstance(key, Key):
        return key
    if isinstance(key, str):
        if len(key) == 1:
            return KeyCode.from_char(key)
        return getattr(Key, key, KeyCode.from_char(key))
    if isinstance(key, int):
        try:
            return KeyCode.from_char(chr(key))
        except ValueError:
            return KeyCode.from_vk(key)
    return key


def PressKey(key):
    """Press a key on Linux."""
    keyboard.press(_to_keycode(key))


def ReleaseKey(key):
    """Release a key on Linux."""
    keyboard.release(_to_keycode(key))


if __name__ == "__main__":
    print("Pressing space...")
    PressKey(SPACE_KEY)
    time.sleep(1)
    print("Releasing space...")
    ReleaseKey(SPACE_KEY)
    time.sleep(1)
