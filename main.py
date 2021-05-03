# https://www.pyimagesearch.com/2019/09/02/opencv-stream-video-to-web-browser-html-page/
# https://stackoverflow.com/questions/4710067/using-python-for-deleting-a-specific-line-in-a-file
# https://dzone.com/articles/flask-101-adding-a-database
# https://www.geeksforgeeks.org/convert-text-and-text-file-to-pdf-using-python/
# https://mecaruco2.readthedocs.io/en/latest/notebooks_rst/Aruco/aruco_basics.html
import jinja2
from matchTemplate import *
from app import app
from scanningCards import scanningCards
from collections import OrderedDict
from flask import render_template, request, redirect, url_for, Flask, Response
from textToBraille import *
from imutils.video import VideoStream
import pytesseract
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import cv2
import glob
import zipfile
from playsound import playsound
import os
import imutils
import time
import threading
from PIL import Image
from os import path, system
from fpdf import FPDF
from PyPDF2 import PdfFileMerger, PdfFileReader
import re
from readTextAndSymbols import textAndSymbols
from readSymbols import getSymbolName

outputFrame = None
t = None
lock = threading.Lock()
videoDone = False
ifBoard = False
ifInstructions = False
ifDice = False
ifCards = False
ifTokens = False
# initialize the video stream and allow the camera sensor to warmup
# vs = VideoStream(src=0).start()
labelsNum = 0
cardNum = 0
boardW = 20
boardH = 20
cardGame = 'Tester'
theCardInfoFile = ' '
lastImageFile = ' '
templateName = ' '
cardTypeName = 'Nothing'


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/boardBrailleInfo")
def boardBrailleInfo():
    global cardGame
    return render_template("boardBrailleInfo.html", cardGame=cardGame)


@app.route("/aboutAccessibility")
def aboutAccessibility():
    return render_template("aboutAccessibility.html")


@app.route("/accessibilityInstructions", methods=['GET', 'POST'])
def accessibilityInstructions():
    global cardGame
    if request.method == "POST":
        theInstructions = ''
        theInstructions = request.form.get('accessibilityInstructions', theInstructions)
        generateAccessibilityInstructionsPDF(theInstructions)
        return render_template("theChecklist.html", cardGame=cardGame, board=ifBoard, instruct=ifInstructions,
                               dice=ifDice, cards=ifCards, tokens=ifTokens)
    else:
        return render_template("accessibilityInstructions.html")


@app.route("/gameInstructions", methods=['GET', 'POST'])
def gameInstructions():
    global cardGame
    if request.method == "POST":
        if 'theeInstructions' not in request.files:
            theInstructions = ''
            theInstructions = request.form.get('instructions', theInstructions)
            generateInstructionsPDF(theInstructions)
        else:
            theFile = request.files['theeInstructions']
            theFile.save(os.path.join(app.config["FINAL_UPLOADS"], 'gameInstructions.pdf'))

        return render_template("accessibilityInstructions.html")
    else:
        return render_template("gameInstructions.html", cardGame=cardGame)


@app.route("/accessWays")
def accessWays():
    global cardGame
    return render_template("accessWays.html", cardGame=cardGame)


@app.route("/gameSpecs", methods=['GET', 'POST'])
def gameSpecs():
    global cardGame, boardH, boardW, ifBoard, ifInstructions, ifDice, ifCards, ifTokens
    if request.method == "POST":
        cardGame = request.form.get('gameName', cardGame)
        ifBoard = request.form.get('feature1', ifBoard)
        ifInstructions = request.form.get('feature2', ifInstructions)
        ifDice = request.form.get('feature3', ifDice)
        ifCards = request.form.get('feature4', ifCards)
        ifTokens = request.form.get('feature5', ifTokens)

        if ifBoard is not False:
            boardW = request.form.get('boardWidth', boardW)
            boardH = request.form.get('boardHeight', boardH)

        return render_template("theChecklist.html", cardGame=cardGame, board=ifBoard, instruct=ifInstructions,
                               dice=ifDice, cards=ifCards, tokens=ifTokens)
    else:
        return render_template("gameSpecs.html")


@app.route("/diceSpinner", methods=['GET', 'POST'])
def diceSpinner():
    global cardGame
    if request.method == 'POST':
        theMinNum = 0
        theMaxNum = 0

        theMinNum = request.form.get("minDice", theMinNum)
        theMaxNum = request.form.get("maxDice", theMaxNum)

        for i in range(int(theMinNum), int(theMaxNum) + 1):
            translateToDiceBraille(str(i))

        generateDicePDF()
        return render_template("theChecklist.html", cardGame=cardGame, board=ifBoard, instruct=ifInstructions,
                               dice=ifDice, cards=ifCards, tokens=ifTokens)
    else:
        return render_template("diceSpinner.html", cardGame=cardGame)


@app.route("/theChecklist", methods=['GET', 'POST'])
def theChecklist():
    global cardGame, ifBoard, ifInstructions, ifDice, ifCards, ifTokens
    return render_template("theChecklist.html", cardGame=cardGame, board=ifBoard, instruct=ifInstructions,
                           dice=ifDice, cards=ifCards, tokens=ifTokens)


@app.route("/boardTactileInfo")
def boardTactileInfo():
    global cardGame
    return render_template("boardTactileInfo.html", cardGame=cardGame)


@app.route("/theBoardBraille", methods=['GET', 'POST'])
def theBoardBraille():
    global cardGame
    if request.method == "POST":
        if request.files:
            image = request.files["board"]
            image.save(os.path.join(app.config["BOARD_UPLOADS"], 'theBoard.png'))
            img = cv2.imread('static/uploads/theBoard.png')
            resized = cv2.resize(img, (775, 775), interpolation=cv2.INTER_AREA)
            cv2.imwrite('static/uploads/theBoard.png', resized)

            return render_template("boardBrailleAnnotation.html", cardGame=cardGame)
    else:
        return render_template("theBoardBraille.html", cardGame=cardGame)


@app.route("/theBoardTactile", methods=['GET', 'POST'])
def theBoardTactile():
    global cardGame
    if request.method == "POST":
        if request.files:
            image = request.files["board"]
            image.save(os.path.join(app.config["BOARD_UPLOADS"], 'theBoard.png'))
            img = cv2.imread('static/uploads/theBoard.png')
            resized = cv2.resize(img, (775, 775), interpolation=cv2.INTER_AREA)
            cv2.imwrite('static/uploads/theBoard.png', resized)

            return render_template("boardTactileAnnotation.html", cardGame=cardGame)
    else:
        return render_template("theBoardTactile.html", cardGame=cardGame)


@app.route("/boardAnnotation", methods=['GET', 'POST'])
def boardAnnotation():
    if request.method == "POST":
        boardFiles = request.files.getlist('board[]')
        for index in range(0, len(boardFiles)):
            fileName = str(boardFiles[index])
            if 'boardImage' in fileName:
                boardFiles[index].save(os.path.join(app.config["FINAL_UPLOADS"], 'finalBoard.jpeg'))
            if 'tactileOverlay' in fileName:
                boardFiles[index].save(os.path.join(app.config["FINAL_UPLOADS"], 'finalBoard.pdf'))
            if 'lasercut' in fileName:
                boardFiles[index].save(os.path.join(app.config["FINAL_UPLOADS"], 'lasercut.jpeg'))

        generateBoardPDF()
        return render_template("boardPreview.html")
    else:
        return render_template("boardAnnotation.html")


@app.route("/boardBrailleAnnotation", methods=['GET', 'POST'])
def boardBrailleAnnotation():
    global cardGame
    return render_template("boardBrailleAnnotation.html", cardGame=cardGame)


@app.route("/boardTactileAnnotation", methods=['GET', 'POST'])
def boardTactileAnnotation():
    global cardGame, boardW, boardH
    if request.method == "POST":
        boardFiles = request.files.getlist('board[]')
        for index in range(0, len(boardFiles)):
            fileName = str(boardFiles[index])
            if 'boardImage' in fileName:
                boardFiles[index].save(os.path.join(app.config["FINAL_UPLOADS"], 'finalBoard.jpeg'))
            if 'tactileOverlay' in fileName:
                boardFiles[index].save(os.path.join(app.config["FINAL_UPLOADS"], 'finalBoard.pdf'))
            if 'lasercut' in fileName:
                boardFiles[index].save(os.path.join(app.config["FINAL_UPLOADS"], 'lasercut.jpeg'))

        generateBoardPDF()
        return render_template("theChecklist.html", cardGame=cardGame, board=ifBoard, instruct=ifInstructions,
                               dice=ifDice, cards=ifCards, tokens=ifTokens)
    else:
        return render_template("boardTactileAnnotation.html", cardGame=cardGame, boardW=boardW, boardH=boardH)


@app.route("/tester", methods=['GET', 'POST'])
def tester():
    # filename = 'participantData.zip'
    return render_template('tester.html')


@app.route("/boardPreview", methods=['GET', 'POST'])
def boardPreview():
    return render_template("boardPreview.html")


@app.route("/cardPreview", methods=['GET', 'POST'])
def cardPreview():
    return render_template("cardPreview.html")


@app.route("/accessKit", methods=['GET', 'POST'])
def accessKit():
    generateAccessKitPDF()
    return render_template("accessKit.html", cardGame=cardGame)


@app.route("/gamePieces", methods=['GET', 'POST'])
def gamePieces():
    global cardGame
    if request.method == 'POST':
        distinguishable = ''
        gamePieces = ''
        playerPieces = ''
        maxPieces = ''
        extraPieces = ''
        theMinNum = 0
        theMaxNum = 0

        # gamePieces = request.form.get('gamePieces', gamePieces)
        playerPieces = request.form.get('playerPieces', playerPieces)
        maxPieces = request.form.get("maxPieces", maxPieces)
        extraPieces = request.form.get("extraPieces", extraPieces)
        totalPieces = int(playerPieces) * int(maxPieces) + int(extraPieces)
        for i in range(1, totalPieces + 1):
            translateToPiecesBraille(str(i))
        '''
        yesDice = request.form['diceYesOrNo']
        if yesDice == 'yes':
            theMinNum = request.form.get("minDice", theMinNum)
            theMaxNum = request.form.get("maxDice", theMaxNum)


        if yesDice == 'yes':
            for i in range(int(theMinNum), int(theMaxNum) + 1):
                translateToDiceBraille(str(i))
        '''
        generatePiecesPDF()
        return render_template("theChecklist.html", cardGame=cardGame, board=ifBoard, instruct=ifInstructions,
                               dice=ifDice, cards=ifCards, tokens=ifTokens)
    else:
        return render_template("gamePieces.html", cardGame=cardGame)


@app.route("/piecePreview", methods=['GET', 'POST'])
def piecePreview():
    return render_template("piecePreview.html")


@app.route("/theCards")
def theCards():
    global cardGame
    return render_template("theCards.html", cardGame=cardGame)


@app.route("/cardUpload", methods=['GET', 'POST'])
def cardUpload():
    global cardNum
    if request.method == "POST":
        imageFiles = request.files.getlist('cards[]')
        for index in range(0, len(imageFiles)):
            fileName = str(cardNum) + '.png'
            cardUploadFile = open("static/userData/cardUploads.txt", "a+")
            cardUploadFile.write(imageFiles[index].filename + '\n')
            imageFiles[index].save(os.path.join(app.config["CARD_UPLOADS"], fileName))
            cardFile = 'static/newCards/' + fileName
            img = cv2.imread(cardFile)
            resized = cv2.resize(img, (400, 400), interpolation=cv2.INTER_AREA)
            cv2.imwrite(cardFile, resized)
            cardNum = cardNum + 1

        return render_template("cardUpload.html", cardGame=cardGame)
    else:
        return render_template("cardUpload.html", cardGame=cardGame)


@app.route("/remainingSymbols", methods=['GET', 'POST'])
def remainingSymbols():
    return render_template("remainingSymbols.html", cardGame=cardGame)


@app.route("/symbolDirections", methods=['GET', 'POST'])
def symbolDirections():
    return render_template("symbolDirections.html", cardGame=cardGame)


@app.route("/cardParts", methods=['GET', 'POST'])
def cardParts():
    return render_template("cardParts.html", cardGame=cardGame)


@app.route("/newTemplate", methods=['GET', 'POST'])
def newTemplate():
    global templateName
    cardFileName = ''
    newCardName = ''
    cardFile = ''
    templateNames = []
    regionList = []
    for filename in os.listdir('static/newCards/'):
        templateNames.append(filename)

    return render_template("newTemplate.html", cardGame=cardGame, templateNames=templateNames,
                           templateLen=len(templateNames))


@app.route("/newSymbol", methods=['GET', 'POST'])
def newSymbol():
    global templateName, lastImageFile
    templateNames = []
    for filename in os.listdir('static/newCards/'):
        templateNames.append(filename)
    if request.method == 'POST':
        symbolName = ''
        symbolCoors = '0'
        cardName = ''

        cardName = request.form.get('symbolTemplateName', cardName)
        symbolName = request.form.get('theSymbolName', symbolName)
        symbolCoors = request.form.get("symbolCoors", symbolCoors)
        # print(cardName)

        symbolImage = cv2.imread('static/newCards/' + cardName)
        symbolCoors = re.sub('\(', '', symbolCoors)
        symbolCoors = re.sub('\)', '', symbolCoors)
        symbolCoors = re.sub(',', ' ', symbolCoors)
        symbolCoors = symbolCoors.split(' ')
        x, y, w, h = symbolCoors

        croppedImage = symbolImage[int(y):int(h), int(x):int(w)]
        fileName = 'static/cardSymbols/' + symbolName + '.jpg'
        cv2.imwrite(fileName, croppedImage)
        return redirect(url_for('newSymbol', templateName=templateName, cardName=lastImageFile))
    else:
        return render_template("newSymbol.html", cardGame=cardGame, templateNames=templateNames,
                               templateLen=len(templateNames), cardName=lastImageFile)


@app.route("/symbolPreview", methods=['GET', 'POST'])
def symbolPreview():
    symbolCoors = request.get_json()
    symbolCoors = symbolCoors.split(' ')
    symbolCoors[0] = re.sub('\(', '', symbolCoors[0])
    symbolCoors[0] = re.sub('\)', '', symbolCoors[0])
    symbolCoors[0] = re.sub(',', ' ', symbolCoors[0])
    symbolCoors[0] = symbolCoors[0].split(' ')
    x = symbolCoors[0][0]
    y = symbolCoors[0][1]
    w = symbolCoors[0][2]
    h = symbolCoors[0][3]
    fileName = symbolCoors[1]
    fileName = 'static/newCards/' + fileName
    symbolImage = cv2.imread(fileName)
    # print(x, y, w, h)
    croppedImage = symbolImage[int(y):int(h), int(x):int(w)]
    if int(h) < int(y):
        tempY = y
        h = y
        y = tempY
    if int(x) > int(w):
        tempX = x
        w = x
        x = tempX
    if int(x) == int(w):
        return
    if int(y) == int(h):
        return
    cv2.imwrite('static/userData/symbolPreview.jpg', croppedImage)
    return "Done"


@app.route("/scanCards")
def scanCards():
    t = threading.Thread(target=getContours())
    t.daemon = True
    t.start()
    return render_template("scanCards.html", cardGame=cardGame)


@app.route("/printLabel", methods=['GET', 'POST'])
def printLabel():
    cardText = ''
    global theCardInfoFile, labelsNum
    templateNames = []
    for filename in os.listdir('static/newCards/'):
        templateNames.append(filename)
    if request.method == 'POST':
        system('say -v Samantha Reading text from card. Please wait')
        template = ' '
        template = request.form.get('templateNames', template)
        cardFile = 'static/newCards/' + template
        theCardInfoFile = cardFile
        '''
        cardText = readCardText(cardFile)
        if cardText is None or len(cardText) == 0:
            cardText = pytesseract.image_to_string(Image.open(cardFile))
            if len(cardText) == 0:
                cardText = 'ERROR: Type in text from card. Unable to read'
        '''
        cardText = pytesseract.image_to_string(Image.open(cardFile))
        if len(cardText) == 0:
            cardText = 'ERROR: Type in text from card. Unable to read'
        return render_template("printLabel.html", templateNames=templateNames, templateLen=len(templateNames),
                               img=cardFile, text=cardText, cardGame=cardGame, labelNum=labelsNum)
    else:
        return render_template("printLabel.html", templateNames=templateNames, templateLen=len(templateNames),
                               img="static/orange.png", text="", cardGame=cardGame, labelNum=labelsNum)


@app.route("/symbolImage")
def symbolImage():
    return "symbolPreview.jpg"


@app.route("/saveLabel", methods=['POST'])
def saveLabel():
    global theCardInfoFile, labelsNum
    cardText = request.get_json()
    theCardText = str(cardText)
    # print(theCardText)
    theCardInfoFile = str(theCardInfoFile)
    theCardText = re.sub('\n', ' ', theCardText)
    theCardFile = open("static/userData/cardInfo.txt", "a+")
    theLabelFile = open("static/userData/labelsGenerated.txt", "a+")
    theCardFile.write(theCardInfoFile + ',' + theCardText + '\n')
    theCardInfoFile = theCardInfoFile.split('/')
    theLabelFile.write(theCardInfoFile[2] + " " + theCardText + '\n')
    labelNum = getLabelNums()
    labelsNum = labelNum
    system('say -v Samantha Label saved. Next')
    return str(labelNum)


@app.route("/saveBraille", methods=['POST'])
def saveBraille():
    global theCardInfoFile
    brailleText = request.get_json()
    brailleText = str(brailleText)
    brailleText = brailleText.split('\n')
    for x in brailleText:
        translateToBoardBraille(str(x))
    return "Done"


@app.route("/saveCardRegions", methods=['POST'])
def saveCardRegions():
    global cardTypeName
    cardRegionText = request.get_json()
    print(cardRegionText)
    cardRegionText = str(cardRegionText)
    cardRegionText = cardRegionText.split('\t')
    if cardRegionText[0] == '':
        cardRegionText[0] = cardTypeName
    else:
        cardTypeName = cardRegionText[0]

    cardFileName = 'static/newCards/' + cardRegionText[0]
    newCardName = 'static/cardTemplates/' + cardRegionText[1] + '.png'
    cardFile = cv2.imread(cardFileName)
    cv2.imwrite(newCardName, cardFile)

    theCardRegionFile = open("static/userData/regions.txt", "a+")
    if cardRegionText[2] == 'yesText':
        cardRegionText[5] = cardRegionText[5] + 'Text'
    if cardRegionText[3] == 'yesSymbols':
        cardRegionText[5] = cardRegionText[5] + 'Symbols'
    if cardRegionText[4] == 'isColor':
        cardRegionText[5] = cardRegionText[5] + 'Color'
    cardRegionString = cardRegionText[1] + ".png " + cardRegionText[5] + ":" + cardRegionText[6] + '\n'
    theCardRegionFile.write(str(cardRegionString))

    return "Done"


@app.route("/saveCardSymbols", methods=['POST'])
def saveCardSymbols():
    cardSymbolText = request.get_json()
    cardSymbolText = str(cardSymbolText)
    cardSymbolText = cardSymbolText.split('\t')
    symbolImage = cv2.imread('static/newCards/' + cardSymbolText[0])
    cardSymbolText[2] = re.sub('\(', '', cardSymbolText[2])
    cardSymbolText[2] = re.sub('\)', '', cardSymbolText[2])
    cardSymbolText[2] = re.sub(',', ' ', cardSymbolText[2])
    cardSymbolText[2] = cardSymbolText[2].split(' ')
    x, y, w, h = cardSymbolText[2]
    tempX = 0
    tempW = 0
    tempY = 0
    tempH = 0
    if int(h) < int(y):
        tempX = x
        tempW = w
        w = x
        x = tempW
        tempY = y
        tempH = h
        h = y
        y = tempH
    elif int(x) > int(w):
        tempX = x
        tempW = w
        w = x
        x = tempW
        tempY = y
        tempH = h
        h = y
        y = tempH
    elif int(x) == int(w):
        return "not rect"
    elif int(y) == int(h):
        return "not rect"
    croppedImage = symbolImage[int(y):int(h), int(x):int(w)]
    fileName = 'static/cardSymbols/' + cardSymbolText[1] + '.jpg'
    cv2.imwrite(fileName, croppedImage)
    theSymbolsFile = open("static/userData/symbols.txt", "a+")
    theSymbolsFile.write(cardSymbolText[1] + '\n')
    return "Done"


@app.route("/saveLastImage", methods=['POST'])
def saveLastImage():
    global lastImageFile
    # print('saving image name')
    imageName = request.get_json()
    imageName = str(imageName)
    lastImageFile = imageName
    # print(imageName)
    return "Saved"


@app.route("/removeLastRegion", methods=['POST', 'GET'])
def removeLastRegion():
    with open('static//userData/regions.txt') as f1:
        lines = f1.readlines()

    with open('static/userData/regions.txt', 'w') as f2:
        f2.writelines(lines[:-1])

    return "finished"


@app.route("/removeLastSymbol", methods=['POST', 'GET'])
def removeLastSymbol():
    with open('static/userData/symbols.txt') as f1:
        lines = f1.readlines()
    sizeofFile = len(lines)
    fileToDelete = "static/cardSymbols/" + lines[sizeofFile - 1] + ".jpg"
    if os.path.exists(fileToDelete):
        os.remove(fileToDelete)
        with open('static/userData/symbols.txt', 'w') as f2:
            f2.writelines(lines[:-1])
    else:
        print('file does not exist')

    return "finished"


def readCardText(cardFile):
    finalText = ''
    # print(cardFile)
    # templateName = matchTemplate(cardFile)
    if templateName is None:
        return
    theImage = cv2.imread(cardFile)
    allRegionCoors = {}
    f = open("static/userData/regions.txt", "r")
    f1 = f.readlines()

    for x in f1:
        line = re.split('\s', x)
        for name in line[1:]:
            regionNames = []
            name = re.sub(':', ' ', name)
            labelName = re.split('\s', name)
            if line[0] == templateName and len(labelName) > 1:
                labelName[1] = re.sub('\(', '', labelName[1])
                labelName[1] = re.sub('\)', '', labelName[1])
                labelName[1] = re.sub(',', ' ', labelName[1])
                regionNames.append(labelName[1])
                regionNames = list(filter(lambda a: a != '', regionNames))
                regionCoors = re.split('\s', regionNames[0])
                x, y, w, h = regionCoors
                regionCoors.append(labelName[0])
                midpoint = (int(x) + int(w)) / 2, (int(y) + int(h)) / 2
                allRegionCoors[midpoint] = regionCoors

    allRegionCoors = OrderedDict(sorted(allRegionCoors.items(), key=lambda k: [k[0][1], k[0][0]]))
    for regionName, regionCoors in allRegionCoors.items():
        tempX = 0
        tempW = 0
        tempY = 0
        tempH = 0
        x, y, w, h, _ = regionCoors
        if int(h) < int(y):
            tempX = x
            tempW = w
            w = x
            x = tempW
            tempY = y
            tempH = h
            h = y
            y = tempH
        elif int(x) > int(w):
            tempX = x
            tempW = w
            w = x
            x = tempW
            tempY = y
            tempH = h
            h = y
            y = tempH
        elif int(x) == int(w):
            continue
        elif int(y) == int(h):
            continue
        croppedImage = theImage[int(y):int(h), int(x):int(w)]
        cv2.imwrite("extractedRegion.jpg", croppedImage)

        if 'Symbols' in regionCoors[4] and 'Text' in regionCoors[4]:
            text = textAndSymbols('extractedRegion.jpg')
            finalText = finalText + ' ' + text
            continue
        if 'Color' in regionCoors[4]:
            # text = getDominantColor('extractedRegion.jpg')
            finalText = finalText + ' ' + text + ' card'
            continue
        if 'Text' in regionCoors[4]:
            text = pytesseract.image_to_string(Image.open('extractedRegion.jpg'))
            finalText = finalText + ' ' + text
            continue
        if 'Symbols' in regionCoors[4]:
            text = getSymbolName('extractedRegion.jpg')
            finalText = finalText + ' ' + text
            continue

    return finalText


def generatePiecesPDF():
    # save FPDF() class into
    # a variable pdf
    pdf = FPDF()
    pdf.add_page()

    # set style and size of font
    # that you want in the pdf

    pdf.set_font("Arial", size=30)
    pdf.multi_cell(200, 5, txt='Braille Labels for Game Pieces\n\n', align='C')
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(200, 5, txt='Cut out Braille labels and paste them onto the game pieces.\n\n', align='C')

    pdf.add_font('Braille', '', 'static/Swell-Braille.ttf', uni=True)
    index = 0
    theText = ['0', '0']
    # open the text file in read mode
    f = open("static/userData/brailleForPieces.txt", "r")
    # insert the texts in pdf
    theX = pdf.get_x()
    theY = pdf.get_y()
    for x in f:
        if theX >= 170:
            theX = 5
            theY += 15
            if theY >= 260:
                pdf.add_page()
                theY = 15
        if index == 0:
            pdf.set_xy(theX - 5, theY)
        if index > 0:
            pdf.set_xy(theX + 17, theY)
        if index % 6 == 0:
            theX = 5
            if int(theText[0]) > 9:
                theY += 15
            pdf.set_xy(theX, theY)
        theX = pdf.get_x()
        theY = pdf.get_y()
        theText = x.split(':')
        pdf.set_font("Arial", size=8)
        pdf.multi_cell(15, 10, txt=theText[0], align='R')
        pdf.set_font('Braille', '', 24)
        pdf.set_xy(theX + 15, theY)
        theX = pdf.get_x()
        theY = pdf.get_y()
        pdf.multi_cell(27, 10, txt=theText[1], align='L', border=1)
        index += 1
    # save the pdf with name .pdf
    pdf.output("static/userData/thePieces.pdf")
    '''
    if os.path.exists("static/userData/brailleForDice.txt"):
        pdf.add_page()

        # set style and size of font
        # that you want in the pdf

        pdf.set_font("Arial", size=30)
        pdf.multi_cell(200, 5, txt='Braille Labels for Dice/Spinner\n\n', align='C')
        pdf.set_font("Arial", size=10)
        pdf.multi_cell(200, 5, txt='Cut out Braille labels and paste them onto the dice/spinner.\n\n', align='C')

        index = 0
        f = open("static/userData/brailleForDice.txt", "r")
        # insert the texts in pdf
        theX = pdf.get_x()
        theY = pdf.get_y()
        for x in f:
            if theX >= 170:
                theX = 5
                theY += 15
                if theY >= 260:
                    pdf.add_page()
                    theY = 15
            if index == 0:
                pdf.set_xy(theX - 5, theY)
            if index > 0:
                pdf.set_xy(theX + 17, theY)
            if index % 6 == 0:
                if int(theText[0]) > 9:
                    theY += 15
                theX = 5
                pdf.set_xy(theX, theY)
            theX = pdf.get_x()
            theY = pdf.get_y()
            theText = x.split(':')
            pdf.set_font("Arial", size=8)
            pdf.multi_cell(15, 10, txt=theText[0], align='R')
            pdf.set_font('Braille', '', size=24)
            pdf.set_xy(theX + 15, theY)
            theX = pdf.get_x()
            theY = pdf.get_y()
            pdf.multi_cell(27, 10, txt=theText[1], align='L', border=1)
            index += 1
        '''


def generateInstructionsPDF(theText):
    global cardGame
    # save FPDF() class into
    # a variable pdf
    pdf = FPDF()
    pdf.add_page()

    # set style and size of font
    # that you want in the pdf

    pdf.set_font("Arial", size=30)
    pdf.multi_cell(200, 5, txt='Game Instructions for ' + cardGame + ' \n\n', align='C')
    pdf.set_font("Arial", size=20)
    pdf.multi_cell(200, 10, txt=theText, align='C')

    # save the pdf with name .pdf
    pdf.output("static/userData/gameInstructions.pdf")


def generateAccessibilityInstructionsPDF(theText):
    global cardGame
    # save FPDF() class into
    # a variable pdf
    pdf = FPDF()
    pdf.add_page()

    # set style and size of font
    # that you want in the pdf

    pdf.set_font("Arial", size=30)
    pdf.multi_cell(200, 5, txt='Accessibility Instructions for ' + cardGame + ' \n\n', align='C')
    pdf.set_font("Arial", size=20)
    pdf.multi_cell(200, 10, txt=theText, align='C')

    # save the pdf with name .pdf
    pdf.output("static/userData/accessibilityInstructions.pdf")


def generateDicePDF():
    # save FPDF() class into
    # a variable pdf
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font('Braille', '', 'static/Swell-Braille.ttf', uni=True)

    # set style and size of font
    # that you want in the pdf

    pdf.set_font("Arial", size=30)
    pdf.multi_cell(200, 5, txt='Braille Labels for Dice/Spinner\n\n', align='C')
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(200, 5, txt='Cut out Braille labels and paste them onto the dice/spinner.\n\n', align='C')

    index = 0
    theText = ['0', '0']
    f = open("static/userData/brailleForDice.txt", "r")
    # insert the texts in pdf
    theX = pdf.get_x()
    theY = pdf.get_y()
    for x in f:
        if theX >= 170:
            theX = 5
            theY += 15
            if theY >= 260:
                pdf.add_page()
                theY = 15
        if index == 0:
            pdf.set_xy(theX - 5, theY)
        if index > 0:
            pdf.set_xy(theX + 17, theY)
        if index % 6 == 0:
            if int(theText[0]) > 9:
                theY += 15
            theX = 5
            pdf.set_xy(theX, theY)
        theX = pdf.get_x()
        theY = pdf.get_y()
        theText = x.split(':')
        pdf.set_font("Arial", size=8)
        pdf.multi_cell(15, 10, txt=theText[0], align='R')
        pdf.set_font('Braille', '', size=24)
        pdf.set_xy(theX + 15, theY)
        theX = pdf.get_x()
        theY = pdf.get_y()
        pdf.multi_cell(27, 10, txt=theText[1], align='L', border=1)
        index += 1

    # save the pdf with name .pdf
    pdf.output("static/userData/theDiceSpinner.pdf")


def generateBoardPDF():
    pdf = FPDF()
    # Add a page
    pdf.add_page()

    # set style and size of font
    # that you want in the pdf
    pdf.set_font("Arial", size=15)
    pdf.cell(200, 5, txt='Tactile Overlay for Board', ln=1, align='C')
    pdf.image('static/finalFiles/finalBoard.jpeg', x=5, y=30, w=200, h=200)

    if os.path.exists("static/userData/brailleForBoard.txt"):
        pdf.add_page()
        pdf.set_font("Arial", size=30)
        pdf.cell(200, 5, txt='Braille Labels for Board', ln=1, align='C')
        pdf.add_font('Braille', '', 'static/qbraille-regular.ttf', uni=True)

        # open the text file in read mode
        f = open("static/userData/brailleForBoard.txt", "r")
        # insert the texts in pdf
        for x in f:
            theText = x.split(':')
            theText[0] = re.sub('[^A-Za-z0-9 ]+', '', theText[0])
            pdf.set_font("Arial", size=10)
            pdf.multi_cell(200, 10, txt=theText[0], align='L')
            pdf.set_font('Braille', '', size=24)
            pdf.multi_cell(200, 10, txt=theText[0], align='L')
    generateTactileTitlePage()
    # save the pdf with name .pdf
    pdf.output("static/userData/theBoard.pdf")


def generateTitlePage():
    global cardGame
    # save FPDF() class into
    # a variable pdf
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=40)
    pdf.cell(200, 50, txt='Accessibility Kit for', ln=50, align='C')
    pdf.cell(200, 55, txt=cardGame, ln=55, align='C')

    pdf.output("static/userData/titlePage.pdf")


def generateTactileTitlePage():
    # save FPDF() class into
    # a variable pdf
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=40)
    pdf.cell(200, 50, txt='Tactile Overlay Template', ln=50, align='C')
    pdf.cell(200, 50, txt='for Board', ln=50, align='C')

    pdf.output("static/userData/tactileTitlePage.pdf")


@app.route("/generateCardPDF", methods=['POST', 'GET'])
def generateCardPDF():
    # save FPDF() class into
    # a variable pdf
    pdf = FPDF()

    # Add a page
    pdf.add_page()
    pdf.set_font("Arial", size=30)
    pdf.multi_cell(200, 5, txt='Braille Labels for Cards\n\n', align='C')
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(200, 5, txt='Cut out Braille labels and paste them onto the cards.\n\n', align='C')
    # set style and size of font
    # that you want in the pdf
    pdf.set_font("Arial", size=15)
    pdf.add_font('Braille', '', 'static/qbraille-regular.ttf', uni=True)
    # open the text file in read mode
    f = open("static/userData/cardInfo.txt", "r")
    index = 0
    # insert the texts in pdf
    for x in f:
        if index > 0:
            pdf.add_page()
        theText = x.split(',')
        x = x.replace(theText[0], '')
        x = x.replace(',', ' ')
        x = re.sub('[^A-Za-z0-9 ]+', '', x)
        pdf.image(theText[0], x=None, y=None, w=20, h=25)
        pdf.set_font("Arial", size=10)
        pdf.multi_cell(200, 10, txt=x, align='C')
        pdf.set_font('Braille', '', size=24)
        pdf.multi_cell(70, 10, txt=x, align='C', border=1)
        index += 1

    # save the pdf with name .pdf
    pdf.output("static/userData/theCards.pdf")
    return "generated"


@app.route("/generateAccessKitPDF", methods=['POST', 'GET'])
def generateAccessKitPDF():
    global cardGame
    generateTitlePage()
    merger = PdfFileMerger()
    newOne = PdfFileMerger()
    title = 'static/userData/titlePage.pdf'
    instructions = 'static/userData/gameInstructions.pdf'
    accessibility = 'static/userData/accessibilityInstructions.pdf'
    board = 'static/userData/theBoard.pdf'
    cards = 'static/userData/theCards.pdf'
    pieces = 'static/userData/thePieces.pdf'
    tactileTitle = 'static/userData/tactileTitlePage.pdf'
    overlay = 'static/finalFiles/finalBoard.pdf'
    if path.exists(title):
        merger.append(PdfFileReader(title))
        newOne.append(PdfFileReader(title))
    if path.exists(instructions):
        merger.append(PdfFileReader(instructions))
        newOne.append(PdfFileReader(instructions))
    if path.exists(accessibility):
        merger.append(PdfFileReader(accessibility))
        newOne.append(PdfFileReader(accessibility))
    if path.exists(board):
        merger.append(PdfFileReader(board))
        newOne.append(PdfFileReader(board))
    if path.exists(cards):
        merger.append(PdfFileReader(cards))
        newOne.append(PdfFileReader(cards))
    if path.exists(pieces):
        merger.append(PdfFileReader(pieces))
        newOne.append(PdfFileReader(pieces))
    if path.exists(tactileTitle):
        merger.append(PdfFileReader(tactileTitle))
        newOne.append(PdfFileReader(tactileTitle))
    if path.exists(overlay):
        merger.append(PdfFileReader(overlay))
        newOne.append(PdfFileReader(overlay))
    filename = 'static/userData/accessibilityKit.pdf'
    uploadFile = 'static/finalFiles/accessibilityKit.pdf'
    merger.write(filename)
    newOne.write(uploadFile)
    generateParticipantData()
    return "fin"


def generateParticipantData():
    read_files = glob.glob("static/userData/*.txt")
    with open("static/uploads/participantData.txt", "wb") as outfile:
        for f in read_files:
            with open(f, "rb") as infile:
                outfile.write(infile.read())

    zipTheFiles()


def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))


def zipTheFiles():
    zipf = zipfile.ZipFile('static/participantData.zip', 'w', zipfile.ZIP_DEFLATED)
    # zipdir('static/cardSymbols', zipf)
    # zipdir('static/cardTemplates', zipf)
    zipdir('static/newCards', zipf)
    zipdir('static/cardUploads', zipf)
    zipdir('static/uploads', zipf)
    zipdir('static/finalFiles', zipf)
    zipdir('static/userData', zipf)
    zipf.close()


@app.route("/generateTextSuggestions", methods=['POST', 'GET'])
def generateTextSuggestions():
    cardFile = request.get_json()
    # Load image, grayscale, Gaussian blur, adaptive threshold
    image = cv2.imread(str(cardFile))
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # play with these numbers
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, 30)

    # Dilate to combine adjacent text contours
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 10))
    dilate = cv2.dilate(thresh, kernel, iterations=4)

    # Find contours, highlight text areas, and extract ROIs
    cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    for c in cnts:
        area = cv2.contourArea(c)
        if area > 50:
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(image, (x, y), (x + w, y + h), (36, 255, 12), 2)

    cv2.imwrite("static/userData/regionSuggestions.jpg", image)
    return "generated"


def getRegions():
    regionList = []
    f = open("static/userData/regions.txt", "r")
    for x in f:
        if templateName in x:
            line = x.split()
            line = line[1].split(':')
            regionList.append(line[0])
    return regionList


@app.route("/getLabelNums", methods=['POST'])
def getLabelNums():
    numLines = 0
    if os.path.exists("static/userData/cardInfo.txt"):
        file = open("static/userData/cardInfo.txt", "r")
        for line in file:
            line = line.strip("\n")
            numLines += 1

    return str(numLines)


def getCheckList(templateName):
    regionNames = []
    f = open("static/userData/regions.txt", "r")
    f1 = f.readlines()
    for x in f1:
        x = x.rstrip('\n')
        line = re.split('\s', x)
        for name in line[1:]:
            labelName = re.split('\s', name)
            if line[0] == templateName and len(labelName) > 0:
                for regions in labelName:
                    regionNames.append(regions)
    regionNames = list(filter(lambda a: a != '', regionNames))
    return regionNames


def drawRegions(image, templateName):
    allRegionCoors = []
    f = open("static/userData/regions.txt", "r")
    f1 = f.readlines()
    for x in f1:
        line = re.split('\s', x)
        for name in line[1:]:
            regionNames = []
            name = re.sub(':', ' ', name)
            labelName = re.split('\s', name)
            if line[0] == templateName:
                if len(labelName) == 1:
                    continue
                labelName[1] = re.sub('\(', '', labelName[1])
                labelName[1] = re.sub('\)', '', labelName[1])
                labelName[1] = re.sub(',', ' ', labelName[1])
                regionNames.append(labelName[1])
                regionNames = list(filter(lambda a: a != '', regionNames))
                regionCoors = re.split('\s', regionNames[0])
                allRegionCoors.append(regionCoors)

    for i in allRegionCoors:
        x, y, w, h = i
        cv2.rectangle(image, (int(x), int(y)), (int(w), int(h)), (0, 255, 0), 2)
        # self.croppedImage = self.newImage[int(y):int(y) + int(h), int(x):int(x) + int(w)]
        cv2.imwrite('static/userData/editImage.jpg', image)


# !!!remove password before commiting to GitHub!!!
@app.route("/sendEmail", methods=['POST'])
def sendEmail():
    print('sent pretend email')
    '''
    fromaddr = ""
    toaddr = ""

    # instance of MIMEMultipart
    msg = MIMEMultipart()

    # storing the senders email address
    msg['From'] = fromaddr

    # storing the receivers email address
    msg['To'] = toaddr

    # storing the subject
    msg['Subject'] = "Participant User Study Data"

    # string to store the body of the mail
    body = "Attached is the  zip file of the participant's data from the user study. GMJ4598"

    # attach the body with the msg instance
    msg.attach(MIMEText(body, 'plain'))

    # open the file to be sent
    filename = "participantData.zip"
    attachment = open("static/participantData.zip", "rb")

    # instance of MIMEBase and named as p
    p = MIMEBase('application', 'octet-stream')

    # To change the payload into encoded form
    p.set_payload((attachment).read())

    # encode into base64
    encoders.encode_base64(p)

    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)

    # attach the instance 'p' to instance 'msg'
    msg.attach(p)

    # creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)

    # start TLS for security
    s.starttls()

    # Authentication
    s.login(fromaddr, "")

    # Converts the Multipart msg into a string
    text = msg.as_string()

    # sending the mail
    s.sendmail(fromaddr, toaddr, text)

    # terminating the session
    s.quit()
    deleteFiles()
    '''
    return "finished"


@app.route("/deleteFiles", methods=['POST'])
def deleteFiles():
    if os.path.exists("static/extractedRegion.jpg"):
        os.remove("static/extractedRegion.jpg")

    filelist = [f for f in os.listdir('static/userData')]
    for f in filelist:
        os.remove(os.path.join('static/userData', f))
    filelist = [f for f in os.listdir('static/uploads')]
    for f in filelist:
        os.remove(os.path.join('static/uploads', f))
    filelist = [f for f in os.listdir('static/cardSymbols')]
    for f in filelist:
        os.remove(os.path.join('static/cardSymbols', f))
    filelist = [f for f in os.listdir('static/cardTemplates')]
    for f in filelist:
        os.remove(os.path.join('static/cardTemplates', f))
    filelist = [f for f in os.listdir('static/newCards')]
    for f in filelist:
        os.remove(os.path.join('static/newCards', f))
    filelist = [f for f in os.listdir('static/finalFiles')]
    for f in filelist:
        os.remove(os.path.join('static/finalFiles', f))

    return "erased"


@app.route("/saveImage")
def saveImage():
    global cardNum
    playsound('cameraClick.mp3')
    currImage = cv2.imread('static/perfectExample.jpg')
    fileName = 'static/newCards/' + str(cardNum) + '.png'
    cv2.imwrite(fileName, currImage)
    cardNum = cardNum + 1
    system('say -v Samantha Next card')
    return "Image saved"


def generate():
    # grab global references to the output frame and lock variables
    global outputFrame, lock

    # loop over frames from the output stream
    while True:
        # wait until the lock is acquired
        with lock:
            # check if the output frame is available, otherwise skip
            # the iteration of the loop
            if outputFrame is None:
                continue

            # encode the frame in JPEG format
            (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)

            # ensure the frame was successfully encoded
            if not flag:
                continue

        # yield the output frame in the byte format
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
               bytearray(encodedImage) + b'\r\n')


@app.route("/videoFeed")
def videoFeed():
    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")


def getContours():
    # grab global references to the video stream, output frame, and lock variables
    global vs, outputFrame, lock, currImage, videoDone

    template = scanningCards()

    # loop over frames from the video stream
    while True:
        if videoDone:
            break
        # read the next frame from the video stream, resize it
        frame = vs.read()
        frame = imutils.resize(frame, width=600)
        contour = template.showContours(frame)
        if contour is not None:
            (thresh, (minX, minY, maxX, maxY)) = contour
            cv2.rectangle(frame, (minX, minY), (maxX, maxY), (0, 0, 255), 2)
        template.getPerfectImage(frame)
        time.sleep(1.5)

        # acquire the lock, set the output frame, and release the lock
        with lock:
            outputFrame = frame.copy()


if __name__ == '__main__':
    # start the flask app
    app.run()
