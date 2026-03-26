import cv2
import time
import numpy as np
from config import *
from gesture_recognizer import GestureRecognizer
from system_controller import SystemController
from overlay import Overlay

ONE_SHOT = {"PLAY_PAUSE", "NEXT_TRACK", "PREV_TRACK", "SCREENSHOT"}

def main():
    cap = cv2.VideoCapture(CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    recognizer = GestureRecognizer()
    controller = SystemController()
    overlay = Overlay()

    prev_time = 0
    gesture_counter = {}
    last_triggered = None
    muted = False
    mute_hold_start = None
    vol_buffer = []
    bright_buffer = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = recognizer.process(rgb)
        hand_landmarks, coords = recognizer.get_landmarks(results, frame.shape)

        curr_time = time.time()
        fps = 1 / (curr_time - prev_time + 1e-9)
        prev_time = curr_time

        gesture, extra = recognizer.detect_gesture(coords)

        if gesture:
            gesture_counter[gesture] = gesture_counter.get(gesture, 0) + 1
        else:
            gesture_counter = {}

        confirmed = None
        if gesture and gesture_counter.get(gesture, 0) >= GESTURE_HOLD_FRAMES:
            confirmed = gesture

        vol = controller.get_volume()
        bright = controller.get_brightness()

        if confirmed == "VOLUME" and coords:
            y = coords[8][1]
            raw_vol = int(np.interp(y, [100, FRAME_HEIGHT - 100], [100, 0]))
            vol_buffer.append(raw_vol)
            if len(vol_buffer) > SMOOTHING_FACTOR:
                vol_buffer.pop(0)
            vol = int(np.mean(vol_buffer))
            controller.set_volume(vol)

        elif confirmed == "BRIGHTNESS" and coords:
            y = coords[8][1]
            raw_bright = int(np.interp(y, [100, FRAME_HEIGHT - 100], [100, 10]))
            bright_buffer.append(raw_bright)
            if len(bright_buffer) > SMOOTHING_FACTOR:
                bright_buffer.pop(0)
            bright = int(np.mean(bright_buffer))
            controller.set_brightness(bright)

        elif confirmed in ONE_SHOT and confirmed != last_triggered:
            if confirmed == "PLAY_PAUSE":   controller.play_pause()
            elif confirmed == "NEXT_TRACK": controller.next_track()
            elif confirmed == "PREV_TRACK": controller.prev_track()
            elif confirmed == "SCREENSHOT": controller.take_screenshot()

        # Mute evaluated every frame independently so the 1s hold can accumulate
        if confirmed == "MUTE_TOGGLE":
            if mute_hold_start is None:
                mute_hold_start = time.time()
            elif time.time() - mute_hold_start >= 1.0:
                muted = controller.toggle_mute()
                overlay.notify("MUTE_TOGGLE")
                mute_hold_start = None
        else:
            mute_hold_start = None

        last_triggered = confirmed if confirmed in ONE_SHOT else None

        if hand_landmarks:
            recognizer.draw_landmarks(frame, hand_landmarks)
        else:
            overlay.draw_no_hand(frame)

        overlay.notify(confirmed)
        overlay.draw_gesture_panel(frame)
        overlay.draw_level_panel(frame, vol, "VOL", x=40)
        overlay.draw_level_panel(frame, bright, "BRIGHT", x=140)
        overlay.draw_mute_badge(frame, muted)
        overlay.draw_fps(frame, fps)
        overlay.draw_status(frame, "Press Q to quit  |  G for guide")

        overlay.draw_guide(frame)
        cv2.imshow("GestureFlow", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        if key == ord('g'):
            overlay.show_guide = not overlay.show_guide

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()