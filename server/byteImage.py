import base64
import cv2
import numpy as np
from imutils import contours
import imutils
from imutils.perspective import four_point_transform
from digit import digit_recog
from PIL import Image
from io import BytesIO


# import requests
# from matplotlib import pyplot as plt

def readb64(encoded_data):
    nparr = np.frombuffer(base64.b64decode(encoded_data), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img


def imgToBase64(img):
    RGB_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(RGB_img)
    buff = BytesIO()
    pil_img.save(buff, format="JPEG")
    new_image_string = base64.b64encode(buff.getvalue()).decode("utf-8")
    return new_image_string


def auto_scoring(image):
    ANSWER_KEY = {0: 3, 1: 2, 2: 1, 3: 3, 4: 1, 5: 0, 6: 2, 7: 3, 8: 3, 9: 1, 10: 0,
                  11: 0, 12: 3, 13: 3, 14: 2, 15: 0, 16: 2, 17: 0, 18: 3, 19: 2, 20: 0,
                  21: 2, 22: 1, 23: 0, 24: 2, 25: 0, 26: 3, 27: 1, 28: 3, 29: 1, 30: 3,
                  31: 3, 32: 0, 33: 3, 34: 2, 35: 2, 36: 0, 37: 2, 38: 0, 39: 1, 40: 3,
                  41: 3, 42: 0, 43: 1, 44: 3, 45: 1, 46: 0, 47: 2, 48: 3, 49: 1, 50: 1,
                  51: 0, 52: 1, 53: 1, 54: 3, 55: 1, 56: 2, 57: 1, 58: 3, 59: 1, 60: 3,
                  61: 1, 62: 3, 63: 3, 64: 3, 65: 1, 66: 1, 67: 1, 68: 1, 69: 0, 70: 3,
                  71: 1, 72: 3, 73: 0, 74: 0, 75: 0, 76: 3, 77: 3, 78: 2, 79: 1, 80: 2,
                  81: 3, 82: 2, 83: 2, 84: 2, 85: 2, 86: 2, 87: 3, 88: 2, 89: 0, 90: 0,
                  91: 1, 92: 3, 93: 0, 94: 1, 95: 2, 96: 2, 97: 3, 98: 2, 99: 0}
    # modify answer key

    b = list(ANSWER_KEY.values())
    b = np.array(b).reshape(-1, 25).transpose().flatten()

    # scale image
    scale = 0.5
    w, h = image.shape[1] * scale, image.shape[0] * scale
    image = cv2.resize(image, (int(w), int(h)))

    # convert image to gray scale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    canny = cv2.Canny(blur, 75, 200)

    cnts = cv2.findContours(canny.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    tmp = None
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
    for c in cnts:
        peri = cv2.arcLength(c, True)
        app = cv2.approxPolyDP(c, 0.02 * peri, True)

        if len(app) == 4:
            tmp = app
            break

    if tmp is None:
        return np.array([])

    color_img = four_point_transform(image, tmp.reshape(4, 2))

    rotate = four_point_transform(gray, tmp.reshape(4, 2))

    # threhold image
    thresh = cv2.adaptiveThreshold(rotate, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 101, 7)

    # find contours
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    # tìm MSV ở đây
    student_id_box = 0
    for c in cnts:
        (__, (w, h), __) = cv2.minAreaRect(c)
        # use ratio between width and height to define a circle
        if w != 0 and h != 0:
            if w > h:
                temp = w
                w = h
                h = temp
            ratio = h / w
            if ratio >= 7.2 and ratio <= 8.2:
                student_id_box = cv2.boundingRect(c)
                break

    ##########
    if student_id_box == 0:
        return np.array([])

    x, y, w, h = student_id_box[0], student_id_box[1], student_id_box[2], student_id_box[3]

    student_id_img = color_img[y:y + h, x:x + w, :]

    student_id = digit_recog(student_id_img)
    print(student_id)

    cv2.rectangle(color_img, [x, y], [x + w, y + h], (255, 0, 0), 3)

    questionCnts = []
    # loop over the contours
    for c in cnts:
        # compute the bounding box of the contour
        (x, y, w, h) = cv2.boundingRect(c)
        # use ratio between width and height to define a circle
        ar = w / float(h)
        if w >= 20 and h >= 20 and ar >= 0.8 and ar <= 1.2:
            questionCnts.append(c)

    print(len(questionCnts))

    ############
    if len(questionCnts) != 500:
        return np.array([])

    # sort the question contours top-to-bottom

    # Cái sort này chỉ đảm bảo các đáp án nằm đúng thứ tự từ trên xuống dưới,
    # nhưng không đảm bảo rằng các câu trong 1 dòng nằm đúng thứ tự từ trái -> phải
    questionCnts = contours.sort_contours(questionCnts, method="top-to-bottom")[0]

    correct = 0

    sorted_cnt = []

    # Sắp xếp các câu trong một dòng, 1 dòng có 20 câu:
    for (q, i) in enumerate(np.arange(0, len(questionCnts), 20)):
        cnts = contours.sort_contours(questionCnts[i:i + 20])[0]
        sorted_cnt = sorted_cnt + list(cnts)

    for (q, i) in enumerate(np.arange(0, 500, 5)):
        cnts = sorted_cnt[i:i + 5]
        bubbled = None

        # loop over the sorted contours
        for (j, c) in enumerate(cnts):
            # create a mask that reveals ONLY the current bubled for the question
            mask = np.zeros(thresh.shape, dtype="uint8")
            cv2.drawContours(mask, [c], -1, 255, -1)

            # apply the mask to the thresholded image, then
            # count the number of non-zero pixels in the
            # bubble area
            mask = cv2.bitwise_and(thresh, thresh, mask=mask)
            total = cv2.countNonZero(mask)

            # find the maximum non-zero pixels --> the chosen one
            if bubbled is None or total > bubbled[0]:
                bubbled = (total, j)

        # create the contour color and the index of the CORRECT answer
        color = (0, 0, 255)  # RED
        k = b[q]
        # print("ans:",k)
        # print("choose:", bubbled[1])

        # check whether the bubbled answer is correct
        if k == bubbled[1]:
            # change color to green
            color = (0, 255, 0)  # GREEN
            correct += 1
        # draw the outline of the correct answer on the test
        cv2.drawContours(color_img, [cnts[k]], -1, color, 3)

    print("Score: {}/{}".format(correct, len(ANSWER_KEY)))
    score = "Score: {}/{}".format(correct, len(ANSWER_KEY))
    cv2.putText(color_img, "{}/{} - {}".format(correct, len(ANSWER_KEY), student_id), (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

    return color_img, student_id, score
