import cv2
from os import system
import numpy as np
import imutils
from scipy.spatial import distance as dist


def mouse_handler(event, x, y, flags, data):
    if event == cv2.EVENT_LBUTTONDOWN:
        cv2.circle(data['im'], (x, y), 1, (0, 0, 255), 2)
        cv2.imshow("Image", data['im'])
        if len(data['points']) < 4:
            data['points'].append([x, y])
            print(x, y)


def get_four_points(im):
    # Set up data to send to mouse handler
    data = {}
    data['im'] = im.copy()
    data['points'] = []

    # Set the callback function for any mouse event
    cv2.imshow("Image", im)
    cv2.setMouseCallback("Image", mouse_handler, data)
    cv2.waitKey(0)

    # Convert array to np.array
    points = np.vstack(data['points']).astype(float)

    return points


def order_points(pts):
    # sort the points based on their x-coordinates
    xSorted = pts[np.argsort(pts[:, 0]), :]

    # grab the left-most and right-most points from the sorted
    # x-roodinate points
    leftMost = xSorted[:2, :]
    rightMost = xSorted[2:, :]

    # now, sort the left-most coordinates according to their
    # y-coordinates so we can grab the top-left and bottom-left
    # points, respectively
    leftMost = leftMost[np.argsort(leftMost[:, 1]), :]
    (tl, bl) = leftMost

    # now that we have the top-left coordinate, use it as an
    # anchor to calculate the Euclidean distance between the
    # top-left and right-most points; by the Pythagorean
    # theorem, the point with the largest distance will be
    # our bottom-right point
    D = dist.cdist(tl[np.newaxis], rightMost, "euclidean")[0]
    (br, tr) = rightMost[np.argsort(D)[::-1], :]

    # return the coordinates in top-left, top-right,
    # bottom-right, and bottom-left order
    return np.array([tl, tr, br, bl], dtype="float32")


def start():
    picture = cv2.VideoCapture(0)

    _, cardImage = picture.read()

    # cardImage = cv2.imread('Black2.jpg')
    cardImage = imutils.resize(cardImage, height=400)

    size = (400, 400)

    im_dst = np.zeros(size, np.uint8)

    pts_dst = np.array(
        [
            [0, 0],
            [size[0], 0],
            [size[0], size[1]],
            [0, size[1]]
        ], dtype=float
    )

    cv2.imshow("Image", cardImage)
    pts_src = get_four_points(cardImage)

    h, status = cv2.findHomography(pts_src, pts_dst)

    # Warp source image to destination
    im_dst = cv2.warpPerspective(cardImage, h, size[0:2])
    '''
    grayScale = cv2.cvtColor(cardImage, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(grayScale, 105, 255, 0)
    cannyEdge = cv2.Canny(thresh, 125, 255)
    
    
    
    # find card in image
    image, contours, hierarchy = cv2.findContours(cannyEdge.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    for c in contours:
        # approximate the contour
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)

        if len(approx) == 4:
            screenCnt = approx
            h = np.array([[0, 0], [400, 0], [400, 400], [0, 400]], np.float32)
            approx = np.array([item for sublist in approx for item in sublist], np.float32)
            approx = order_points(approx)
            transform = cv2.getPerspectiveTransform(approx, h)
            image = cv2.warpPerspective(cardImage, transform, (400, 400))
            break
    '''

    # save perfect card version
    cv2.imwrite('perfectCard.jpg', im_dst)
    return


