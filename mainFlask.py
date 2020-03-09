# https://www.pyimagesearch.com/2019/09/02/opencv-stream-video-to-web-browser-html-page/
# https://stackoverflow.com/questions/4710067/using-python-for-deleting-a-specific-line-in-a-file
from creatingTemplates import creatingTemplates
from scanningCards import scanningCards
from matchTemplate import *
from recognizeNewSymbols import *
from getColor import getDominantColor
from readCardText import *
from imutils.video import VideoStream
from flask import Response
from flask import Flask
from flask import render_template
from flask import request
from flask import redirect, url_for
from playsound import playsound
from collections import OrderedDict
import threading
import pytesseract
import imutils
import time
import cv2
import os

# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful when multiple browsers/tabs
# are viewing the stream)
outputFrame = None
t = None
lock = threading.Lock()
imageNum = 0
videoDone = False
cardGame = ''

# initialize a flask object
app = Flask(__name__)

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
        return redirect(url_for('stepTwo', cardName=cardGame))
    else:
        return render_template("index.html")


@app.route("/stepTwo", methods=['GET', 'POST'])
def stepTwo():
    global videoDone, cardGame
    videoDone = True

    return render_template("stepTwo.html", cardGame=cardGame)


@app.route("/newRegion", methods=['GET', 'POST'])
def newRegion():
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
    else:
        return render_template("newRegion.html")


@app.route("/newSymbol", methods=['GET', 'POST'])
def newSymbol():
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
    else:
        return render_template("newSymbol.html")


@app.route("/createTemplate", methods=['GET', 'POST'])
def createTemplate():
    global videoDone
    videoDone = False

    t = threading.Thread(target=getContours)
    t.daemon = True
    t.start()
    if request.method == 'POST':
        currImage = cv2.imread('static/perfectExample.jpg')
        templateName = ' '

        templateName = request.form.get("theTemplateName", templateName)
        fileName = 'static/cardTemplates/' + str(templateName) + '.jpg'
        status = cv2.imwrite(fileName, currImage)
        if status:
            system('say -v Samantha Success')
        else:
            system('say -v Samantha Picture not taken')
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
    return render_template("scanCards.html")


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
    global videoDone
    videoDone = True
    templateNames = []
    for filename in os.listdir('static/newCards/'):
        templateNames.append(filename)
    if request.method == 'POST':
        template = ' '
        template = request.form.get('templateNames', template)
        cardFile = 'static/newCards/' + template
        cardText = readCardText(cardFile)
        if len(cardText) == 0:
            cardText = 'ERROR: Type in text from card. Unable to read'
        return render_template("printLabel.html", templateNames=templateNames, templateLen=len(templateNames),
                               img=cardFile, text=cardText)
    else:
        return render_template("printLabel.html", templateNames=templateNames, templateLen=len(templateNames),
                               img="", text="")


@app.route("/videoFeed")
def videoFeed():
    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/getImage")
def getImage():
    global currImage
    currImage = cv2.imread('static/perfectExample.jpg')
    return "perfectExample.jpg"


@app.route("/saveImage")
def saveImage():
    global imageNum
    playsound('cameraClick.mp3')
    currImage = cv2.imread('static/perfectExample.jpg')
    fileName = 'static/newCards/' + str(imageNum) + '.jpg'
    cv2.imwrite(fileName, currImage)
    system('say -v Samantha Checking for new text')
    # scanningCards.checkNewRegions(fileName)
    system('say -v Samantha Checking for new symbols')
    # findNewSymbols(fileName, templateName)
    imageNum = imageNum + 1
    system('say -v Samantha Continue to next card')
    return "Image saved"


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
    cardText = request.get_json()
    print(cardText)
    # write this text to a word file or create a QR code
    return "Done"


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
                midpoint = (int(x) + int(w)) / 2, (int(y) + int(h)) / 2
                allRegionCoors[midpoint] = regionCoors

    allRegionCoors = OrderedDict(sorted(allRegionCoors.items(), key=lambda k: [k[1], k[0]]))

    for regionName, regionCoors in allRegionCoors.items():
        x, y, w, h = regionCoors
        croppedImage = theImage[int(y):int(h), int(x):int(w)]
        cv2.imwrite('extractedRegion.jpg', croppedImage)
        theText = pytesseract.image_to_string(Image.open('extractedRegion.jpg'))
        finalText = theText + finalText

    return finalText


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


def getContoursBlind():
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


# check to see if this is the main thread of execution
if __name__ == '__main__':
    # start the flask app
    app.run(host='0.0.0.0', port=8000)

# release the video stream pointer
vs.stop()
