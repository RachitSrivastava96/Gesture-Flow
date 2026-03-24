import numpy as np
import screen_brightness_control as sbc
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from pycaw.utils import AudioUtilities as AU
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL

class SystemController:
    def __init__(self):
        devices = AudioUtilities.GetSpeakers()
        # Newer pycaw: access the COM interface via _dev, then Activate
        interface = devices._dev.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = cast(interface, POINTER(IAudioEndpointVolume))
        self.vol_range = self.volume.GetVolumeRange()
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