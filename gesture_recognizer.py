import cv2
import mediapipe as mp
import numpy as np
from collections import deque

class GestureRecognizer:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.detector = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.8,
            min_tracking_confidence=0.8
        )
        self.position_history = deque(maxlen=12)

    def process(self, rgb_frame):
        return self.detector.process(rgb_frame)

    def get_landmarks(self, results, frame_shape):
        if not results.multi_hand_landmarks:
            return None, None
        h, w = frame_shape[:2]
        hand = results.multi_hand_landmarks[0]
        coords = [(int(lm.x * w), int(lm.y * h)) for lm in hand.landmark]
        return hand, coords

    def fingers_up(self, coords):
        tips = [8, 12, 16, 20]
        fingers = [1 if coords[tip][1] < coords[tip - 2][1] else 0 for tip in tips]
        thumb = 1 if abs(coords[4][0] - coords[2][0]) > 40 else 0
        return [thumb] + fingers

    def detect_gesture(self, coords):
        if coords is None:
            self.position_history.clear()
            return None, None

        fingers   = self.fingers_up(coords)
        index_up  = fingers[1]
        middle_up = fingers[2]
        ring_up   = fingers[3]
        pinky_up  = fingers[4]
        thumb_up  = fingers[0]
        non_thumb = [index_up, middle_up, ring_up, pinky_up]

        self.position_history.append((coords[0][0], coords[0][1]))

        if sum(non_thumb) == 4:
            return "PLAY_PAUSE", None
        if sum(non_thumb) == 0 and not thumb_up:
            return "MUTE_TOGGLE", None
        if index_up and not middle_up and not ring_up and not pinky_up and not thumb_up:
            return "VOLUME", None
        if index_up and middle_up and not ring_up and not pinky_up and not thumb_up:
            return "BRIGHTNESS", None
        if thumb_up and not index_up and not middle_up and not ring_up and not pinky_up:
            return "PREV_TRACK", None
        if pinky_up and not index_up and not middle_up and not ring_up and not thumb_up:
            return "NEXT_TRACK", None
        if index_up and middle_up and ring_up and not thumb_up and not pinky_up:
            return "SCREENSHOT", None
        return None, None

    def draw_landmarks(self, frame, hand_landmarks):
        h, w = frame.shape[:2]
        coords = [(int(lm.x * w), int(lm.y * h)) for lm in hand_landmarks.landmark]
        connections = [
            (0,1),(1,2),(2,3),(3,4),(0,5),(5,6),(6,7),(7,8),
            (5,9),(9,10),(10,11),(11,12),(9,13),(13,14),(14,15),
            (15,16),(13,17),(17,18),(18,19),(19,20),(0,17)
        ]
        for a, b in connections:
            cv2.line(frame, coords[a], coords[b], (0, 200, 0), 2)
        for cx, cy in coords:
            cv2.circle(frame, (cx, cy), 4, (0, 255, 0), cv2.FILLED)