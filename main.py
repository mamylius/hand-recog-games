import cv2
from HandTrackingModule import HandDetector
from directkeys import PressKey, ReleaseKey
from directkeys import SPACE_KEY as space_pressed
import time

detector=HandDetector(detectionCon=0.7, maxHands=6)

space_key_pressed=space_pressed

# actions = {'left': 18, 'half_left': 12, 'right': 0, 'half_right': 6}
ACTIONS = [
    (18, 12,  0,  6),   # P1  – 1, q, a, y full_up/right, up/half_right, down/half_left, down/left
    (19, 13,  1,  7),   # P2  – 2, w, s, x
    (20, 14,  2,  8),   # P3  – 3, e, d, c
    (21, 15,  3,  9),   # P4  – 4, r, f, v
    (23, 17,  5, 11),   # P5  – 5, t, g, b
    (22, 16,  4, 45)    # P6  – 6, z, h, n
]

time.sleep(2.0)

current_key_pressed = set()

video=cv2.VideoCapture(0)

while True:
    start = time.time()
    ret,frame=video.read()
    keyPressed = False
    spacePressed = False
    key_count=0
    key_pressed=0   
    hands,img=detector.findHands(frame)
    cv2.rectangle(img, (0, 480), (300, 425),(50, 50, 255), -2)
    cv2.rectangle(img, (640, 480), (400, 425),(50, 50, 255), -2)
    cv2.rectangle(img, (0, 580), (400, 525),(50, 50, 255), -2) 
    if hands:
        for key in current_key_pressed:
            ReleaseKey(key)
            
        current_key_pressed = set()

        for i, hand in enumerate(hands):
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

        for key in current_key_pressed:
            PressKey(key)



    cv2.imshow("Frame",frame)
    k=cv2.waitKey(1)
    if k==ord('q'):
        break
    end = time.time()
    print(f"Frame processing time: {end - start:.4f} seconds")
    # time.sleep(1 - (end - start))  # Adjust the sleep time as needed


video.release()
cv2.destroyAllWindows()
