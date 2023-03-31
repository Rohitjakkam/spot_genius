import cv2
import pickle
import cvzone
import numpy as np
import os


# Video feed
file_name2 = os.path.join(os.path.dirname(__file__), 'carPark.mp4')
# cap = cv2.VideoCapture(file_name2) 

cap = cv2.VideoCapture()

with open('CarParkPos', 'rb') as f:
    posList = pickle.load(f)

width, height = 107, 48


def assignLaneAndSpotNumbers():
    global current_spot, spot_list
    current_spot = 0
    spot_list = []
    for i, pos in enumerate(posList):
        x1, y1 = pos
        spot = i
        for j, pos2 in enumerate(posList):
            if i == j:
                break

        spot_list.append(spot)
        current_spot += 1

        cv2.putText(img, f"S: {spot}", (
            x1+5, y1+height-20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)


def checkParkingSpace(imgPro):
    spaceCounter = 0
    for i, pos in enumerate(posList):
        x1, y1 = pos
        imgCrop = imgPro[y1:y1 + height, x1:x1 + width]
        count = cv2.countNonZero(imgCrop)

        if count < 900:
            color = (0, 255, 0)
            thickness = 5
            spaceCounter += 1
            spot_num = spot_list[i]
            print(f"Green rectangle: Spot {spot_num}")
        else:
            color = (0, 0, 255)
            thickness = 2

        cv2.rectangle(img, pos, (pos[0] + width,
                      pos[1] + height), color, thickness)
        cvzone.putTextRect(img, str(count), (x1, y1 + height - 3),
                           scale=1, thickness=2, offset=0, colorR=color)

    cvzone.putTextRect(img, f'Free: {spaceCounter}/{len(posList)}',
                       (100, 50), scale=3, thickness=5, offset=20, colorR=(0, 200, 0))


while True:

    if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    ret, img = cap.read()
    assignLaneAndSpotNumbers()
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)
    imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                         cv2.THRESH_BINARY_INV, 25, 16)
    imgMedian = cv2.medianBlur(imgThreshold, 5)
    kernel = np.ones((3, 3), np.uint8)
    imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)

    checkParkingSpace(imgDilate)
    cv2.imshow("Image", img)
    cv2.waitKey(10)
