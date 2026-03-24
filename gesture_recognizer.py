import mediapipe as mp
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

mp_draw = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands
class GestureRecognizer:
    def __init__(self):
        self.hands = mp_hands.Hands(
            max_num_hands=1,
            min_detection_confidence=0.8,
            min_tracking_confidence=0.8
        )
        self.gesture_buffer = []

    def process(self, rgb_frame):
        return self.hands.process(rgb_frame)

    def get_landmarks(self, results, frame_shape):
        if not results.multi_hand_landmarks:
            return None, None
        hand = results.multi_hand_landmarks[0]
        h, w = frame_shape[:2]
        coords = [(int(lm.x * w), int(lm.y * h)) for lm in hand.landmark]
        return hand, coords

    # --- Finger State ---
    def fingers_up(self, coords):
        tips = [8, 12, 16, 20]
        fingers = [1 if coords[tip][1] < coords[tip - 2][1] else 0 for tip in tips]
        thumb = 1 if coords[4][0] > coords[3][0] else 0
        return [thumb] + fingers

    # --- Gesture Detection ---
    def detect_gesture(self, coords):
        if coords is None:
            return None

        fingers = self.fingers_up(coords)
        index_up   = fingers[1]
        middle_up  = fingers[2]
        ring_up    = fingers[3]
        pinky_up   = fingers[4]
        thumb_up   = fingers[0]

        # Open palm — all fingers up
        if all(f == 1 for f in fingers):
            return "MUTE_TOGGLE"

        # Fist — all fingers down
        if all(f == 0 for f in fingers):
            return "PLAY_PAUSE"

        # Index only — volume control
        if index_up and not middle_up and not ring_up and not pinky_up:
            return "VOLUME"

        # Index + middle — brightness control
        if index_up and middle_up and not ring_up and not pinky_up:
            return "BRIGHTNESS"

        # Thumb only — previous track
        if thumb_up and not index_up and not middle_up and not ring_up and not pinky_up:
            return "PREV_TRACK"

        # Pinky only — next track
        if pinky_up and not index_up and not middle_up and not ring_up and not thumb_up:
            return "NEXT_TRACK"

        return None

    def draw_landmarks(self, frame, hand_landmarks):
        mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)