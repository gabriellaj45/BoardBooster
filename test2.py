from cv2 import aruco
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.backends.backend_pdf import PdfPages

cardGame = 'Dominion'
playerPieces = 4
maxPieces = 4
extraPieces = 25
outputPDF = PdfPages('static/gamePieceMarkers.pdf')
aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_250)
fileTitle = cardGame + ' Game Piece Markers'

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
