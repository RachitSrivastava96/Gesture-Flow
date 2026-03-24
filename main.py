import cv2
import time
import numpy as np
from config import *
from gesture_recognizer import GestureRecognizer
from system_controller import SystemController
from overlay import Overlay

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

    # Smoothing buffers
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

        # FPS
        curr_time = time.time()
        fps = 1 / (curr_time - prev_time + 1e-9)
        prev_time = curr_time

        gesture = recognizer.detect_gesture(coords)

        # Gesture hold counter
        if gesture:
            gesture_counter[gesture] = gesture_counter.get(gesture, 0) + 1
        else:
            gesture_counter = {}

        confirmed_gesture = None
        if gesture and gesture_counter.get(gesture, 0) >= GESTURE_HOLD_FRAMES:
            confirmed_gesture = gesture

        # --- Actions ---
        vol = controller.get_volume()
        bright = controller.get_brightness()

        if confirmed_gesture == "VOLUME" and coords:
            # Index fingertip Y position controls volume
            y = coords[8][1]
            raw_vol = int(np.interp(y, [100, FRAME_HEIGHT - 100], [100, 0]))
            vol_buffer.append(raw_vol)
            if len(vol_buffer) > SMOOTHING_FACTOR:
                vol_buffer.pop(0)
            vol = int(np.mean(vol_buffer))
            controller.set_volume(vol)

        elif confirmed_gesture == "BRIGHTNESS" and coords:
            y = coords[8][1]
            raw_bright = int(np.interp(y, [100, FRAME_HEIGHT - 100], [100, 10]))
            bright_buffer.append(raw_bright)
            if len(bright_buffer) > SMOOTHING_FACTOR:
                bright_buffer.pop(0)
            bright = int(np.mean(bright_buffer))
            controller.set_brightness(bright)

        elif confirmed_gesture == "PLAY_PAUSE" and confirmed_gesture != last_triggered:
            controller.play_pause()

        elif confirmed_gesture == "NEXT_TRACK" and confirmed_gesture != last_triggered:
            controller.next_track()

        elif confirmed_gesture == "PREV_TRACK" and confirmed_gesture != last_triggered:
            controller.prev_track()

        elif confirmed_gesture == "MUTE_TOGGLE" and confirmed_gesture != last_triggered:
            muted = controller.toggle_mute()

        last_triggered = confirmed_gesture if confirmed_gesture in ["PLAY_PAUSE", "NEXT_TRACK", "PREV_TRACK", "MUTE_TOGGLE"] else None

        # --- Draw ---
        if hand_landmarks:
            recognizer.draw_landmarks(frame, hand_landmarks)

        overlay.draw_gesture(frame, confirmed_gesture)
        overlay.draw_mute_badge(frame, muted)
        overlay.draw_fps(frame, fps)
        overlay.draw_bar(frame, vol, "VOL", x=50)
        overlay.draw_bar(frame, bright, "BRIGHT", x=120)
        overlay.draw_status(frame, "Press Q to quit")

        cv2.imshow("GestureFlow", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()