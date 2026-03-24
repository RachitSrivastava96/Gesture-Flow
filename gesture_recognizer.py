import cv2
import mediapipe as mp
import numpy as np
import urllib.request
import os

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

MODEL_PATH = "hand_landmarker.task"
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"

if not os.path.exists(MODEL_PATH):
    print("Downloading hand landmark model...")
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
    print("Done.")

class GestureRecognizer:
    def __init__(self):
        options = vision.HandLandmarkerOptions(
            base_options=python.BaseOptions(model_asset_path=MODEL_PATH),
            num_hands=1,
            min_hand_detection_confidence=0.8,
            min_hand_presence_confidence=0.8,
            min_tracking_confidence=0.8
        )
        self.detector = vision.HandLandmarker.create_from_options(options)

    def process(self, rgb_frame):
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        return self.detector.detect(mp_image)

    def get_landmarks(self, results, frame_shape):
        if not results.hand_landmarks:
            return None, None
        h, w = frame_shape[:2]
        hand = results.hand_landmarks[0]
        coords = [(int(lm.x * w), int(lm.y * h)) for lm in hand]
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
        index_up  = fingers[1]
        middle_up = fingers[2]
        ring_up   = fingers[3]
        pinky_up  = fingers[4]
        thumb_up  = fingers[0]

        if all(f == 1 for f in fingers):
            return "MUTE_TOGGLE"
        if all(f == 0 for f in fingers):
            return "PLAY_PAUSE"
        if index_up and not middle_up and not ring_up and not pinky_up:
            return "VOLUME"
        if index_up and middle_up and not ring_up and not pinky_up:
            return "BRIGHTNESS"
        if thumb_up and not index_up and not middle_up and not ring_up and not pinky_up:
            return "PREV_TRACK"
        if pinky_up and not index_up and not middle_up and not ring_up and not thumb_up:
            return "NEXT_TRACK"

        return None

    # --- Draw ---
    def draw_landmarks(self, frame, hand_landmarks):
        h, w = frame.shape[:2]
        coords = [(int(lm.x * w), int(lm.y * h)) for lm in hand_landmarks]

        connections = [
            (0,1),(1,2),(2,3),(3,4),
            (0,5),(5,6),(6,7),(7,8),
            (5,9),(9,10),(10,11),(11,12),
            (9,13),(13,14),(14,15),(15,16),
            (13,17),(17,18),(18,19),(19,20),(0,17)
        ]

        for a, b in connections:
            cv2.line(frame, coords[a], coords[b], (0, 200, 0), 2)
        for cx, cy in coords:
            cv2.circle(frame, (cx, cy), 4, (0, 255, 0), cv2.FILLED)