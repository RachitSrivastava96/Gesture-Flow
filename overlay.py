# overlay.py
import cv2
from config import UI_COLOR, WARNING_COLOR, FONT_SCALE, FONT_THICKNESS

class Overlay:
    def __init__(self):
        self.font = cv2.FONT_HERSHEY_SIMPLEX

    # --- Bar (volume/brightness) ---
    def draw_bar(self, frame, level, label, x=50, y=400):
        bar_height = int(200 * (level / 100))
        cv2.rectangle(frame, (x, y), (x + 30, y - 200), (50, 50, 50), 2)
        cv2.rectangle(frame, (x, y), (x + 30, y - bar_height), UI_COLOR, cv2.FILLED)
        cv2.putText(frame, f"{label}: {level}%", (x - 10, y + 25),
                    self.font, FONT_SCALE * 0.7, UI_COLOR, FONT_THICKNESS - 1)

    # --- Gesture label ---
    def draw_gesture(self, frame, gesture):
        if gesture:
            cv2.putText(frame, gesture, (50, 80),
                        self.font, FONT_SCALE, UI_COLOR, FONT_THICKNESS)

    # --- Mute badge ---
    def draw_mute_badge(self, frame, muted):
        if muted:
            cv2.putText(frame, "MUTED", (50, 120),
                        self.font, FONT_SCALE, WARNING_COLOR, FONT_THICKNESS)

    # --- FPS counter ---
    def draw_fps(self, frame, fps):
        cv2.putText(frame, f"FPS: {fps:.1f}", (frame.shape[1] - 120, 30),
                    self.font, FONT_SCALE * 0.7, (150, 150, 150), 1)

    # --- Status line at bottom ---
    def draw_status(self, frame, text):
        h = frame.shape[0]
        cv2.putText(frame, text, (50, h - 20),
                    self.font, FONT_SCALE * 0.7, (150, 150, 150), 1)