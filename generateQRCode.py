import qrcode


def makeQRCode(text, game, card):
    qrCode = qrcode.make(text)
    fileName = game + '/qrImages/' + card + '.png'
    qrCode.save(fileName)
