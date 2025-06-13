import argparse
import cv2
from HandTrackingModule import HandDetector
from directkeys_linux import PressKey, ReleaseKey
from directkeys_linux import SPACE_KEY as space_pressed
import time
import pynput
import numpy as np

# ---- Argument Parsing ---- #
parser = argparse.ArgumentParser(description="Hand gesture control script.")
parser.add_argument('--device', type=str, default=None, help='Video capture device ID')
parser.add_argument('--half', type=str, default='left', choices=['left', 'right'], help='Which half of the frame to process')
parser.add_argument('--playerid', type=int, default=1, choices=range(1, 7), help='Player ID (1 to 6)')
args = parser.parse_args()

# ---- Setup ---- #
keyboard = pynput.keyboard.Controller()
PressKey = keyboard.press
ReleaseKey = keyboard.release

detector = HandDetector(detectionCon=0.7, maxHands=1)
space_key_pressed = space_pressed

ACTIONS = [
    ('1', 'q',  'a', 'z'),   # P1
    ('2', 'w',  's', 'x'),   # P2
    ('3', 'e',  'd', 'c'),   # P3
    ('4', 'r',  'f', 'v'),   # P4
    ('5', 't',  'g', 'b'),   # P5
    ('6', 'y',  'h', 'n')    # P6
]
FRAME_DIM = (640, 480)
current_key_pressed = set()

# ---- Initialize Video ---- #
# Explicitly specify the backend when opening the camera.  On some
# systems OpenCV's default backend fails to initialise a second camera
# when multiple devices are connected.  CAP_DSHOW is broadly supported
# on Windows and prevents errors like "can't open camera by index".
video = cv2.VideoCapture(args.device)
video.set(3, FRAME_DIM[0])
video.set(4, FRAME_DIM[1])

if not video.isOpened():
    raise RuntimeError(f"Failed to open video device {args.device}")

prev_key_pressed = set()

while True:
    start = time.time()
    ret, frame = video.read()
    
    if not ret:
        print("Failed to read from video device.")
        break

    # Process left or right half
    if args.half == 'left':
        frame = frame[:, :FRAME_DIM[0] // 2]
    else:
        frame = frame[:, FRAME_DIM[0] // 2:]

    playerid = args.playerid - 1  # zero-based index
    keyPressed = False
    spacePressed = False
    key_count = 0
    key_pressed = 0   

    hands, img = detector.findHands(frame, onlyRight=True, playerid=playerid)
    cv2.rectangle(img, (0, 580), (400, 525), (50, 50, 255), -2)

    if hands:
        current_key_pressed = set()
        hands.reverse()
        hand = hands[0]  # Only process the first hand
        print(f"PLAYER: {playerid+1}")
        lm = hand
        fingerUp = detector.fingersUp(lm)
        thumbAngle = detector.thumbAngle(lm)
        print(thumbAngle)      

        if 30 < thumbAngle < 60:
            current_key_pressed.add(ACTIONS[playerid][1])
            print("half_right")
        elif thumbAngle > 60:
            current_key_pressed.add(ACTIONS[playerid][0])
            print("right")
        elif -60 < thumbAngle < -30:
            current_key_pressed.add(ACTIONS[playerid][2])
            print("half_left")
        elif thumbAngle < -60:
            current_key_pressed.add(ACTIONS[playerid][3])
            print("left")

        if thumbAngle:
            cv2.putText(frame, f'ThumbAngle: {thumbAngle:.1f}', (20,560), cv2.FONT_HERSHEY_COMPLEX, 1, (255,255,255), 1, cv2.LINE_AA)

        for key in current_key_pressed - prev_key_pressed:
            PressKey(key)

        for key in prev_key_pressed - current_key_pressed:
            ReleaseKey(key)

        prev_key_pressed = current_key_pressed.copy()

    cv2.imshow(f"Frame-{playerid}", frame)
    k = cv2.waitKey(1)
    if k == ord('q'):
        break
    end = time.time()
    print(f"Frame processing time: {end - start:.4f} seconds")

video.release()
cv2.destroyAllWindows()