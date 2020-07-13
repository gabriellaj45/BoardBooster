# https://www.pyimagesearch.com/2019/09/02/opencv-stream-video-to-web-browser-html-page/
# https://stackoverflow.com/questions/4710067/using-python-for-deleting-a-specific-line-in-a-file
# https://dzone.com/articles/flask-101-adding-a-database
# https://www.geeksforgeeks.org/convert-text-and-text-file-to-pdf-using-python/
# https://mecaruco2.readthedocs.io/en/latest/notebooks_rst/Aruco/aruco_basics.html
from creatingTemplates import creatingTemplates
from scanningCards import scanningCards
from matchTemplate import *
from readCardText import *
from imutils.video import VideoStream
from flask import Response
from flask import Flask
from flask import redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from models import *
from dbSetup import init_db, db_session
from app import app
from forms import *
from flask import flash, render_template, request, send_file
from models import CardInformation, CardGame
from playsound import playsound
from collections import OrderedDict
import threading
import pytesseract
from zipfile import ZipFile
import imutils
import time
import cv2
import os
import io
import pathlib
from os import path
from fpdf import FPDF
from PyPDF2 import PdfFileMerger, PdfFileReader
import re
import numpy as np
from cv2 import aruco
from readTextAndSymbols import textAndSymbols
from readSymbols import getSymbolName
import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages

# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful when multiple browsers/tabs
# are viewing the stream)
outputFrame = None
t = None
lock = threading.Lock()
imageNum = 0
minNum = 0
maxNum = 0
tempNum = 0
symbolNum = 0
cardNum = 0
brailleNums = 0
gameSpaceNum = 1
cardNums = 30
videoDone = False
cardGame = 'Dominion'
theCardInfoFile = ''
sessionName = 'AddFunction'
templateName = 'ActionType'

init_db()

# initialize the video stream and allow the camera sensor to warmup
vs = VideoStream(src=0).start()


@app.after_request
def set_response_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.route("/", methods=['GET', 'POST'])
def index():
    global videoDone, cardGame
    videoDone = True
    if request.method == 'POST':
        cardGame = request.form.get("cardInput", cardGame)
        return redirect(url_for('theBoard', cardName=cardGame))
    else:
        return render_template("index.html")


@app.route('/results')
def search_results(search):
    results = []
    search_string = search.data['search']

    if search.data['search'] == '':
        qry = db_session.query(cardGame)
        results = qry.all()

    if not results:
        flash('No results found!')
        return redirect('/')
    else:
        # display results
        return render_template('results.html', results=results)


@app.route("/theBoard", methods=['GET', 'POST'])
def theBoard():
    global videoDone, cardGame
    videoDone = True
    if request.method == "POST":
        if request.files:
            image = request.files["image"]
            image.save(os.path.join(app.config["BOARD_UPLOADS"], 'theBoard.png'))
            img = cv2.imread('static/uploads/board/theBoard.png')
            resized = cv2.resize(img, (775, 775), interpolation=cv2.INTER_AREA)
            cv2.imwrite('static/uploads/board/theBoard.png', resized)
            cv2.imwrite('static/uploads/board/theBoardCopy.png', resized)
            cv2.imwrite('static/uploads/board/theBoardDeleteCopy.png', resized)
            print("Board Image saved")

            return render_template("boardAnnotation.html", cardGame=cardGame)
    else:
        return render_template("theBoard.html", cardGame=cardGame)


@app.route("/boardAnnotation", methods=['GET', 'POST'])
def boardAnnotation():
    if request.method == "POST":
        if request.files:
            image = request.files["board"]
            image.save(os.path.join(app.config["FINAL_UPLOADS"], 'finalBoard.png'))
            print('Board Annotation saved')
            generateBoardPDF()
            return redirect(url_for('gcLabeler'))
    else:
        return render_template("boardAnnotation.html")


@app.route("/tester", methods=['GET', 'POST'])
def tester():
    return render_template("tester.html")


@app.route("/gcLabeler", methods=['GET', 'POST'])
def gcLabeler():
    global gameSpaceNum
    if request.method == 'POST':
        gameSpaceName = ''
        gameSpaceTLCoors = '0'
        gameSpaceBRCoors = '0'

        gameSpaceName = request.form.get('gameSpaceName', gameSpaceName)
        gameSpaceTLCoors = request.form.get('gameSpaceTLCoors', gameSpaceTLCoors)
        gameSpaceBRCoors = request.form.get('gameSpaceBRCoors', gameSpaceBRCoors)
        if gameSpaceName is '':
            gameSpaceName = str(gameSpaceNum)
            gameSpaceNum = gameSpaceNum + 1

        gameSpaceFile = open("static/gameSpaces.txt", "a+")
        gameSpaceFile.write(gameSpaceName + ',' + gameSpaceTLCoors + ',' + gameSpaceBRCoors + '\n')
        boardImage = cv2.imread('static/uploads/board/theBoardCopy.png')
        if boardImage is not None:
            gameSpaceTLCoors = gameSpaceTLCoors.split(',')
            gameSpaceBRCoors = gameSpaceBRCoors.split(',')
            cv2.circle(boardImage, (int(gameSpaceTLCoors[0]), int(gameSpaceTLCoors[1])), 4, (0, 0, 255), -1)
            cv2.circle(boardImage, (int(gameSpaceBRCoors[0]), int(gameSpaceBRCoors[1])), 4, (0, 0, 255), -1)
            cv2.imwrite('static/uploads/board/theBoardCopy.png', boardImage)

        # drawPointsonImage()
        return render_template("gcLabeler.html", cardGame=cardGame)
    else:
        return render_template("gcLabeler.html", cardGame=cardGame)


@app.route("/boardPreview", methods=['GET', 'POST'])
def boardPreview():
    return render_template("boardPreview.html")


@app.route("/cardPreview", methods=['GET', 'POST'])
def cardPreview():
    return render_template("cardPreview.html")


@app.route("/accessKit", methods=['GET', 'POST'])
def accessKit():
    return render_template("accessKit.html", cardGame=cardGame)


@app.route("/gcFiles", methods=['GET', 'POST'])
def gcFiles():
    return render_template("gcFiles.html", cardGame=cardGame)


@app.route("/scanBoard", methods=['GET', 'POST'])
def scanBoard():
    global videoDone
    videoDone = False
    t = threading.Thread(target=getContoursBlind)
    t.daemon = True
    t.start()
    return render_template("scanBoard.html", cardGame=cardGame)


@app.route("/scanSymbols", methods=['GET', 'POST'])
def scanSymbols():
    global videoDone
    videoDone = False
    t = threading.Thread(target=getContoursBlind)
    t.daemon = True
    t.start()
    return render_template("scanSymbols.html", cardGame=cardGame)


@app.route("/pieces", methods=['GET', 'POST'])
def gamePieces():
    global cardGame, minNum, maxNum, cardNums
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
        theMinNum = request.form.get("minDice", theMinNum)
        theMaxNum = request.form.get("maxDice", theMaxNum)

        minNum = theMinNum
        maxNum = theMaxNum

        distinguishable = request.form['yesOrNo']
        '''
        if distinguishable == 'yes':
            aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_250)
            fileTitle = cardGame + ' Additional Piece Markers'

            fig = plt.figure()
            plt.suptitle(fileTitle, fontsize=16, fontweight='bold')

            nx = int(int(extraPieces) / 2)
            ny = int(int(extraPieces) / 2)

            for i in range(1, int(extraPieces) + 1):
                ax = fig.add_subplot(ny, nx, i)
                img = aruco.drawMarker(aruco_dict, i, 700)
                plt.title(i, size=5, pad=2.75)
                plt.imshow(img, cmap=mpl.cm.gray, interpolation="nearest")
                ax.axis("off")

            plt.savefig("static/gamePieceMarkers.pdf")
        else:
        '''
        # needs labels for everything
        outputPDF = PdfPages('static/gamePieceMarkers.pdf')
        aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_250)
        fileTitle = cardGame + ' Game Piece Markers'
        newID = 0
        fig = plt.figure()
        plt.suptitle(fileTitle, fontsize=16, fontweight='bold')

        nx = int(playerPieces)
        ny = int(maxPieces)
        k = 1
        for i in range(1, int(maxPieces) + 1):
            for j in range(1, int(playerPieces) + 1):
                ax = fig.add_subplot(10, 10, k)
                img = aruco.drawMarker(aruco_dict, i, 700)
                plt.title(i, size=5, pad=5)
                plt.imshow(img, cmap=mpl.cm.gray, interpolation="nearest")
                ax.axis("off")
                k = k + 1
        plt.subplots_adjust(hspace=1.5, wspace=0.4)
        outputPDF.savefig()
        if int(extraPieces) > 0:
            fileTitle = cardGame + ' Additional Piece Markers'

            fig = plt.figure()
            plt.suptitle(fileTitle, fontsize=16, fontweight='bold')

            if int(extraPieces) % 2 == 0:
                nx = int(int(extraPieces) / 2)
                ny = int(int(extraPieces) / 2)
            else:
                nx = int(int(extraPieces) / 2) + 1
                ny = int(int(extraPieces) / 2) + 1
            newID = int(maxPieces) + 1
            for i in range(1, int(extraPieces) + 1):
                ax = fig.add_subplot(10, 10, i)
                img = aruco.drawMarker(aruco_dict, newID, 700)
                plt.title(newID, size=5, pad=5)
                plt.imshow(img, cmap=mpl.cm.gray, interpolation="nearest")
                ax.axis("off")
                newID = newID + 1
            plt.subplots_adjust(hspace=1.5, wspace=0.4)
            outputPDF.savefig()
        outputPDF.close()
        if k > newID:
            cardNums = k + 1
        else:
            cardNums = newID + 1
        return redirect(url_for('piecePreview'))
    else:
        return render_template("gamePieces.html", cardGame=cardGame)


@app.route("/labelBoard", methods=['GET', 'POST'])
def labelBoard():
    return render_template("labelBoard.html")


@app.route("/piecePreview", methods=['GET', 'POST'])
def piecePreview():
    return render_template("piecePreview.html")


@app.route("/theCards", methods=['GET', 'POST'])
def theCards():
    if request.method == 'POST':

        return redirect(url_for('createTemplate', cardGame=cardGame))
    else:
        return render_template("theCards.html", cardGame=cardGame)


@app.route("/differentTemplates", methods=['GET', 'POST'])
def differentTemplates():
    return render_template("differentTemplates.html", cardGame=cardGame)


@app.route("/remainingCards", methods=['GET', 'POST'])
def remainingCards():
    return render_template("remainingCards.html")


@app.route("/symbolUpload", methods=['GET', 'POST'])
def symbolUpload():
    global symbolNum
    if request.method == "POST":
        if request.files:
            fileName = str(symbolNum) + '.png'
            image = request.files["symbols"]
            image.save(os.path.join(app.config["SYMBOL_UPLOADS"], fileName))

            print("Image saved")
            symbolNum = symbolNum + 1
            return render_template("symbolUpload.html", cardGame=cardGame)
    else:
        return render_template("symbolUpload.html", cardGame=cardGame)


@app.route("/cardUpload", methods=['GET', 'POST'])
def cardUpload():
    global cardNum
    if request.method == "POST":
        if request.files:
            fileName = str(cardNum) + '.png'
            image = request.files["cards"]
            cardUploadFile = open("static/cardUploads.txt", "a+")
            cardUploadFile.write(image.filename + '\n')
            image.save(os.path.join(app.config["CARD_UPLOADS"], fileName))
            cardFile = 'static/newCards/' + fileName
            img = cv2.imread(cardFile)
            resized = cv2.resize(img, (400, 400), interpolation=cv2.INTER_AREA)
            cv2.imwrite(cardFile, resized)
            print("Image saved")
            cardNum = cardNum + 1
            return render_template("cardUpload.html", cardGame=cardGame)
    else:
        return render_template("cardUpload.html", cardGame=cardGame)


@app.route("/remainingSymbols", methods=['GET', 'POST'])
def remainingSymbols():
    return render_template("remainingSymbols.html", cardGame=cardGame)


@app.route("/symbolDirections", methods=['GET', 'POST'])
def symbolDirections():
    return render_template("symbolDirections.html")


@app.route("/cardParts", methods=['GET', 'POST'])
def cardParts():
    return render_template("cardParts.html", cardGame=cardGame)


@app.route("/newTemplate", methods=['GET', 'POST'])
def newTemplate():
    global videoDone, templateName
    videoDone = True
    cardFileName = ''
    newCardName = ''
    cardFile = ''
    templateNames = []
    regionList = []
    for filename in os.listdir('static/newCards/'):
        templateNames.append(filename)
    if request.method == 'POST':
        text = False
        symbols = False
        color = False
        regionName = ''
        regionCoors = '0'
        templateName = ''
        cardName = ''

        cardName = request.form.get('cardName', cardName)
        templateName = request.form.get('templateName', templateName)
        regionName = request.form.get('theName', regionName)
        text = request.form.get("lookingForText", text)
        symbols = request.form.get("lookingForSymbols", symbols)
        color = request.form.get("lookingForColor", color)
        regionCoors = request.form.get("regionCoors", regionCoors)

        templateName = re.sub(' ', '', templateName)

        cardFileName = 'static/newCards/' + cardName
        newCardName = 'static/cardTemplates/' + templateName + '.png'
        cardFile = cv2.imread(cardFileName)
        cv2.imwrite(newCardName, cardFile)

        if text == 'yesText':
            regionName = regionName + 'Text'
        if symbols == 'yesSymbols':
            regionName = regionName + 'Symbols'
        if color == 'yesColor':
            regionName = regionName + 'Color'

        regionFile = open("static/regions.txt", "a+")
        newtemplateName = templateName + '.png'
        regionFile.write(newtemplateName + ' ' + regionName + ':' + regionCoors + '\n')

        return render_template("newTemplate.html", templateName=templateName, cardGame=cardGame,
                               templateNames=templateNames, templateLen=len(templateNames))
    else:
        return render_template("newTemplate.html", cardGame=cardGame, templateNames=templateNames,
                               templateLen=len(templateNames))


@app.route("/newSymbol", methods=['GET', 'POST'])
def newSymbol():
    global videoDone, templateName
    videoDone = True
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

        symbolImage = cv2.imread('static/newCards/' + cardName)
        symbolCoors = re.sub('\(', '', symbolCoors)
        symbolCoors = re.sub('\)', '', symbolCoors)
        symbolCoors = re.sub(',', ' ', symbolCoors)
        symbolCoors = symbolCoors.split(' ')
        x, y, w, h = symbolCoors

        croppedImage = symbolImage[int(y):int(h), int(x):int(w)]
        fileName = 'static/cardSymbols/' + symbolName + '.jpg'
        cv2.imwrite(fileName, croppedImage)
        return redirect(url_for('newSymbol', templateName=templateName))
    else:
        return render_template("newSymbol.html", cardGame=cardGame, templateNames=templateNames,
                               templateLen=len(templateNames))


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
    print(x, y, w, h)
    croppedImage = symbolImage[int(y):int(h), int(x):int(w)]
    cv2.imwrite('static/symbolPreview.jpg', croppedImage)
    return "Done"


@app.route("/createTemplate", methods=['GET', 'POST'])
def createTemplate():
    global videoDone, tempNum
    videoDone = False

    t = threading.Thread(target=getContours)
    t.daemon = True
    t.start()
    if request.method == 'POST':
        currImage = cv2.imread('static/perfectExample.jpg')

        fileName = 'static/cardTemplates/' + str(tempNum) + '.jpg'
        status = cv2.imwrite(fileName, currImage)
        if status:
            system('say -v Samantha Success')
        else:
            system('say -v Samantha Picture not taken')
        tempNum = tempNum + 1
        return redirect(url_for('createTemplate'))
    else:
        return render_template("createTemplate.html")


@app.route("/cardInfo")
def cardInfo():
    global videoDone
    videoDone = False
    t = threading.Thread(target=getContoursBlind)
    t.daemon = True
    t.start()
    return render_template("cardInfo.html")


@app.route("/editTemplates", methods=['GET', 'POST'])
def editTemplate():
    global videoDone
    videoDone = True
    if request.method == 'POST':
        templateName = ' '
        deleteOrEdit = '0'

        deleteOrEdit = request.form.get("deleteEdit", deleteOrEdit)
        templateName = request.form.get("templateName", templateName)

        if deleteOrEdit == 'delete':
            with open("static/regions.txt", "r") as f:
                lines = f.readlines()

            with open("static/regions.txt", "w") as f:
                for line in lines:
                    if not line.startswith(templateName):
                        f.write(line)

            return redirect(url_for('editTemplate'))
        if deleteOrEdit == 'edit':
            filename = 'static/cardTemplates/' + templateName
            image = cv2.imread(filename)
            drawRegions(image, templateName)
            return redirect(url_for('reviseTemplates', templateName=templateName))
    else:
        templateNames = []
        f = open("static/regions.txt", "r")
        f1 = f.readlines()
        for x in f1:
            line = re.split('\s', x)
            templateNames.append(line[0])
        return render_template("editTemplates.html", len=len(templateNames), templateNames=templateNames)


@app.route("/reviseTemplates", methods=['GET', 'POST'])
def reviseTemplates():
    global videoDone
    videoDone = True
    templateName = request.args.get('templateName')
    regionNames = getCheckList(templateName)

    if request.method == 'POST':
        regionCoors = request.form.getlist('regionCoors')
        for regionDelete in regionCoors:
            f = open("static/regions.txt", "r+")
            fileText = f.read()
            fileText = fileText.replace(regionDelete, "")
            f.close()

            f = open("static/regions.txt", "w+")
            f.write(fileText)
            f.close()
        regionNames = getCheckList(templateName)
        return render_template('reviseTemplates.html', len=len(regionNames), regionNames=regionNames, templateName=templateName)
    else:
        return render_template('reviseTemplates.html', len=len(regionNames), regionNames=regionNames, templateName=templateName)


@app.route("/scanCards")
def scanCards():
    global videoDone
    videoDone = False
    t = threading.Thread(target=getContoursBlind)
    t.daemon = True
    t.start()
    return render_template("scanCards.html", cardGame=cardGame, sessionName=sessionName)


@app.route("/labelRegions", methods=['GET', 'POST'])
def labelRegions():
    global videoDone
    videoDone = True

    if request.method == 'POST':
        text = False
        symbols = False
        color = False
        regionName = ''
        symbolName = ''
        regionCoors = '0'
        symbolCoors = '0'
        templateName = ''

        templateName = request.form.get('templateName', templateName)
        regionName = request.form.get('theName', regionName)
        text = request.form.get("lookingForText", text)
        symbols = request.form.get("lookingForSymbols", symbols)
        color = request.form.get("lookingForColor", color)
        regionCoors = request.form.get("regionCoors", regionCoors)

        templateName = request.form.get('symbolTemplateName', templateName)
        symbolName = request.form.get('theSymbolName', symbolName)
        symbolCoors = request.form.get("symbolCoors", symbolCoors)

        if regionName is not '':

            if text == 'yesText':
                regionName = regionName + 'Text'
            if symbols == 'yesSymbols':
                regionName = regionName + 'Symbols'
            if color == 'yesColor':
                regionName = regionName + 'Color'

            regionFile = open("static/regions.txt", "a+")
            regionFile.write(templateName + ' ' + regionName + ':' + regionCoors + '\n')

        if symbolName is not '':
            symbolImage = cv2.imread('static/cardTemplates/' + templateName)
            symbolCoors = re.sub('\(', '', symbolCoors)
            symbolCoors = re.sub('\)', '', symbolCoors)
            symbolCoors = re.sub(',', ' ', symbolCoors)
            symbolCoors = symbolCoors.split(' ')
            x, y, w, h = symbolCoors

            croppedImage = symbolImage[int(y):int(h), int(x):int(w)]
            fileName = 'static/cardSymbols/' + symbolName + '.jpg'
            cv2.imwrite(fileName, croppedImage)

        return redirect(url_for('labelRegions'))
    else:
        templateNames = []
        for filename in os.listdir('static/cardTemplates/'):
            templateNames.append(filename)
        return render_template("labelRegions.html", len=len(templateNames), templateNames=templateNames)


@app.route("/printLabel", methods=['GET', 'POST'])
def printLabel():
    '''
    templateNames = []
    for filename in os.listdir('static/newCards/'):
        templateNames.append(filename)
    if request.method == 'POST':
        template = ' '
        template = request.form.get('templateNames', template)
        print(template)
        regionNames = []

        template = 'action.jpg'
        # need to get the template match
        regionNames = []
        f = open("static/regions.txt", "r")
        f1 = f.readlines()
        for x in f1:
            line = re.split('\s', x)
            if line[0] == template:
                for name in line[1:]:
                    name = re.sub(':', ' ', name)
                    labelName = re.split('\s', name)
                    regionNames.append(labelName[0])
                    regionNames = list(filter(lambda a: a != '', regionNames))

        return redirect(url_for('printLabel', templateNames=templateNames, templateLen=len(templateNames),
                                len=len(regionNames), regionNames=regionNames))
    '''
    cardText = ''
    global videoDone, theCardInfoFile
    videoDone = True
    templateNames = []
    for filename in os.listdir('static/newCards/'):
        templateNames.append(filename)
    if request.method == 'POST':
        system('say -v Samantha Reading text from card')
        template = ' '
        template = request.form.get('templateNames', template)
        cardFile = 'static/newCards/' + template
        theCardInfoFile = cardFile
        cardText = readCardText(cardFile)
        # cardText = pytesseract.image_to_string(Image.open(cardFile))
        if len(cardText) == 0:
            cardText = 'ERROR: Type in text from card. Unable to read'

        return render_template("printLabel.html", templateNames=templateNames, templateLen=len(templateNames),
                               img=cardFile, text=cardText, cardGame=cardGame)
    else:
        return render_template("printLabel.html", templateNames=templateNames, templateLen=len(templateNames),
                               img="static/orange.png", text="", cardGame=cardGame)


@app.route("/videoFeed")
def videoFeed():
    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/getImage")
def getImage():
    global currImage
    currImage = cv2.imread('static/perfectExample.jpg')
    return "perfectExample.jpg"


@app.route("/symbolImage")
def symbolImage():
    return "symbolPreview.jpg"


@app.route("/discardImage")
def discardImage():
    global currImage, imageNum
    imageNum = imageNum - 1
    currImage = cv2.imread('static/perfectExample.jpg')
    return "perfectExample.jpg"


@app.route("/saveImage")
def saveImage():
    global imageNum
    currImage = cv2.imread('static/perfectExample.jpg')
    fileName = 'static/newCards/' + str(imageNum) + '.jpg'
    cv2.imwrite(fileName, currImage)
    imageNum = imageNum + 1
    system('say -v Samantha Next card')
    return "Image saved"


@app.route("/saveBoardImage")
def saveBoardImage():
    global imageNum
    currImage = cv2.imread('static/perfectExample.jpg')
    fileName = 'static/uploads/theBoard.png'
    cv2.imwrite(fileName, currImage)
    return "Board saved"


@app.route("/getColor")
def getColor():
    color = getDominantColor("static/perfectExample.jpg")
    system('say -v Samantha ' + color)

    return "Complete"


@app.route("/getType")
def getType():
    category = matchTemplate("static/perfectExample.jpg")
    category = re.sub('.jpg', '', category)
    system('say -v Samantha ' + category)

    return "Complete"


@app.route("/getTemplates")
def getTemplates():
    templateNames = []
    f = open("static/regions.txt", "r")
    f1 = f.readlines()
    for x in f1:
        line = re.split('\s', x)
        templateNames.append(line[0])
    for x in templateNames:
        return x


@app.route("/saveLabel", methods=['POST'])
def saveLabel():
    global cardNums, theCardInfoFile
    cardText = request.get_json()
    theCardText = str(cardText)
    theCardText = re.sub('\n', ' ', theCardText)
    theCardFile = open("static/cardInfo.txt", "a+")
    theCardFile.write(str(cardNums) + ',' + str(theCardInfoFile) + ',' + str(theCardText) + '\n')
    # theCardFile.write(str(cardNums) + '  ' + str(theCardText) + '\n')
    cardNums = cardNums + 1
    labelNum = getLabelNums()
    system('say -v Samantha Label saved. Next')
    return str(labelNum)


@app.route("/saveBraille", methods=['POST'])
def saveBraille():
    global brailleNums, theCardInfoFile
    brailleText = request.get_json()
    theBrailleFile = open("static/brailleInfo.txt", "a+")
    # theCardFile.write(str(brailleNums) + ' ' + str(theCardInfoFile) + ' ' + str(cardText) + '\n')
    theBrailleFile.write(str(brailleNums) + '  ' + str(brailleText) + '\n')
    brailleNums = brailleNums + 1
    return "Done"


@app.route("/saveBImage", methods=['POST'])
def saveBImage():
    print('here')
    if request.method == 'POST':
        print('post Here')
        file = request.files['image']
        print(file)
        '''
        if file and allowed_file(file.filename):
            n = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], n))

        '''


@app.route("/getText")
def getText():
    theText = pytesseract.image_to_string(Image.open('static/perfectExample.jpg'))
    theText = re.sub('\n', ' ', theText)
    theText = re.sub('[^A-Za-z0-9\s]+', '', theText)
    print(theText)
    system('say -v Samantha ' + theText)
    '''
    templateName = matchTemplate("static/perfectExample.jpg")
    theImage = cv2.imread("static/perfectExample.jpg")
    allRegionCoors = {}
    f = open("static/regions.txt", "r")
    f1 = f.readlines()
    num = 0
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
                allRegionCoors[num] = regionCoors
                num = num + 1

    for regionName, regionCoors in allRegionCoors.items():
        x, y, w, h = regionCoors
        croppedImage = theImage[int(y):int(h), int(x):int(w)]
        cv2.imwrite('extractedRegion.jpg', croppedImage)
        theText = pytesseract.image_to_string(Image.open('extractedRegion.jpg'))
        system('say -v Samantha ' + theText)
    '''
    return "Complete"


@app.route("/removeLastRegion", methods=['POST', 'GET'])
def removeLastRegion():
    with open('static/regions.txt') as f1:
        lines = f1.readlines()

    with open('static/regions.txt', 'w') as f2:
        f2.writelines(lines[:-1])

    return "finished"


@app.route("/removeLastGameSpace", methods=['POST', 'GET'])
def removeLastGameSpace():
    with open('static/gameSpaces.txt') as f1:
        lines = f1.readlines()

    with open('static/gameSpaces.txt', 'w') as f2:
        f2.writelines(lines[:-1])

    gameSpaceFile = open("static/gameSpaces.txt", "r")
    boardImage = cv2.imread('static/uploads/board/theBoardDeleteCopy.png')
    for x in gameSpaceFile:
        x = x.split(',')
        tlX = int(x[1])
        tlY = int(x[2])
        brX = int(x[3])
        brY = int(x[4])
        cv2.circle(boardImage, (tlX, tlY), 4, (0, 0, 255), -1)
        cv2.circle(boardImage, (brX, brY), 4, (0, 0, 255), -1)
    cv2.imwrite('static/uploads/board/theBoardCopy.png', boardImage)
    return "finished"


def readCardText(cardFile):
    finalText = ''
    templateName = matchTemplate(cardFile)
    theImage = cv2.imread(cardFile)
    allRegionCoors = {}
    f = open("static/regions.txt", "r")
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

    allRegionCoors = OrderedDict(sorted(allRegionCoors.items(), key=lambda k: [k[1], k[0]]))

    for regionName, regionCoors in allRegionCoors.items():
        x, y, w, h, _ = regionCoors

        croppedImage = theImage[int(y):int(h), int(x):int(w)]
        cv2.imwrite('extractedRegion.jpg', croppedImage)
        if 'Symbols' in regionCoors[4] and 'Text' in regionCoors[4]:
            text = textAndSymbols('extractedRegion.jpg')
            finalText = finalText + ' ' + text
            continue
        if 'Color' in regionCoors[4]:
            text = getDominantColor('extractedRegion.jpg')
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
        '''
        theText = pytesseract.image_to_string(Image.open('extractedRegion.jpg'))
        finalText = theText + finalText
        '''

    return finalText


def generateBoardPDF():

    global cardGame
    # save FPDF() class into
    # a variable pdf
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=40)
    pdf.cell(200, 50, txt='Accessibility Kit for', ln=50, align='C')
    pdf.cell(200, 55, txt=cardGame, ln=55, align='C')

    # Add a page
    pdf.add_page()

    # set style and size of font
    # that you want in the pdf
    pdf.set_font("Arial", size=15)

    pdf.image('static/finalBoard.png', x=None, y=None, w=200, h=200)
    pdf.cell(200, 10, txt='Suggested Materials for Tactile Markers', ln=1, align='C')
    pdf.cell(200, 11, txt='Pipe Cleaners', ln=1, align='C')
    pdf.cell(200, 11, txt='Rhinestones', ln=1, align='C')
    pdf.cell(200, 11, txt='Wooden Shapes', ln=1, align='C')
    pdf.cell(200, 11, txt='Puffy Paint', ln=1, align='C')
    pdf.cell(200, 11, txt='Bump Dots', ln=1, align='C')

    pdf.add_page()
    pdf.set_font("Arial", size=30)
    pdf.cell(200, 5, txt='Braille Labels for Board', ln=1, align='C')
    pdf.set_font("Arial", size=15)
    # open the text file in read mode
    f = open("static/brailleInfo.txt", "r")

    # insert the texts in pdf
    for x in f:
        y = x.split(' ')
        x = x.replace(y[1], '')
        # pdf.image(y[1], x=None, y=None, w=20, h=20)
        pdf.multi_cell(200, 10, txt=x, align='C')

    # save the pdf with name .pdf
    pdf.output("static/theBoard.pdf")


@app.route("/generateCardPDF")
def generateCardPDF():
    # save FPDF() class into
    # a variable pdf
    pdf = FPDF()

    # Add a page
    pdf.add_page()
    pdf.set_font("Arial", size=30)
    pdf.cell(200, 5, txt='Braille Labels for Cards', ln=1, align='C')
    # set style and size of font
    # that you want in the pdf
    pdf.set_font("Arial", size=15)

    # open the text file in read mode
    f = open("static/cardInfo.txt", "r")

    # insert the texts in pdf
    for x in f:
        y = x.split(',')
        x = x.replace(y[1], '')
        x = x.replace(',', ' ')
        pdf.image(y[1], x=None, y=None, w=20, h=20)
        pdf.multi_cell(200, 10, txt=x, align='C')

    # save the pdf with name .pdf
    pdf.output("static/theCards.pdf")
    generateAccessKitPDF()
    return "generated"


def getFilePaths(directory):
    # initializing empty file paths list
    file_paths = []

    # crawling through directory and subdirectories
    for root, directories, files in os.walk(directory):
        for filename in files:
            # join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)

            # returning all file paths
    return file_paths


def generateGCZip():
    '''
    # path to folder which needs to be zipped
    directory = 'static/GameChangerFiles'

    # calling function to get all file paths in the directory
    file_paths = getFilePaths(directory)

    # printing the list of all files to be zipped
    for file_name in file_paths:
        print(file_name)

    # writing files to a zipfile
    with ZipFile('static/gameChangerFiles.zip', 'w') as zip:
        # writing each file one by one
        for file in file_paths:
            zip.write(file)
    '''
    base_path = pathlib.Path('./static/GameChangerFiles')
    data = io.BytesIO()
    with ZipFile(data, mode='w') as z:
        for f_name in base_path.iterdir():
            z.write(f_name)
    data.seek(0)
    return send_file(
        data,
        mimetype='application/zip',
        as_attachment=True,
        attachment_filename='static/gameChangerFiles.zip'
    )


def generateGCFiles():
    global minNum, maxNum
    # get game space info
    oldGameSpaceFile = open('static/gameSpaces.txt', 'r')
    newGameSpaceFile = open('static/GameChangerFiles/gcGameSpaces.txt', 'w')
    oldLines = oldGameSpaceFile.readlines()
    newGameSpaceFile.write('minNum,' + str(minNum) + ',maxNum' + str(maxNum) + '\n')
    newGameSpaceFile.write('Game Space Number,startX,endX,startY,endY\n')
    for line in oldLines:
        newGameSpaceFile.write(line)
    # get card info
    f = open("static/cardInfo.txt", "r")
    gcCardFile = open('static/GameChangerFiles/gcCardInfo.txt', 'w')
    gcCardFile.write('Tag Number, Description\n')
    f1 = f.readlines()

    for x in f1:
        line = re.split(',', x)
        gcCardFile.write(line[0] + ',' + line[2])
    print('generating Game Changer zip file')
    generateGCZip()


@app.route("/generateAccessKitPDF", methods=['POST', 'GET'])
def generateAccessKitPDF():
    global cardGame
    print('generating accessibility kit')
    merger = PdfFileMerger()
    board = 'static/theBoard.pdf'
    cards = 'static/theCards.pdf'
    pieces = 'static/gamePieceMarkers.pdf'
    if path.exists(board):
        merger.append(PdfFileReader(board))
    if path.exists(cards):
        merger.append(PdfFileReader(cards))
    if path.exists(pieces):
        merger.append(PdfFileReader(pieces))
    filename = 'static/accessibilityKit.pdf'
    merger.write(filename)
    generateGCFiles()
    # open('static/brailleInfo.txt', 'w').close()
    # open('static/cardInfo.txt', 'w').close()
    # open('static/cardUpload.txt', 'w').close()
    # open('static/gameSpaces.txt', 'w').close()
    return "fin"


def getRegions():
    regionList = []
    f = open("static/regions.txt", "r")
    for x in f:
        if templateName in x:
            line = x.split()
            line = line[1].split(':')
            regionList.append(line[0])
    return regionList


def getContours():
    # grab global references to the video stream, output frame, and lock variables
    global vs, outputFrame, lock, currImage, videoDone

    template = creatingTemplates()

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
            # cv2.rectangle(thresh, (minX, minY), (maxX, maxY), (0, 0, 255), 2)
        template.getPerfectImage(frame)
        time.sleep(1.5)

        # acquire the lock, set the output frame, and release the lock
        with lock:
            outputFrame = frame.copy()


def getLabelNums():
    numLines = 0
    file = open("static/cardInfo.txt", "r")
    for line in file:
        line = line.strip("\n")
        numLines += 1

    return numLines


def getContoursBlind():
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


def drawPointsonImage():
    gameSpaceFile = open("static/gameSpaces.txt", "r")
    boardImage = cv2.imread('static/uploads/board/theBoardCopy.png')
    for x in gameSpaceFile:
        x = x.split(',')
        tlX = int(x[1])
        tlY = int(x[2])
        brX = int(x[3])
        brY = int(x[4])
        cv2.circle(boardImage, (tlX, tlY), 4, (0, 0, 255), -1)
        cv2.circle(boardImage, (brX, brY), 4, (0, 0, 255), -1)
    cv2.imwrite('static/uploads/board/theBoardCopy.png', boardImage)


def getCheckList(templateName):
    regionNames = []
    f = open("static/regions.txt", "r")
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
    f = open("static/regions.txt", "r")
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
        cv2.imwrite('static/editImage.jpg', image)


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


if __name__ == '__main__':
    # start the flask app
    app.run(host='0.0.0.0', port=8000)

# release the video stream pointer
vs.stop()
