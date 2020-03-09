from fpdf import FPDF
import os
'''
https://pyfpdf.readthedocs.io/en/latest/Tutorial/index.html
'''


class PDF(FPDF):
    def __init__(self, game):
        FPDF.__init__(self)
        self.game = game

    def header(self):
        self.set_font('Times', 'B', 12)
        # Move to the right
        self.cell(80)
        # Title
        self.cell(30, 10, 'Participant\'s Braille and QR code Output', 0, 0, 'C')
        # Line break
        self.ln(20)


def genPDF(game):
    # Instantiation of inherited class
    pdf = PDF(game)
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font('Times', '', 12)
    index = 10
    yIndex = 20
    if not os.path.isdir(game + '/qrImages/'):
        os.mkdir(game + '/qrImages')
    for filename in os.listdir(game + '/qrImages/'):
        if index > 300:
            yIndex = yIndex + 50
        pdf.image(filename, x=index, y=yIndex, w=50, h=50)
        index = index + 50
    pdf.output('finalOutput.pdf', 'F')
