import time

from typing import Optional
from ctypes import windll, create_unicode_buffer


def getForegroundWindowTitle() -> Optional[str]:
    hWnd = windll.user32.GetForegroundWindow()
    length = windll.user32.GetWindowTextLengthW(hWnd)
    buf = create_unicode_buffer(length + 1)
    windll.user32.GetWindowTextW(hWnd, buf, length + 1)

    return buf.value if buf.value else None


while True:
    active_window = getForegroundWindowTitle()

    if active_window == "ELDEN RING™":
        print("ELDEN RING is running")

    time.sleep(5)
