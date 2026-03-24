# system_controller.py
import screen_brightness_control as sbc
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import numpy as np

class SystemController:
    def __init__(self):
        # Audio setup
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(interface, POINTER(IAudioEndpointVolume))
        self.vol_range = self.volume.GetVolumeRange()  # (min_dB, max_dB, step)
        self.muted = False

    # --- Volume ---
    def set_volume(self, level):
        level = np.clip(level, 0, 100)
        min_dB, max_dB, _ = self.vol_range
        vol_dB = min_dB + (max_dB - min_dB) * (level / 100)
        self.volume.SetMasterVolumeLevel(vol_dB, None)

    def get_volume(self):
        min_dB, max_dB, _ = self.vol_range
        current_dB = self.volume.GetMasterVolumeLevel()
        return int((current_dB - min_dB) / (max_dB - min_dB) * 100)

    # --- Brightness ---
    def set_brightness(self, level):
        level = int(np.clip(level, 10, 100))
        sbc.set_brightness(level)

    def get_brightness(self):
        return sbc.get_brightness(display=0)[0]

    # --- Media Controls ---
    def play_pause(self):
        import pyautogui
        pyautogui.press('playpause')

    def next_track(self):
        import pyautogui
        pyautogui.press('nexttrack')

    def prev_track(self):
        import pyautogui
        pyautogui.press('prevtrack')

    # --- Mute ---
    def toggle_mute(self):
        self.muted = not self.muted
        self.volume.SetMute(self.muted, None)
        return self.muted