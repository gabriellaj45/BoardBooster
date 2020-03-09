import cv2
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
from getColor import *
colorsImg = {}


def centroid_histogram(clt):
    # grab the number of different clusters and create a histogram
    # based on the number of pixels assigned to each cluster
    numLabels = np.arange(0, len(np.unique(clt.labels_)) + 1)
    (hist, _) = np.histogram(clt.labels_, bins=numLabels)

    # normalize the histogram, such that it sums to one
    hist = hist.astype("float")
    hist /= hist.sum()

    # return the histogram
    return hist


def plot_colors(hist, centroids):
    # initialize the bar chart representing the relative frequency
    # of each of the colors
    bar = np.zeros((50, 300, 3), dtype="uint8")
    startX = 0

    # loop over the percentage of each cluster and the color of
    # each cluster
    for (percent, color) in zip(hist, centroids):
        describeColor = int(color[0]), int(color[1]), int(color[2])
        actualName, closestColorName = getColorName(describeColor)
        colorsImg[closestColorName] = percent
        # plot the relative percentage of each cluster
        endX = startX + (percent * 300)
        cv2.rectangle(bar, (int(startX), 0), (int(endX), 50), color.astype("uint8").tolist(), -1)
        startX = endX

    # return the bar chart
    return bar


def checkForNewSymbols(symbols, text):
    img = cv2.imread("cropped.jpg")
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray_img, 127, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    cannyEdge = cv2.Canny(thresh, 125, 255)
    image, contours, hierarchy = cv2.findContours(cannyEdge.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    mask = np.zeros(img.shape[:2], np.uint8)
    for contour in contours:
        (x, y, w, h) = cv2.boundingRect(contour)
        cv2.rectangle(mask, (x, y), (x+w, y+h), 255, -1)
        # cv2.drawContours(mask, contour, -1, (0, 255, 0), 4)

    new_img = cv2.bitwise_and(img, img, mask=mask)
    # cv2.imwrite('mask.jpg', mask)
    cv2.imwrite('findSymbols.jpg', new_img)

    image = cv2.imread('findSymbols.jpg')
    # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    ret, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY)

    image[thresh == 255] = (255, 0, 0)

    # kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    # erosion = cv2.erode(img, kernel, iterations=1)
    cv2.imwrite('findSymbols.jpg', image)

    image = image.reshape((image.shape[0] * image.shape[1], 3))
    clt = KMeans(n_clusters=3)
    clt.fit(image)

    hist = centroid_histogram(clt)
    bar = plot_colors(hist, clt.cluster_centers_)
    
    for (x, y) in colorsImg.items():
        print(x, y)
        if x == 'black' or x == 'red':
            continue
        else:
            # if y > 0.01:
            return True
    return False


'''

    plt.figure()
    plt.axis("off")
    plt.imshow(image)

    # show our color chart
    plt.figure()
    plt.axis("off")
    plt.imshow(bar)
    plt.show()
'''