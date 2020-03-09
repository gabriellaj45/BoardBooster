from sklearn.cluster import KMeans
from collections import Counter
import cv2
import webcolors
from os import system


def getDominantColor(image, k=4):
    image = cv2.imread(image)

    # reshape the image to be a list of pixels
    image = image.reshape((image.shape[0] * image.shape[1], 3))

    # cluster and assign labels to the pixels
    clt = KMeans(n_clusters=k)
    labels = clt.fit_predict(image)

    # count labels to find most popular
    numLabels = Counter(labels)

    # subset out most popular centroid
    dominantColor = clt.cluster_centers_[numLabels.most_common(1)[0][0]]

    r, g, b = dominantColor

    describeColor = int(r), int(g), int(b)
    actualName, closestColorName = getColorName(describeColor)

    # system('say -v Samantha ' + closestColorName)
    return closestColorName


def closestColor(describeColor):
    min_colours = {}
    for key, name in webcolors.css3_hex_to_names.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - describeColor[0]) ** 2
        gd = (g_c - describeColor[1]) ** 2
        bd = (b_c - describeColor[2]) ** 2
        min_colours[(rd + gd + bd)] = name
    return min_colours[min(min_colours.keys())]


def getColorName(describeColor):
    try:
        closestColorName = actualName = webcolors.rgb_to_name(describeColor)
    except ValueError:
        closestColorName = closestColor(describeColor)
        actualName = None
    return actualName, closestColorName