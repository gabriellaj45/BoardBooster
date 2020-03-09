from PIL import Image, ImageTk
import tkinter as tk
import PIL.Image
import PIL.ImageTk
import cv2


class newSymbols:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        self.x = self.y = 0
        self.cropImage = None
        self.canvas = tk.Canvas(self.window, width=400, height=425)

        self.canvas.grid(row=0, column=0)
        self.canvas.bind("<ButtonPress-1>", self.buttonPress)
        self.canvas.bind("<B1-Motion>", self.movePress)
        self.canvas.bind("<ButtonRelease-1>", self.buttonRelease)

        self.nextButton = tk.Button(self.window, text="Next Card", width=15, command=self.window.destroy)
        self.nextButton.grid(row=2, column=0, sticky=tk.E)

        self.rect = None
        self.regionName = None

        self.startX = None
        self.startY = None
        '''
        self.image = PIL.Image.open(image)
        self.tk_im = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_im)
        '''

        self.window.mainloop()

    def buttonPress(self, event):
        # save mouse drag start position
        self.startX = self.canvas.canvasx(event.x)
        self.startY = self.canvas.canvasy(event.y)

        # create rectangle if not yet exist
        if not self.rect:
            self.rect = self.canvas.create_rectangle(self.x, self.y, 1, 1, outline='red')

    def movePress(self, event):
        currX = self.canvas.canvasx(event.x)
        currY = self.canvas.canvasy(event.y)

        # expand rectangle as you drag the mouse
        self.canvas.coords(self.rect, self.startX, self.startY, currX, currY)

    def buttonRelease(self, event):

        strCoor = int(self.startX), int(self.startY), event.x, event.y
        x = int(strCoor[0])
        w = int(strCoor[2]) - int(strCoor[0])
        y = int(strCoor[1])
        h = int(strCoor[3]) - int(strCoor[1])
        strCoor = str(strCoor)
        strCoor = strCoor.replace(" ", "")

        img = cv2.imread(self.cropImage)
        cropImage = img[y:y + h, x:x + w]
        cv2.imwrite('cropped.jpg', cropImage)
        croppedImage(self.regionFile, strCoor)
        # self.regionFile.write(strCoor)

    def showRegion(self, x, y, w, h):
        img = cv2.imread(self.cropImage)
        cropImage = img[y:y + h, x:x + w]
        cv2.imwrite('cropped.jpg', cropImage)
        name = croppedImage(self.regionFile)


class croppedImage:
    def __init__(self, file, coordinates):
        self.file = file
        self.coordinates = coordinates
        self.value = None
        self.subRoot = tk.Toplevel()
        self.subRoot.title("Verify Region")

        self.showImage()

        tk.Label(self.subRoot, text='Region Name').pack()
        self.regionName = tk.Entry(self.subRoot)
        # self.regionName.insert(0, 'Region Name')
        self.regionName.pack()

        self.nextButton = tk.Button(self.subRoot, text="Confirm", width=15, command=self.saveInfo)
        self.nextButton.pack()

        self.nextButton = tk.Button(self.subRoot, text="Try Again", width=15, command=self.retryRegion)
        self.nextButton.pack()

    def showImage(self):
        '''
        photo = Image.open('cardImage.jpg')
        render = ImageTk.PhotoImage(photo)
        label = tk.Label(self.subRoot, image=render)
        label.image = render
        label.pack()
        self.regionName.delete(0, tk.END)
        '''

        photo = Image.open('cropped.jpg')
        render = ImageTk.PhotoImage(photo)
        label = tk.Label(self.subRoot, image=render)
        label.image = render
        label.pack()

    def saveInfo(self):
        name = self.regionName.get()
        self.file.write(name + ':' + self.coordinates + '\n')
        self.subRoot.destroy()

    def retryRegion(self):
        self.subRoot.destroy()

