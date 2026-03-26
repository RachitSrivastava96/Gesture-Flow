# GestureFlow

GestureFlow is a real-time, vision-based system control application that lets you control your computer using hand gestures captured through a webcam. No physical input devices are required. Using MediaPipe for hand landmark detection, GestureFlow recognizes a set of defined gestures and maps them to system actions such as adjusting volume and brightness, controlling media playback, toggling mute, and taking screenshots.

---

## Table of Contents

- [Motivation](#motivation)
- [Features](#features)
- [Gesture Reference](#gesture-reference)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Setup and Installation](#setup-and-installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Author](#author)
- [Contact](#contact)

---

## Motivation

Conventional input devices require physical contact and constant attention. In scenarios involving presentations, accessibility needs, or simply a desire for a more natural interaction model, gesture-based control offers a practical alternative. GestureFlow was built to explore how computer vision and machine learning techniques can bridge the gap between human intent and machine response in a real, everyday context.

---

## Features

- Real-time hand detection and landmark tracking via MediaPipe
- Volume control using index finger position (vertical axis)
- Screen brightness control using two-finger position (vertical axis)
- Media playback control: play/pause, next track, previous track
- Mute toggle with a deliberate hold gesture to prevent accidental activation
- Screenshot capture saved automatically to disk
- On-screen overlay with live gesture feedback, volume and brightness indicators, FPS counter, and an interactive gesture guide
- Smoothing and hold-frame confirmation to reduce false positives

---

## Gesture Reference

| Gesture | Action |
|---|---|
| All four fingers extended (open palm) | Play / Pause |
| Closed fist, held for 1 second | Toggle Mute |
| Index finger only, move up/down | Adjust Volume |
| Index and middle fingers, move up/down | Adjust Brightness |
| Thumb only | Previous Track |
| Pinky finger only | Next Track |
| Index, middle, and ring fingers | Take Screenshot |

Press `G` while the application is running to display the gesture guide overlay. Press `Q` to quit.

---

## Project Structure

```
Gesture-Flow/
├── main.py                  # Application entry point and main loop
├── gesture_recognizer.py    # Hand detection, landmark parsing, and gesture logic
├── system_controller.py     # System actions: volume, brightness, media, screenshot
├── overlay.py               # On-screen UI rendering
├── config.py                # Tunable parameters for camera, gestures, and UI
├── requirements.txt         # Python dependencies
├── hand_landmarker.task     # MediaPipe hand landmarker model file
├── Screenshots/             # Auto-created folder where screenshots are saved
└── README.md
```

---

## Requirements

- Python 3.9 or later
- Windows OS (required for `pycaw` audio control and `screen_brightness_control`)
- A working webcam
- The dependencies listed in `requirements.txt`

---

## Setup and Installation

**1. Clone the repository**

```bash
git clone https://github.com/RachitSrivastava96/Gesture-Flow.git
cd Gesture-Flow
```

**2. Create and activate a virtual environment (recommended)**

```bash
python -m venv venv
venv\Scripts\activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Verify the model file is present**

Ensure `hand_landmarker.task` is in the root project directory alongside `main.py`. This file is required by MediaPipe for hand detection.

---

## Usage

Run the application from the project root:

```bash
python main.py
```

Once running:

- Position your hand clearly in front of the webcam
- Hold each gesture steady for a brief moment; gestures are confirmed after a short hold to avoid accidental triggers
- Use vertical hand position for volume and brightness control
- Press `G` to toggle the gesture guide overlay
- Press `Q` to exit

Screenshots are saved automatically to the `Screenshots\` folder inside the project directory, with a timestamp in the filename.

---

## Configuration

All tunable parameters are in `config.py`:

| Parameter | Default | Description |
|---|---|---|
| `CAMERA_INDEX` | `0` | Webcam device index |
| `FRAME_WIDTH` / `FRAME_HEIGHT` | `1280 x 720` | Capture resolution |
| `MAX_HANDS` | `1` | Maximum hands to detect |
| `DETECTION_CONFIDENCE` | `0.8` | Minimum detection confidence |
| `TRACKING_CONFIDENCE` | `0.8` | Minimum tracking confidence |
| `SMOOTHING_FACTOR` | `5` | Frames averaged for smooth volume/brightness control |
| `GESTURE_HOLD_FRAMES` | `5` | Frames a gesture must be held before it is confirmed |

Adjust `SMOOTHING_FACTOR` and `GESTURE_HOLD_FRAMES` to tune responsiveness versus stability based on your hardware and lighting conditions.

---

## Author

Rachit Srivastava

---

## Contact

rachitsrivastava0fficial96@gmail.com