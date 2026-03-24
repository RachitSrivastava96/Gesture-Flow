# Gesture Flow

**Gesture Flow** is a desktop application that lets you control common system settings and media playback using hand gestures in front of your webcam. It uses your camera feed together with hand tracking so you can adjust volume and screen brightness, skip tracks, play or pause audio, and mute the system without touching the keyboard or mouse.

This repository: [https://github.com/RachitSrivastava96/Gesture-Flow](https://github.com/RachitSrivastava96/Gesture-Flow)

---

## What this project does

Gesture Flow runs in a loop: it reads video from your webcam, detects your hand, figures out which gesture you are making, and then runs the matching action on your computer (for example, raising or lowering the master volume). A live preview window shows your camera image, a simple skeleton overlay on your hand, the name of the recognized gesture, bars for volume and brightness, frames per second, and a reminder of how to exit.

The application is intended for **Windows**. It relies on Windows audio APIs for volume and mute, common Windows-friendly libraries for screen brightness, and simulated media keys for music and video apps that respond to those keys.

---

## How it works (overview)

1. **Capture**  
   Each frame is read from the default webcam, then flipped horizontally so the preview behaves like a mirror (more natural when you move your hand).

2. **Hand tracking**  
   The frame is converted to RGB and passed to **MediaPipe Hands**, which estimates the positions of hand landmarks (fingertips, joints, and palm points).

3. **Gesture classification**  
   Landmark positions are turned into pixel coordinates. A small set of rules checks which fingers are extended. Those rules map finger patterns to named gestures such as volume control or next track.

4. **Stability**  
   The same gesture must be seen for several consecutive frames before it is treated as “confirmed.” This reduces accidental triggers when the hand moves quickly or the tracker flickers.

5. **Actions**  
   Once a gesture is confirmed, the program either updates volume or brightness continuously (while you hold that gesture) or fires a one-shot action once (such as play/pause), depending on the gesture type.

6. **On-screen feedback**  
   A separate overlay module draws text and simple bars on top of the video so you can see the active gesture, mute state, and current levels.

---

## Project structure

| File | Role |
|------|------|
| `main.py` | Main loop: camera, recognition, actions, and the preview window. |
| `gesture_recognizer.py` | MediaPipe hand tracking, finger state, and gesture labels. |
| `system_controller.py` | Volume, brightness, mute, and media key actions on the OS. |
| `overlay.py` | Drawing gesture text, bars, FPS, mute badge, and status text. |
| `config.py` | Camera size, detection settings, smoothing, and UI colors. |
| `requirements.txt` | Python package versions used by the project. |

---

## Gestures and behavior

Gestures are detected from which fingers are extended. The logic uses the positions of fingertips relative to nearby joints (and the thumb relative to the hand). The webcam image is mirrored, which keeps left/right behavior consistent with what you see on screen.

| Gesture name | What to do with your hand | What the system does |
|--------------|---------------------------|----------------------|
| **VOLUME** | Index finger up; middle, ring, and pinky down | While held and confirmed, **vertical position of the index fingertip** maps to master volume (higher on screen tends toward higher volume; the exact range is mapped in code). Values are smoothed over several frames to reduce jitter. |
| **BRIGHTNESS** | Index and middle fingers up; ring and pinky down | Same idea as volume: **index fingertip height** controls display brightness within a configured minimum and maximum. |
| **PLAY_PAUSE** | All fingers closed into a fist (no fingers counted as “up”) | Sends a **play/pause** media key once per gesture activation (not repeated every frame while held). |
| **NEXT_TRACK** | Only the pinky extended | **Next track** media key, once per activation. |
| **PREV_TRACK** | Only the thumb extended | **Previous track** media key, once per activation. |
| **MUTE_TOGGLE** | All fingers extended (open hand) | Toggles **system mute** on the default playback device once per activation. |

If the pose does not match any rule, no gesture is active and no new action is taken.

**Hold frames:** A gesture must be recognized for a minimum number of consecutive frames (`GESTURE_HOLD_FRAMES` in `config.py`) before it becomes a **confirmed** gesture. That makes the controls less sensitive to brief mis-detections.

**One-shot vs continuous:** Volume and brightness keep updating while you hold the matching gesture and it stays confirmed. Play/pause, next, previous, and mute are designed to fire when the gesture becomes confirmed, and repeated firing is limited by tracking the last triggered gesture so the same pose does not spam the same key repeatedly in an uncontrolled way.

**Smoothing:** Raw volume and brightness values are averaged over a short buffer (`SMOOTHING_FACTOR` in `config.py`) so the levels do not jump erratically when your hand shakes slightly.

---

## Requirements

- **Operating system:** Windows (tested expectations: Windows 10 or 11). The audio stack uses `pycaw` and COM interfaces that are aimed at Windows. Brightness control depends on `screen-brightness-control`, which supports Windows among other systems. Media shortcuts use `pyautogui` to send key press events.
- **Hardware:** A working webcam (built-in or USB). Good lighting and a clear view of your hand improve detection.
- **Software:** Python 3.10 or newer is recommended (match the versions in `requirements.txt` if you need a reproducible environment).

---

## Clone the repository

Use Git from a terminal (Command Prompt, PowerShell, or Git Bash):

```bash
git clone https://github.com/RachitSrivastava96/Gesture-Flow.git
cd Gesture-Flow
```

If you do not use Git, you can download the repository as a ZIP archive from the green **Code** button on the GitHub page and extract it, then open a terminal in the extracted folder.

---

## Run Gesture Flow on your machine

### 1. Create a virtual environment (recommended)

A virtual environment keeps this project’s packages separate from your global Python installation.

**PowerShell:**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Command Prompt:**

```cmd
python -m venv venv
venv\Scripts\activate.bat
```

### 2. Install dependencies

With the virtual environment activated:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

If installation fails, confirm you are using a 64-bit Python build on Windows when the documentation of a dependency requires it, and that your `pip` points to the same Python you used to create `venv`.

### 3. Start the application

```bash
python main.py
```

A window titled **GestureFlow** should open showing the webcam feed. Position your hand in frame and use the gestures described above.

### 4. Exit

Press the **q** key while the preview window is focused to quit and release the camera.

---

## Configuration (`config.py`)

You can tune behavior without changing the core logic:

- **`CAMERA_INDEX`:** Which webcam to use (`0` is usually the first camera). If the wrong device opens, try `1`, `2`, and so on.
- **`FRAME_WIDTH` / `FRAME_HEIGHT`:** Resolution of the capture. Higher resolution can cost more CPU; very low resolution may hurt tracking accuracy.
- **`DETECTION_CONFIDENCE` / `TRACKING_CONFIDENCE`:** Used by MediaPipe (see `gesture_recognizer.py` for the values passed into `Hands`). Stricter values can reduce false positives but may drop the hand more often in poor lighting.
- **`SMOOTHING_FACTOR`:** Length of the moving average for volume and brightness (larger is smoother but slower to respond).
- **`GESTURE_HOLD_FRAMES`:** How many frames a gesture must persist before it counts as confirmed.
- **`BRIGHTNESS_MIN` / `BRIGHTNESS_MAX`:** Clamp range for brightness percentage (as used when mapping fingertip position to brightness).

Colors and font sizes for the overlay are also defined here.

---

## Troubleshooting

- **No window or black screen:** Another program may be using the camera. Close other apps that use the webcam, or change `CAMERA_INDEX`.
- **Wrong camera:** Try different indices in `config.py` until the intended device appears.
- **Gesture does nothing:** Ensure lighting is adequate, your full hand is visible, and hold the pose steadily until the label appears. Check that `GESTURE_HOLD_FRAMES` is not set too high for quick testing.
- **Volume or mute does not change:** Confirm you are on Windows and that the default playback device is the one you expect. Some apps or drivers manage volume differently.
- **Brightness does not change:** External monitors sometimes do not support software brightness control; laptops often work more reliably. Permissions or vendor tools can also interfere.
- **Media keys have no effect:** The target player must respond to global media keys. Some applications only listen when they are focused or use different shortcuts.

---

## Dependencies (high level)

- **OpenCV (`cv2`):** Webcam capture and display.
- **MediaPipe:** Hand landmark detection.
- **NumPy:** Numerical helpers for smoothing and mapping.
- **`pycaw` / `comtypes`:** Windows audio endpoint volume and mute.
- **`screen-brightness-control`:** Screen brightness.
- **`pyautogui`:** Media key simulation (play/pause, next, previous).

Full pinned versions are listed in `requirements.txt`.

---


## Contact

**Gesture Flow** — questions or feedback:

- **Email:** rachitsrivastava0fficial96@gmail.com  

Phone numbers are not listed here by design.

---

## Acknowledgments

Hand tracking is powered by [Google MediaPipe](https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker). OpenCV is used for video I/O and drawing. Other libraries are credited in `requirements.txt`.
