import PIL.Image
import PIL.ImageTk
import tkinter as tk
import numpy as np
from scipy.spatial import distance as dist
from VideoCapture import *
from os import system
from imagePreProcessing import *
from extractText import *
from matchTemplate import *
from getColor import *
from readCardText import *


class cardInformation:
    def __init__(self, window, window_title, game, video_source=0):
        self.window = window
        self.window.title(window_title)
        self.video_source = video_source
        self.game = game
        self.destroy = False
        self.templateMatch = None
        self.cardContour = None

        # open video source
        self.vid = MyVideoCapture(self.video_source)

        # Create a canvas that can fit the above video source size
        self.canvas = tk.Canvas(window, width=self.vid.width, height=self.vid.height)

        self.cardColorButton = tk.Button(window, text="Get color of card", width=15, command=self.cardColor)
        self.cardColorButton.pack()

        self.snapButton = tk.Button(window, text="Get category of card", width=15, command=self.cardCategory)
        self.snapButton.pack()

        self.quitButton = tk.Button(window, text="Read text on card", width=15, command=self.readText)
        self.quitButton.pack()

        self.exitButton = tk.Button(window, text="Exit", width=15, command=self.window.destroy)
        self.exitButton.pack(side=tk.BOTTOM)

        self.canvas.pack()

        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 2000
        self.cardNum = 0
        self.update()

        self.window.mainloop()

    def cardColor(self):
        self.snapshot()
        color = getDominantColor("cardInformation.jpg")
        system('say -v Samantha ' + color)

    def cardCategory(self):
        self.snapshot()
        category = matchTemplate("cardInformation.jpg", self.game)
        category = re.sub('.jpg', '', category)
        system('say -v Samantha ' + category)

    def readText(self):
        self.snapshot()
        self.templateMatch = matchTemplate("cardInformation.jpg", self.game)
        self.destroy = True

    def snapshot(self):
        ret, frame = self.vid.get_frame()

        if ret:
            # approximate the contour
            peri = cv2.arcLength(self.cardContour, True)
            approx = cv2.approxPolyDP(self.cardContour, 0.02 * peri, True)

            if len(approx) == 4:
                h = np.array([[0, 0], [400, 0], [400, 400], [0, 400]], np.float32)
                approx = np.array([item for sublist in approx for item in sublist], np.float32)
                approx = self.order_points(approx)
                transform = cv2.getPerspectiveTransform(approx, h)
                image = cv2.warpPerspective(frame, transform, (400, 400))

                fileName = "cardInformation.jpg"
                # imagePreProcessing(fileName, self.game)
                cv2.imwrite(fileName, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
                # self.cardNum = self.cardNum + 1
            else:
                system('say -v Samantha Please try again, I could not find the card')

    def order_points(self, pts):
        # sort the points based on their x-coordinates
        xSorted = pts[np.argsort(pts[:, 0]), :]

        # grab the left-most and right-most points from the sorted
        # x-coordinate points
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

    def showContours(self):
        ret, frame = self.vid.get_frame()
        if ret:
            grayScale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(grayScale, 105, 255, 0)
            cannyEdge = cv2.Canny(thresh, 125, 255)

            # find card in image
            image, contours, hierarchy = cv2.findContours(cannyEdge.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contours = sorted(contours, key=cv2.contourArea, reverse=True)

            if contours:
                self.cardContour = contours.pop(0)

                cv2.drawContours(frame, [self.cardContour], 0, (0, 255, 0), 2)

                peri = cv2.arcLength(self.cardContour, True)
                approx = cv2.approxPolyDP(self.cardContour, 0.02 * peri, True)

                if len(approx) == 4:
                    system('say -v Samantha Good')

                if len(approx) is not 4:
                    system('say -v Samantha Please try again no card detected')

            self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

    def update(self):
        # Get a frame from the video source
        ret, frame = self.vid.get_frame()

        if ret:
            self.showContours()

        if not self.destroy:
            self.window.after(self.delay, self.update)
        else:
            self.window.destroy()
            readCardText(tk.Tk(), "Read Text", "cardInformation.jpg", self.templateMatch, self.game)


class MyVideoCapture:
    def __init__(self, video_source=0):
        # Open the video source
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        # Get video source width and height
        self.width = self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                # Return a boolean success flag and the current frame converted to BGR
                return ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else:
                return ret, None

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()
