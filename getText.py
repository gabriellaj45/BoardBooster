import pytesseract
from PIL import Image


def readText(file):
    text = pytesseract.image_to_string(Image.open(file))
    return text
