# -*- coding: utf-8 -*-
from __future__ import unicode_literals
'''
https://github.com/its-sarin/BrailleCodec/blob/master/braille_codec.py
'''


alphabraille = ['⠁', '⠃', '⠉', '⠙', '⠑', '⠋', '⠛', '⠓', '⠊', '⠚', '⠅', '⠇',
                '⠍', '⠝', '⠕', '⠏', '⠟', '⠗', '⠎', '⠞', '⠥', '⠧', '⠺', '⠭', '⠽', '⠵']
numbraille = ['⠼⠁', '⠼⠃', '⠼⠉', '⠼⠙', '⠼⠑', '⠼⠋', '⠼⠛', '⠼⠓', '⠼⠊', '⠼⠚']
alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
nums = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']


def translateToPiecesBraille(text):
    s = ""
    brailleFile = open("static/userData/brailleForPieces.txt", "a")
    if text:
        for n in text:
            if n in alphabet:
                s += alphabraille[alphabet.index(n)]
            elif n in nums:
                s += numbraille[nums.index(n)]
        brailleFile.write(text + ': ' + s + ' ' + '\n')
        return


def translateToDiceBraille(text):
    s = ""
    brailleFile = open("static/userData/brailleForDice.txt", "a")
    if text:
        for n in text:
            if n in alphabet:
                s += alphabraille[alphabet.index(n)]
            elif n in nums:
                s += numbraille[nums.index(n)]
        brailleFile.write(text + ': ' + s + ' ' + '\n')
        return


def translateToBoardBraille(text):
    s = ""
    brailleFile = open("static/userData/brailleForBoard.txt", "a")
    if text:
        for n in text:
            if n in alphabet:
                s += alphabraille[alphabet.index(n)]
            elif n in nums:
                s += numbraille[nums.index(n)]
        brailleFile.write(text + ': ' + s + ' ' + '\n')
        return


def brailleText(text):
    s = ""
    if text:
        for n in text:
            if n in alphabet:
                s += alphabraille[alphabet.index(n)]
            elif n in nums:
                s += numbraille[nums.index(n)]
    print(s)
