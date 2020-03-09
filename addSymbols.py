import PIL.Image
import PIL.ImageTk
import tkinter as tk
import numpy as np
from scipy.spatial import distance as dist
from getRegions import *
from extractSymbols import *


class addSymbols:
    def __init__(self, window, window_title, game, video_source=0):
        self.window = window
        self.window.title(window_title)
        self.game = game
        self.video_source = video_source

        self.cardContour = None
        self.zoomWindow = None
        self.destroy = False

        # open video source
        self.vid = MyVideoCapture(self.video_source)

        # Create a canvas that can fit the above video source size
        self.canvas = tk.Canvas(window, width=self.vid.width, height=self.vid.height)

        self.quitButton = tk.Button(window, text="Done", width=15, command=self.labelSymbols)
        self.quitButton.pack(side=tk.BOTTOM)

        self.snapButton = tk.Button(window, text="Take Picture", width=15, command=self.snapshot)
        self.snapButton.pack(side=tk.BOTTOM)

        self.canvas.pack()

        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 2000
        self.cardNum = 0
        self.update()

        self.window.mainloop()

    def labelSymbols(self):
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

                fileName = self.game + "/processSymbols/" + str(self.cardNum) + ".jpg"
                cv2.imwrite(fileName, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
                self.cardNum = self.cardNum + 1

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
                
            self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

    def update(self):
        # Get a frame from the video source
        ret, frame = self.vid.get_frame()

        if ret:
            self.showContours()
            self.updateWin()

        if not self.destroy:
            self.window.after(self.delay, self.update)
        else:
            self.window.destroy()
            extractSymbols(self.game)

    def updateWin(self):
        self.zoomWindow = zoomWindow(self)


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


class zoomWindow:
    def __init__(self, createTemplates, video_source=0):
        self.subRoot = tk.Toplevel()
        self.subRoot.title("Verify Contour Perspective Corrected")
        self.subRoot.geometry("500x500+125+125")

        self.createTemplates = createTemplates

        self.video_source = video_source
        self.vid = MyVideoCapture(self.video_source)

        self.showImage()

        self.subRoot.after(2000, lambda: self.subRoot.destroy())

    def showImage(self):
        '''
        photo = Image.open('cardImage.jpg')
        render = ImageTk.PhotoImage(photo)
        label = tk.Label(self.subRoot, image=render)
        label.image = render
        label.pack()
        '''

        ret, frame = self.vid.get_frame()
        if ret:
            # approximate the contour
            peri = cv2.arcLength(self.createTemplates.cardContour, True)
            approx = cv2.approxPolyDP(self.createTemplates.cardContour, 0.02 * peri, True)

            if len(approx) == 4:
                h = np.array([[0, 0], [400, 0], [400, 400], [0, 400]], np.float32)
                approx = np.array([item for sublist in approx for item in sublist], np.float32)
                approx = self.createTemplates.order_points(approx)
                transform = cv2.getPerspectiveTransform(approx, h)
                image = cv2.warpPerspective(frame, transform, (400, 400))

                photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(image))
                label = tk.Label(self.subRoot, image=photo)
                label.image = photo
                label.pack()





