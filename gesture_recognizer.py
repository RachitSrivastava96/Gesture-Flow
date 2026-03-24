# gesture_recognizer.py
import mediapipe as mp
import numpy as np
import urllib.request
import os

from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from mediapipe.framework.formats import landmark_pb2

MODEL_PATH = "hand_landmarker.task"
MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"

# Download model if not present
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
        import mediapipe as mp
        from mediapipe.framework.formats import landmark_pb2

        hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
        hand_landmarks_proto.landmark.extend([
            landmark_pb2.NormalizedLandmark(x=lm.x, y=lm.y, z=lm.z)
            for lm in hand_landmarks
        ])
        mp.solutions.drawing_utils.draw_landmarks(
            frame,
            hand_landmarks_proto,
            mp.solutions.hands.HAND_CONNECTIONS
        )