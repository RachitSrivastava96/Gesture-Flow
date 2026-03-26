import cv2
import numpy as np
import time

GESTURE_META = {
    "VOLUME":      ("Volume",          (0, 220, 120),    "☝ Index up/down"),
    "BRIGHTNESS":  ("Brightness",      (80, 180, 255),   "✌ Two fingers up/down"),
    "PLAY_PAUSE":  ("Play / Pause",    (180, 100, 255),  "🖐 Open palm"),
    "MUTE_TOGGLE": ("Mute Toggle",     (255, 80,  80),   "✊ Fist"),
    "NEXT_TRACK":  ("Next Track",      (180, 100, 255),  "🤙 Pinky only"),
    "PREV_TRACK":  ("Prev Track",      (180, 100, 255),  "👍 Thumb only"),
    "SCREENSHOT":  ("Screenshot",      (255, 80,  80),   "👌 Thumb+Index+Middle"),
}

class Overlay:
    def __init__(self):
        self.font            = cv2.FONT_HERSHEY_SIMPLEX
        self.panel_gesture   = None
        self.panel_time      = 0
        self.PANEL_DURATION  = 2.0
        self.show_guide      = False

    # --- Core: alpha blend a filled rect ---
    def _blend(self, frame, x1, y1, x2, y2, color, alpha):
        x1,y1,x2,y2 = max(0,x1),max(0,y1),min(frame.shape[1],x2),min(frame.shape[0],y2)
        if x2<=x1 or y2<=y1: return
        roi = frame[y1:y2, x1:x2]
        overlay = np.full_like(roi, color[::-1] if len(color)==3 else color)
        cv2.addWeighted(overlay, alpha, roi, 1-alpha, 0, roi)
        frame[y1:y2, x1:x2] = roi

    # --- Rounded rect with alpha ---
    def _panel(self, frame, x1, y1, x2, y2, color=(20,20,20), alpha=0.55, r=16):
        self._blend(frame, x1+r, y1, x2-r, y2, color, alpha)
        self._blend(frame, x1, y1+r, x2, y2-r, color, alpha)
        for cx,cy in [(x1+r,y1+r),(x2-r,y1+r),(x1+r,y2-r),(x2-r,y2-r)]:
            cv2.circle(frame, (cx,cy), r, color[::-1], -1)

    # --- Glow dot ---
    def _glow(self, frame, cx, cy, color, radius=8):
        for i in range(3,0,-1):
            cv2.circle(frame, (cx,cy), radius+i*3,
                       tuple(max(0,c//3) for c in color[::-1]), -1)
        cv2.circle(frame, (cx,cy), radius, color[::-1], -1)
    
    # --- No Hand ---
    def draw_no_hand(self, frame):
        fw, fh = frame.shape[1], frame.shape[0]
        text = "No hand detected"
        scale = 1.2
        thickness = 2
        (tw, th), _ = cv2.getTextSize(text, self.font, scale, thickness)
        cx = fw // 2 - tw // 2
        cy = fh // 2 + th // 2
        self._panel(frame, cx - 24, cy - th - 20, cx + tw + 24, cy + 16, (15, 15, 15), alpha=0.6, r=14)
        cv2.putText(frame, text, (cx, cy), self.font, scale, (200, 200, 200), thickness)

    # --- Level panel (vol / brightness) ---
    def draw_level_panel(self, frame, level, label, x=40):
        fh = frame.shape[0]
        px, py, pw, ph = x, fh//2-130, 64, 260
        self._panel(frame, px, py, px+pw, py+ph, (15,15,15), alpha=0.65, r=14)
        inner_top = py+30
        inner_bot = py+ph-20
        inner_h   = inner_bot - inner_top
        fill_h    = int(inner_h * level/100)
        color     = (0,220,120) if label=="VOL" else (80,180,255)
        # track
        self._blend(frame, px+22, inner_top, px+pw-22, inner_bot, (40,40,40), 0.9)
        # fill with glow
        if fill_h > 0:
            fy = inner_bot - fill_h
            self._blend(frame, px+22, fy, px+pw-22, inner_bot, color, 0.85)
            for i in range(1,4):
                self._blend(frame, px+20, fy-i, px+pw-20, fy+2,
                            tuple(c//2 for c in color), 0.3)
        # label + value
        cv2.putText(frame, label, (px+8, py+18),
                    self.font, 0.42, (160,160,160), 1)
        cv2.putText(frame, f"{level}%", (px+6, py+ph+18),
                    self.font, 0.5, color[::-1], 1)

    # --- Toast notification ---
    def notify(self, gesture):
        if gesture and gesture != self.panel_gesture:
            self.panel_gesture = gesture
            self.panel_time    = time.time()

    def draw_gesture_panel(self, frame):
        if not self.panel_gesture: return
        elapsed = time.time() - self.panel_time
        if elapsed > self.PANEL_DURATION:
            self.panel_gesture = None
            return
        fade   = max(0.0, 1.0 - (elapsed/self.PANEL_DURATION))
        meta   = GESTURE_META.get(self.panel_gesture)
        label  = meta[0] if meta else self.panel_gesture
        color  = meta[1] if meta else (255,255,255)
        fw     = frame.shape[1]
        (tw,_),_ = cv2.getTextSize(label, self.font, 0.78, 2)
        pw, ph = tw+60, 52
        px     = fw//2 - pw//2
        py     = 24
        tmp    = frame.copy()
        self._panel(tmp, px, py, px+pw, py+ph, (18,18,18), alpha=0.72, r=14)
        # accent bar
        cv2.rectangle(tmp, (px+4, py+8), (px+8, py+ph-8), color[::-1], -1)
        cv2.putText(tmp, label, (px+18, py+34),
                    self.font, 0.78, (240,240,240), 2)
        cv2.addWeighted(tmp, fade, frame, 1-fade, 0, frame)

    # --- Gesture guide (toggle with G) ---
    def draw_guide(self, frame):
        if not self.show_guide: return
        fw, fh   = frame.shape[1], frame.shape[0]
        pw, ph   = 310, len(GESTURE_META)*44+50
        px, py   = fw-pw-20, fh//2-ph//2
        self._panel(frame, px, py, px+pw, py+ph, (12,12,12), alpha=0.78, r=18)
        cv2.putText(frame, "Gesture Guide", (px+16, py+28),
                    self.font, 0.6, (200,200,200), 1)
        cv2.line(frame, (px+12, py+36), (px+pw-12, py+36), (50,50,50), 1)
        for i,(gesture, (label, color, hint)) in enumerate(GESTURE_META.items()):
            gy = py+52+i*44
            self._glow(frame, px+20, gy+8, color, radius=6)
            cv2.putText(frame, label, (px+36, gy+13),
                        self.font, 0.52, (220,220,220), 1)
            cv2.putText(frame, hint, (px+36, gy+28),
                        self.font, 0.38, (120,120,120), 1)
        cv2.putText(frame, "Press G to close", (px+16, py+ph-10),
                    self.font, 0.35, (80,80,80), 1)

    # --- Mute badge ---
    def draw_mute_badge(self, frame, muted):
        if not muted: return
        fw = frame.shape[1]
        self._panel(frame, fw-140, 16, fw-16, 52, (180,20,20), alpha=0.75, r=12)
        cv2.putText(frame, "MUTED", (fw-124, 42),
                    self.font, 0.65, (255,255,255), 2)

    # --- FPS ---
    def draw_fps(self, frame, fps):
        cv2.putText(frame, f"FPS {fps:.0f}",
                    (frame.shape[1]-72, frame.shape[0]-12),
                    self.font, 0.42, (60,60,60), 1)

    # --- Status ---
    def draw_status(self, frame, text):
        cv2.putText(frame, text, (16, frame.shape[0]-12),
                    self.font, 0.42, (60,60,60), 1)