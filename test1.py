# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from fpdf import FPDF
import os
import re


cardGame = 'Dominion'
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
pdf.output("static/userData/theCardsTest.pdf")