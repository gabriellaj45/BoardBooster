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


def translateToBraille(text, game, file):
    s = ""
    brailleFile = open(game + "/brailleFromCards.txt", "a")
    brailleFile.write(file + '\n')
    if text:
        for n in text:
            if n in alphabet:
                s += alphabraille[alphabet.index(n)]
            elif n in nums:
                s += numbraille[nums.index(n)]
        brailleFile.write(s + ' ')
        return
