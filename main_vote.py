import cv2
from HandTrackingModule import HandDetector
from directkeys_linux import PressKey, ReleaseKey
from directkeys_linux import SPACE_KEY as space_pressed
import time

detector = HandDetector(detectionCon=0.7, maxHands=6)
space_key_pressed = space_pressed

time.sleep(2.0)

current_key_pressed = set()

FRAME_DIM = (1280, 720)
video = cv2.VideoCapture(0)
video.set(3, FRAME_DIM[0])
video.set(4, FRAME_DIM[1])

while True:
    ret, frame = video.read()
    keyPressed = False
    jump_votes = 0
    total_hands = 0

    hands, img = detector.findHands(frame)
    
    # UI placeholders
    cv2.rectangle(img, (0, 480), (300, 425), (50, 50, 255), -2)
    cv2.rectangle(img, (640, 480), (400, 425), (50, 50, 255), -2)
    cv2.rectangle(img, (0, 580), (400, 525), (50, 50, 255), -2)

    if hands:
        for i, hand in enumerate(hands):
            total_hands += 1
            fingerUp = detector.fingersUp(hand)
            # Count jump votes: All fingers down
            if fingerUp == [0, 0, 0, 0, 0]:
                jump_votes += 1
            # Display per-hand debug info
            cv2.putText(frame, f'Hand {i+1}: {sum(fingerUp)} fingers', (20, 30 + i*30),
                        cv2.FONT_HERSHEY_COMPLEX, 0.7, (255, 255, 255), 1, cv2.LINE_AA)

        # Show jump vote result
        cv2.putText(frame, f'Jump Votes: {jump_votes}/{total_hands}', (20, 560),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)

        # Jump if majority of hands are doing the gesture
        if jump_votes >= (total_hands // 2) + 1:
            cv2.putText(frame, 'Majority Jumping', (420, 460),
                        cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)
            PressKey(space_key_pressed)
            current_key_pressed.add(space_key_pressed)
            keyPressed = True
        else:
            cv2.putText(frame, 'Majority Not Jumping', (420, 460),
                        cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)

    # Release key if not jumping
    if not keyPressed and len(current_key_pressed) != 0:
        for key in current_key_pressed:
            ReleaseKey(key)
        current_key_pressed = set()

    # Display the frame
    cv2.imshow("Frame", frame)
    k = cv2.waitKey(1)
    if k == ord('q'):
        break

video.release()
cv2.destroyAllWindows()