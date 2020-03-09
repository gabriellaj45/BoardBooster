import PIL.Image
import PIL.ImageTk
from addNewRegion import *
from recognizeNewSymbols import *
from matchTemplate import *
from generateLabels import *


class scanCards:
    def __init__(self, window, window_title, game, video_source=0):
        self.window = window
        self.window.title(window_title)
        self.video_source = video_source
        self.game = game
        self.destroy = False
        self.templateName = None
        self.fileName = None
        self.cardContour = None
        self.zoomWindow = None
        self.audio = True
        self.check = True
        self.ogCard = None
        self.allRegionCoors = []

        # open video source
        self.vid = MyVideoCapture(self.video_source)

        # Create a canvas that can fit the above video source size
        self.canvas = tk.Canvas(window, width=self.vid.width, height=self.vid.height)

        self.quitButton = tk.Button(window, text="Done", width=15, command=self.generateLabel)
        self.quitButton.pack(side=tk.BOTTOM)

        self.snapButton = tk.Button(window, text='Take Picture', width=15, command=self.snapshot)
        self.snapButton.pack(side=tk.BOTTOM)

        self.canvas.pack()

        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 2000
        self.cardNum = 0
        self.update()

        self.window.mainloop()

    def generateLabel(self):
        self.audio = False
        verifyAllPicturesTaken(self)

    def getTemplateMatch(self):
        self.templateName = matchTemplate(self.fileName, self.game)

    def checkPoint(self, x1, y1, x2, y2, x, y):
        if x >= x1 and x <= x2 and y >= y1 and y <= y2:
            return True
        else:
            return False

    def getRegionCoors(self):
        f = open(self.game + "/regions.txt", "r")
        f1 = f.readlines()
        for x in f1:
            line = re.split('\s', x)
            for name in line[1:]:
                name = re.sub(':', ' ', name)
                labelName = re.split('\s', name)
                if line[0] == self.templateName and 'Text' in labelName[0]:
                    if len(labelName) == 1:
                        continue
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
                    region = regionX1, regionY1, regionX2, regionY2
                    self.allRegionCoors.append(region)

    def checkNewRegions(self):
        print('checking for text')
        # self.getTemplateMatch()
        # print(self.templateName)
        newTextFound = False
        textBoxes = findText(self.fileName)
        self.getRegionCoors()
        for box in textBoxes:
            x1 = int(box[0][0])
            y1 = int(box[0][1])
            x2 = int(box[2][0])
            y2 = int(box[2][1])
            midpointX, midpointY = (x2 + x1) / 2, (y2 + y1) / 2
            if len(self.allRegionCoors) == 0:
                print('no region coordinates')
                addNewRegion(self.game, self.templateName, self.fileName, textBoxes, self.ogCard)
            index = 0
            for i in self.allRegionCoors:
                regionX1, regionY1, regionX2, regionY2 = i
                if self.checkPoint(regionX1, regionY1, regionX2, regionY2, midpointX, midpointY):
                    break
                else:
                    index = index + 1
            if index == len(self.allRegionCoors):
                newTextFound = True
        if newTextFound:
            addNewRegion(self.game, self.templateName, self.fileName, textBoxes, self.ogCard)

        '''
        if x1 < regionX1 < regionX2 < x2 and y1 < regionY1 < regionY2 < y2:
            continue
        else:
            addNewRegion(self.game, self.templateName, self.fileName, textBoxes)
        '''

        '''
        if x1 >= regionX1 and y1 >= regionY1:
            if x2 <= regionX2 and y2 <= regionY2:
                continue
            else:
                addNewRegion(self.game, self.templateName, self.fileName, textBoxes)
                break
        else:
            addNewRegion(self.game, self.templateName, self.fileName, textBoxes)
            break
            
        if nameNotFound:
            addNewRegion(self.game, self.templateName, self.fileName, textBoxes)
        '''

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

                fileName = self.game + "/processCards/" + str(self.cardNum) + ".jpg"
                self.ogCard = fileName
                # imagePreProcessing(fileName, fileName)
                cv2.imwrite(fileName, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))
                self.cardNum = self.cardNum + 1
                self.fileName = fileName
                self.audio = False
                self.getTemplateMatch()
                print(self.templateName)
                system('say -v Samantha Scanning for new text')
                self.checkNewRegions()
                system('say -v Samantha Scanning for new symbols')
                findNewSymbols(self.game, self.fileName, self.templateName)
                self.audio = True
            else:
                system('say -v Samantha Please try again')

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
                    if self.audio:
                        system('say -v Samantha good')

            self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

    def update(self):
        # Get a frame from the video source
        ret, frame = self.vid.get_frame()

        if ret:
            self.showContours()

        if not self.destroy:
            self.window.after(self.delay, self.update)

            # if self.check:
              #   self.zoomWindow = zoomWindow(self)
        else:

            self.window.destroy()
            genLabels(self.game)
            '''
            if not self.zoomWindow.isAlive:
                self.window.destroy()
                genLabels(self.game)
            else:
                self.window.after(self.delay, self.update)
            '''


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


class verifyAllPicturesTaken:
    def __init__(self, scanCards):
        self.value = None
        self.templateName = None
        self.scanCards = scanCards
        self.subRoot = tk.Toplevel()
        self.subRoot.title("Done taking pictures?")

        tk.Label(self.subRoot, text='Are you finished taking pictures of cards?').pack()

        self.continueButton = tk.Button(self.subRoot, text="Yes Continue", width=15, command=self.continueOn)
        self.continueButton.pack()

        self.returnButton = tk.Button(self.subRoot, text="Not Done", width=15, command=self.notDone)
        self.returnButton.pack()

        self.subRoot.mainloop()

    def continueOn(self):
        self.scanCards.destroy = True
        self.subRoot.destroy()

    def notDone(self):
        self.scanCards.destroy = False
        self.scanCards.check = True
        self.scanCards.audio = True
        self.subRoot.destroy()
