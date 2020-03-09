import cv2
import numpy as np
import PIL.Image
import PIL.ImageTk
from addNewRegion import *
from textDetection import findText
from getRegions import *
from matchTemplate import *
from scipy.spatial import distance as dist
from scanCards import *
from cardInformation import *


class createTemplates:
    def __init__(self, window, window_title, game, video_source=0):
        self.window = window
        self.window.title(window_title)
        self.game = game
        self.video_source = video_source
        self.destroy = False
        self.check = True
        self.templateName = None
        self.fileName = None
        self.destroyMain = False
        self.editDestroy = False
        self.scanDestroy = False
        self.infoDestroy = False

        self.cardContour = None
        self.zoomWindow = None

        # open video source
        self.vid = MyVideoCapture(self.video_source)

        # Create a canvas that can fit the above video source size
        self.canvas = tk.Canvas(window, width=self.vid.width, height=self.vid.height)

        self.quitButton = tk.Button(self.window, text="Done", width=15, command=self.labelRegions)
        self.quitButton.pack(side=tk.BOTTOM)

        self.snapButton = tk.Button(self.window, text="Take Picture", width=15, command=self.snapshot)
        self.snapButton.pack(side=tk.BOTTOM)

        self.canvas.pack()

        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 2000
        self.cardNum = 2
        self.update()

        self.window.mainloop()

    def labelRegions(self):
        verifyAllPicturesTaken(self)

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

                self.check = False
                name = nameTemplate()

                self.fileName = self.game + "/cardTemplates/" + name.templateName + ".jpg"
                cv2.imwrite(self.fileName, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
                self.cardNum = self.cardNum + 1
                self.check = True
        # self.checkNewRegions()

    def checkNewRegions(self):
        regionName = 'Text'
        self.getTemplateMatch()
        textBoxes = findText(self.fileName)
        for box in textBoxes:
            x1 = int(box[0][0])
            y1 = int(box[0][1])
            x2 = int(box[1][0])
            y2 = int(box[1][1])
            f = open(self.game + "/regions.txt", "r")
            f1 = f.readlines()
            for x in f1:
                line = re.split('\s', x)
                for name in line[1:]:
                    name = re.sub(':', ' ', name)
                    labelName = re.split('\s', name)
                    if regionName in labelName[0] and line[0] == self.templateName:
                        labelName[1] = re.sub('\(', '', labelName[1])
                        labelName[1] = re.sub('\)', '', labelName[1])
                        labelName[1] = re.sub(',', ' ', labelName[1])
                        region = str(labelName[1])
                        region = re.split('\s', region)
                        region = list(filter(lambda a: a != '', region))
                        regionX1 = int(region[0])
                        regionY1 = int(region[1])
                        regionX2 = int(region[2])
                        regionY2 = int(region[3])

                        if x1 >= regionX1 and y1 >= regionY1:
                            if x2 <= regionX2 and y2 <= regionY2:
                                continue
                            else:
                                addNewRegion()
                                break
                        else:
                            addNewRegion()
                            break

    def getTemplateMatch(self):
        self.templateName = matchTemplate(self.fileName, self.game)

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

        if not self.destroy:
            self.window.after(self.delay, self.update)
            if self.check:
                self.zoomWindow = zoomWindow(self)
        else:
            if not self.zoomWindow.isAlive:
                self.window.destroy()
                getRegions(self.game)
            else:
                self.window.after(self.delay, self.update)


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
        self.isAlive = True

        self.createTemplates = createTemplates
        tk.Label(self.subRoot, text='Click Take Picture button, when picture looks good' ,fg='red').pack()
        self.video_source = video_source
        self.vid = MyVideoCapture(self.video_source)

        self.showImage()

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
            if len(self.createTemplates.cardContour) > 0:
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
        self.subRoot.after(2000, self.kill)

    def kill(self):
        self.isAlive = False
        self.subRoot.destroy()


class nameTemplate:
    def __init__(self):
        self.value = None
        self.templateName = None
        self.subRoot = tk.Toplevel()
        self.subRoot.title("Template Name")

        tk.Label(self.subRoot, text='Template Name').pack()
        self.regionName = tk.Entry(self.subRoot)
        self.regionName.pack()

        self.nextButton = tk.Button(self.subRoot, text="Ok", width=15, command=self.saveInfo)
        self.nextButton.pack()

        self.subRoot.mainloop()

    def saveInfo(self):
        name = self.regionName.get()
        self.templateName = name
        self.subRoot.quit()
        self.subRoot.destroy()


class verifyAllPicturesTaken:
    def __init__(self, createTemplates):
        self.value = None
        self.templateName = None
        self.createTemplates = createTemplates
        self.subRoot = tk.Toplevel()
        self.subRoot.title("Done taking pictures?")

        tk.Label(self.subRoot, text='Are you finished taking pictures of cards?').pack()

        self.continueButton = tk.Button(self.subRoot, text="Yes Continue", width=15, command=self.continueOn)
        self.continueButton.pack()

        self.returnButton = tk.Button(self.subRoot, text="Not Done", width=15, command=self.notDone)
        self.returnButton.pack()

        self.createTemplates.check = False

        self.subRoot.mainloop()

    def continueOn(self):
        self.createTemplates.destroy = True
        self.subRoot.destroy()

    def notDone(self):
        self.createTemplates.destroy = False
        self.createTemplates.check = True
        self.subRoot.destroy()


if __name__ == '__main__':
    # createTemplates(tk.Tk(), "Add New Templates", 'Cards Against Humanity')
    root = tk.Tk()  # run standalone?
    button = createTemplates(root, "Add New Templates", 'Cards Against Humanity')  # parent=Tk: top-level
    root.mainloop()
