import tkinter as tk
from createTemplates import *
from scanCards import *
from cardInformation import *
from editTemplate import *


class mainScreen:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)
        self.game = None
        self.cardGames = []
        self.getCardGames()

        # Create a canvas
        self.canvas = tk.Canvas(self.window, bg="gray", height=500, width=500)
        self.canvas.create_text(250, 200, fill="blue", font="Times 48 italic bold", text="LabelGen")
        self.canvas.pack()

        self.frame = tk.Frame(self.window)
        self.frame.pack()

        self.exitButton = tk.Button(self.frame, text="Exit LabelGen", width=15, command=self.exitLabelGen)
        self.exitButton.pack(side=tk.BOTTOM)

        self.cardInfoButton = tk.Button(self.frame, text="Get Card Info", width=15, command=self.cardInfo)
        self.cardInfoButton.pack(side=tk.BOTTOM)

        self.scanCardsButton = tk.Button(self.frame, text="Scan Cards", width=15, command=self.scanCards)
        self.scanCardsButton.pack(side=tk.BOTTOM)

        self.editTemplateButton = tk.Button(self.frame, text="Edit Templates", width=15, command=self.editTemplate)
        self.editTemplateButton.pack(side=tk.BOTTOM)

        self.newTemplateButton = tk.Button(self.frame, text="Add Template", width=15, command=self.newTemplate)
        self.newTemplateButton.pack(side=tk.BOTTOM)

        self.var = tk.StringVar(self.frame)
        self.var.set("Select Card Game")  # initial value

        self.option = tk.OptionMenu(self.frame, self.var, *self.cardGames)
        self.option.pack()

        self.window.mainloop()

    def exitLabelGen(self):
        exit(0)

    def getCardGames(self):
        for filename in os.listdir():
            if os.path.isdir(filename):
                if filename == '__pycache__' or filename == '.idea':
                    continue
                self.cardGames.append(filename)
        self.cardGames.append('Add New Game')

    def cardInfo(self):
        self.game = self.var.get()
        if self.game == "Select Card Game":
            self.tryAgain()
            return
        if self.game == "Add New Game":
            self.addNewGame()
        self.window.destroy()
        cardInformation(tk.Tk(), "Card Information", self.game)

    def editTemplate(self):
        self.game = self.var.get()
        if self.game == "Select Card Game":
            self.tryAgain()
            return
        if self.game == "Add New Game":
            self.addNewGame()
        self.window.destroy()
        editTemplate(tk.Tk(), "Edit Saved Templates", self.game)

    def newTemplate(self):
        self.game = self.var.get()
        if self.game == "Select Card Game":
            self.tryAgain()
            return
        if self.game == "Add New Game":
            self.addNewGame()
        self.window.destroy()
        createTemplates(tk.Tk(), "Add New Templates", self.game)

    def scanCards(self):
        self.game = self.var.get()
        if self.game == "Select Card Game":
            self.tryAgain()
            return
        if self.game == "Add New Game":
            self.addNewGame()
        self.window.destroy()
        scanCards(tk.Tk(), "Scan Cards", self.game)

    def tryAgain(self):
        system('say -v Samantha Select a card game first')

    def addNewGame(self):
        game = newGame()
        self.game = game.nameOfGame
        if not os.path.exists(self.game):
            os.mkdir(self.game)
            os.mkdir(self.game + '/cardTemplates')
            os.mkdir(self.game + '/cardSymbols')
            os.mkdir(self.game + '/processCards')
            os.mkdir(self.game + '/processSymbols')


class newGame:
    def __init__(self):
        self.nameOfGame = None
        self.subRoot = tk.Toplevel()
        self.subRoot.title("Add New Game")

        tk.Label(self.subRoot, text='Name of Game').pack()
        self.regionName = tk.Entry(self.subRoot)
        self.regionName.pack()

        self.nextButton = tk.Button(self.subRoot, text="Confirm", width=15, command=self.saveInfo)
        self.nextButton.pack()

        self.subRoot.mainloop()

    def saveInfo(self):
        name = self.regionName.get()
        self.nameOfGame = name
        self.subRoot.quit()
        self.subRoot.destroy()
