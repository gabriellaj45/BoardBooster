# https://www.pyimagesearch.com/2019/09/02/opencv-stream-video-to-web-browser-html-page/
from creatingTemplates import creatingTemplates
from imutils.video import VideoStream
from flask import Response
from flask import Flask
from flask import render_template
import threading
import imutils
import time
import cv2
import os

# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful when multiple browsers/tabs
# are viewing the stream)
outputFrame = None
lock = threading.Lock()
currImage = None

# initialize a flask object
app = Flask(__name__)

# initialize the video stream and allow the camera sensor to warmup
vs = VideoStream(src=0).start()
time.sleep(2.0)


@app.after_request
def set_response_headers(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.route("/")
def index():
    return render_template("labelRegions.html")


def getContours():
    # grab global references to the video stream, output frame, and lock variables
    global vs, outputFrame, lock, currImage

    template = creatingTemplates()

    # loop over frames from the video stream
    while True:
        # read the next frame from the video stream, resize it
        frame = vs.read()
        frame = imutils.resize(frame, width=600)
        contour = template.showContours(frame)
        if contour is not None:
            (thresh, (minX, minY, maxX, maxY)) = contour
            cv2.rectangle(frame, (minX, minY), (maxX, maxY), (0, 0, 255), 2)
        template.getPerfectImage(frame, minX, minY, maxX, maxY)
        time.sleep(1.5)

        # acquire the lock, set the output frame, and release the lock
        with lock:
            outputFrame = frame.copy()


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


@app.route("/video_feed")
def video_feed():
    # return the response generated along with the specific media
    #  type (mime type)
    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/getImage")
def getImage():
    global currImage
    currImage = cv2.imread('static/tester.jpg')
    return "tester.jpg"


@app.route("/saveImage")
def saveImage():
    cv2.imwrite('theCurrImage.jpg', currImage)
    return "Image saved"


# check to see if this is the main thread of execution
if __name__ == '__main__':

    # start a thread that will perform motion detection
    t = threading.Thread(target=getContours)
    t.daemon = True
    t.start()

    # start the flask app
    app.run(host='0.0.0.0', port=8000, debug=True, threaded=True, use_reloader=False)

# release the video stream pointer
vs.stop()
