from PIL import Image, ImageTk
import tkinter as tk
import PIL.Image
import PIL.ImageTk
import cv2


class labelSymbols:
    def __init__(self, window, window_title, image, game):
        self.window = window
        self.window.title(window_title)
        self.x = self.y = 0
        self.cropImage = image
        self.game = game
        self.canvas = tk.Canvas(self.window, width=400, height=425)

        self.canvas.grid(row=0, column=0)
        self.canvas.bind("<ButtonPress-1>", self.buttonPress)
        self.canvas.bind("<B1-Motion>", self.movePress)
        self.canvas.bind("<ButtonRelease-1>", self.buttonRelease)

        self.nextButton = tk.Button(self.window, text="Next", width=15, command=self.window.destroy)
        self.nextButton.grid(row=1, column=0, sticky=tk.E)

        self.rect = None

        self.startX = None
        self.startY = None

        self.image = PIL.Image.open(image)
        self.tk_im = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, anchor="nw", image=self.tk_im)

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
        croppedImage(self.game)


class croppedImage:
    def __init__(self, game):
        self.value = None
        self.photo = None
        self.label = None
        self.render = None
        self.game = game
        self.subRoot = tk.Toplevel()
        self.subRoot.title("Verify Symbol")

        self.showImage()

        tk.Label(self.subRoot, text='Symbol Name').pack()
        self.symbolName = tk.Entry(self.subRoot)
        self.symbolName.pack()

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

        self.photo = Image.open('cropped.jpg')
        self.render = ImageTk.PhotoImage(self.photo)
        self.label = tk.Label(self.subRoot, image=self.render)
        self.label.image = self.render
        self.label.pack()

    def saveInfo(self):
        image = cv2.imread('cropped.jpg')
        name = self.symbolName.get()
        path = self.game + '/cardSymbols/'
        # improve the quality of this image before saving
        cv2.imwrite(path + name + '.jpg', image)
        self.subRoot.destroy()

    def retryRegion(self):
        self.subRoot.destroy()

