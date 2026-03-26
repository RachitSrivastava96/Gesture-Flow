import numpy as np
import pyautogui
import screen_brightness_control as sbc
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
import time
import os

class SystemController:
    def __init__(self):
        devices = AudioUtilities.GetSpeakers()
        interface = devices._dev.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(interface, POINTER(IAudioEndpointVolume))
        self.vol_range = self.volume.GetVolumeRange()
        self.muted = False
        # Cache the first available display identifier for sbc
        monitors = sbc.list_monitors()
        self._display = monitors[0] if monitors else 0

    # --- Volume ---
    def set_volume(self, level):
        level = np.clip(level, 0, 100)
        min_dB, max_dB, _ = self.vol_range
        self.volume.SetMasterVolumeLevel(min_dB + (max_dB - min_dB) * (level / 100), None)

    def get_volume(self):
        min_dB, max_dB, _ = self.vol_range
        return int((self.volume.GetMasterVolumeLevel() - min_dB) / (max_dB - min_dB) * 100)

    # --- Brightness ---
    def set_brightness(self, level):
        level = int(np.clip(level, 10, 100))
        try:
            sbc.set_brightness(level, display=self._display)
        except Exception:
            sbc.set_brightness(level)

    def get_brightness(self):
        try:
            result = sbc.get_brightness(display=self._display)
        except Exception:
            result = sbc.get_brightness()
        # sbc may return int, [int], or [[int]] depending on driver
        while isinstance(result, (list, tuple)):
            result = result[0]
        return int(result)

    # --- Media ---
    def play_pause(self):  pyautogui.press('playpause')
    def next_track(self):  pyautogui.press('nexttrack')
    def prev_track(self):  pyautogui.press('prevtrack')

    # --- Mute ---
    def toggle_mute(self):
        self.muted = not self.muted
        self.volume.SetMute(self.muted, None)
        return self.muted

    # --- Screenshot ---
    def take_screenshot(self):
        folder = os.path.join("C:\\GestureFlow", "Screenshots")
        os.makedirs(folder, exist_ok=True)
        filename = os.path.join(folder, f"screenshot_{int(time.time())}.png")
        img = pyautogui.screenshot()
        img.save(filename)
        print(f"Screenshot saved: {filename}")