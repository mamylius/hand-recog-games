import cv2
from HandTrackingModule import HandDetector
from directkeys_linux import PressKey, ReleaseKey
from directkeys_linux import SPACE_KEY as space_pressed
import time
import pynput

keyboard = pynput.keyboard.Controller()
PressKey = keyboard.press
ReleaseKey = keyboard.release
#pyautogui.PAUSE = 0

detector=HandDetector(detectionCon=0.7, maxHands=6)

space_key_pressed=space_pressed

print(pynput.keyboard.KeyCode.from_char("a"))

# actions = {'left': 18, 'half_left': 12, 'right': 0, 'half_right': 6}
# ACTIONS = [
#     (18, 12,  0,  6),   # P1  – 1, q, a, y full_up/right, up/half_right, down/half_left, down/left
#     (19, 13,  1,  7),   # P2  – 2, w, s, x
#     (20, 14,  2,  8),   # P3  – 3, e, d, c
#     (21, 15,  3,  9),   # P4  – 4, r, f, v
#     (23, 17,  5, 11),   # P5  – 5, t, g, b
#     (22, 16,  4, 45)    # P6  – 6, z, h, n
# ] # For mac

# ACTIONS = [
#     (0x31, 0x51,  0x41, 0x59),   # P1  – 1, q, a, y full_up/right, up/half_right, down/half_left, down/left
#     (0x32, 0x57,  0x53, 0x58),   # P2  – 2, w, s, x
#     (0x33, 0x45,  0x44, 0x43),   # P3  – 3, e, d, c
#     (0x34, 0x52,  0x46, 0x56),   # P4  – 4, r, f, v
#     (0x35, 0x54,  0x47, 0x42),   # P5  – 5, t, g, b
#     (0x36, 0x5A,  0x48, 0x4E)    # P6  – 6, z, h, n
# ]

ACTIONS = [
    ('1', 'q',  'a', 'z'),   # P1  – 1, q, a, y full_up/right, up/half_right, down/half_left, down/left
    ('2', 'w',  's', 'x'),   # P2  – 2, w, s, x
    ('3', 'e',  'd', 'c'),   # P3  – 3, e, d, c
    ('4', 'r',  'f', 'v'),   # P4  – 4, r, f, v
    ('5', 't',  'g', 'b'),   # P5  – 5, t, g, b
    ('6', 'y',  'h', 'n')    # P6  – 6, z, h, n
]
FRAME_DIM = (640, 480)


time.sleep(2.0)

current_key_pressed = set()

video=cv2.VideoCapture(0)
video.set(3, FRAME_DIM[0])
video.set(4, FRAME_DIM[1])

prev_key_pressed = set()

while True:
    start = time.time()
    ret,frame=video.read()
    keyPressed = False
    spacePressed = False
    key_count=0
    key_pressed=0   
    hands,img=detector.findHands(frame, onlyRight=True)
    # cv2.rectangle(img, (0, 480), (300, 425),(50, 50, 255), -2)
    # cv2.rectangle(img, (640, 480), (400, 425),(50, 50, 255), -2)
    cv2.rectangle(img, (0, 580), (400, 525),(50, 50, 255), -2) 
    if hands:
        #for key in current_key_pressed:
        #    ReleaseKey(key)
            
        current_key_pressed = set()
        hands.reverse()

        for i, hand in enumerate(hands):
            print(f"PLAYER:{i}")
            lm=hand
            fingerUp=detector.fingersUp(lm)
            thumbAngle=detector.thumbAngle(lm)
            print(thumbAngle)      
            if 30<thumbAngle and thumbAngle<60: 
                # Add a key press for the event the key is 1 on the keyboard    
                # PressKey(ACTIONS[i][1])
                current_key_pressed.add(ACTIONS[i][1])
                print("half_right")
            elif 60<thumbAngle:
                # PressKey(ACTIONS[i][0])
                current_key_pressed.add(ACTIONS[i][0])
                print("right")
            elif -60<thumbAngle and thumbAngle<-30:
                # PressKey(ACTIONS[i][2])
                current_key_pressed.add(ACTIONS[i][2])
                print("half_left")
            elif thumbAngle<-60:
                # PressKey(ACTIONS[i][3])
                current_key_pressed.add(ACTIONS[i][3])
                print("left")
            else:
                pass

        if thumbAngle:
            cv2.putText(frame, f'ThumbAngle: {thumbAngle:.1f}', (20,560), cv2.FONT_HERSHEY_COMPLEX, 1, (255,255,255), 1, cv2.LINE_AA)

        for key in current_key_pressed - prev_key_pressed:
            PressKey(key)

        for key in prev_key_pressed - current_key_pressed:
            ReleaseKey(key)
    
        prev_key_pressed = current_key_pressed.copy()

    cv2.imshow("Frame",frame)
    k=cv2.waitKey(1)
    if k==ord('q'):
        break
    end = time.time()
    print(f"Frame processing time: {end - start:.4f} seconds")
    # time.sleep(1 - (end - start))  # Adjust the sleep time as needed


video.release()
cv2.destroyAllWindows()
