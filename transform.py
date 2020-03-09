import cv2
import numpy as np
import imutils


def mouse_handler(event, x, y, flags, data):
    if event == cv2.EVENT_LBUTTONDOWN:
        cv2.circle(data['im'], (x, y), 1, (0, 0, 255), 2)
        cv2.imshow("Image", data['im'])
        if len(data['points']) < 4:
            data['points'].append([x, y])
            print(x, y)


def get_four_points(im):
    # Set up data to send to mouse handler
    data = {}
    data['im'] = im.copy()
    data['points'] = []

    # Set the callback function for any mouse event
    cv2.imshow("Image", im)
    cv2.setMouseCallback("Image", mouse_handler, data)
    cv2.waitKey(0)

    # Convert array to np.array
    points = np.vstack(data['points']).astype(float)

    return points


#def rotateBoard():
if __name__ == '__main__':

    # Read in the image.
    cap = cv2.VideoCapture(0)

    _, im_src = cap.read()

    # im_src = cv2.imread('Cards Against Humanity/cardTemplates/White.jpg')

    ratio = im_src.shape[0] / 800.0
    orig = im_src.copy()
    image = imutils.resize(im_src, height=800)

    height = image.shape[0]
    width = image.shape[1]
    # Destination image
    size = (800, 800)

    im_dst = np.zeros(size, np.uint8)

    pts_dst = np.array(
        [
            [0, 0],
            [size[0], 0],
            [size[0], size[1]],
            [0, size[1]]
        ], dtype=float
    )

    '''
        Click on the four corners of the book -- top left first and
        bottom left last -- and then hit ENTER
        '''

    # Show image and wait for 4 clicks.
    im_src = cv2.resize(im_src, (width, height))
    cv2.imshow("Image", im_src)
    pts_src = get_four_points(im_src)
    # print(pts_src)

    # Calculate the homography
    h, status = cv2.findHomography(pts_src, pts_dst)

    # Warp source image to destination
    im_dst = cv2.warpPerspective(im_src, h, size[0:2])

    # Show output
    cv2.imwrite("skewTest.jpg", im_dst)
    # return im_dst
