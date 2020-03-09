from labelCards import getRegions
import cv2


def drawRegions(labels):
    # draw all the ROI on the perfect cards and get user to confirm that it is the correct labels
    image = cv2.imread('perfectCard.jpg')
    for keys, values in labels.items():
        font = cv2.FONT_HERSHEY_SIMPLEX
        x = ((values[2] - values[0]) / 2) + values[0]
        y = ((values[3] - values[1]) / 2) + values[1]
        cv2.putText(image, keys, (int(x), int(y)), font, 1, (0, 0, 255), 1, cv2.LINE_AA)
        image = cv2.rectangle(image, (values[0], values[1]), (values[2], values[3]), (0, 255, 0), 2)
    cv2.imshow('Confirm Regions on Card', image)
    cv2.waitKey(40) & 0xFF

    if cv2.waitKey(0) & 0xFF == ord('y'):
        cv2.destroyAllWindows()
        print('Begin scanning the rest of the cards')
        return

    if cv2.waitKey(0) & 0xFF == ord('n'):
        getRegions()

