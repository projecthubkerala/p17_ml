import cv2
import numpy as np
import urllib.request

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore



# --------------------------------
# --------------------------------

# CHANGE HERE
width, height = 100, 50
slot1 = [40,80]
slot2 = [190,80]
url = "http://192.168.1.40/cam-lo.jpg"


# --------------------------------
# --------------------------------







cred = credentials.Certificate('carparking.json')
app = firebase_admin.initialize_app(cred)

db = firestore.client()

poss = [slot1,slot2]
old = [True,True]

def checkParkingSpace(imgPro):
    spaceCounter = 0
    data = [False,False]

    for idx,pos in enumerate(poss):
        x, y = pos

        imgCrop = imgPro[y:y + height, x:x + width]
        count = cv2.countNonZero(imgCrop)
        print(count)


        if count < 300:
        # if count < 900:
            color = (0, 255, 0)
            thickness = 2
            spaceCounter += 1
            data[idx] = True
        else:
            color = (0, 0, 255)
            thickness = 2

        cv2.rectangle(img, pos, (pos[0] + width, pos[1] + height), color, thickness)

    if(old[0] != data[0] or old[1] != data[1]):
        old[0] = data[0]
        old[1] = data[1]

        slots = {
            u'slot1': not data[0],
            u'slot2': not data[1],
        }
        print(f'slots: {slots}')

        db.collection(u'slot').document(u'xW7Qps7dlbZezeOYFWM7').set(slots, merge=True)

while True:
    req = urllib.request.urlopen(url)
    arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
    img = cv2.imdecode(arr, -1)
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