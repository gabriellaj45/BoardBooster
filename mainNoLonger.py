from mainScreen import *

if __name__ == '__main__':
    '''
    templateMatch = 'White.jpg'
    game = 'Cards Against Humanity'
    readCardText(tk.Tk(), "Read Text", "Cards Against Humanity/cardTemplates/White.jpg", templateMatch, game)
    '''
    '''
    game = 'Cards Against Humanity'
    scanCards(tk.Tk(), "Scan Cards", game)
    #createTemplates(tk.Tk(), "Add New Templates", game)
    '''
    '''
    game = 'Cards Against Humanity'
    file = 'Cards Against Humanity/cardTemplates/Black.jpg'
    textAndSymbols(game, file)
    '''
    '''
    game = 'Cards Against Humanity'
    file = 'Cards Against Humanity/cardTemplates/Black.jpg'
    editTemplate(tk.Tk(), 'Edit Templates', game)
    '''

    '''
    game = 'Dominion'
    file = 'Dominion/cardTemplates/0.jpg'
    templateName = '0.jpg'
    findNewSymbols(game, file, templateName)
    '''
    '''
    game = 'Dominion'
    cardImage = 'dominionTest.png'
    addNewSymbol(game, cardImage)
    '''

    # print(checkForNewSymbols())
    ''''
    game = 'Cards Against Humanity'
    file = 'Cards Against Humanity/cardTemplates/Black.jpg'
    templateName = 'Black.jpg'
    findNewSymbols(game, file, templateName)
    '''

    '''
    game = 'Dominion'
    file = 'Dominion/cardTemplates/0.jpg'
    template = '0.jpg'
    checkNewText(file, game, template)
    '''

    '''
    game = 'Cards Against Humanity'
    file = 'Cards Against Humanity/cardTemplates/Black.jpg'
    template = 'Black.jpg'
    checkNewText(file, game, template)
    '''

    # getRegions('Cards Against Humanity')
    # getRegions()
    # extractText()
    # cleanUp()
    # createTemplates(tk.Tk(), "Add New Templates", 'Cards Against Humanity')
    '''
    cardFile = "Magic the Gathering/processSymbols/magic1.jpeg"
    game = 'Magic the Gathering'
    symbolDetection(tk.Tk(), "Find Symbols", cardFile, game)
    '''
    # findText('Dominion/cardTemplates/0.jpg')

    '''
    test = matchTemplate('processCards/White1.jpg')
    print(test.templateMatch)
    

    cardFile = 'Cards Against Humanity/cardTemplates/Black2.jpg'
    templateMatch = matchTemplate(cardFile, 'Cards Against Humanity')
    template = templateMatch.templateMatch
    print(template)
    printLabel(tk.Tk(), "Print Label", cardFile, template, 'Cards Against Humanity')
    '''
    '''
    game = 'Cards Against Humanity'
    templateMatch = 'Black.jpg'
    readCardText(tk.Tk(), "Read Text", "cardInformation.jpg", templateMatch, game)
    
    game = 'Cards Against Humanity'
    file = 'extractedRegion.jpg'
    textAndSymbols(game, 'extractedRegion.jpg')
    '''
    '''
    file = 'Magic the Gathering/processCards/0.jpg'
    textBoxes = findText(file)
    template = 'creature.jpg'
    game = 'Magic the Gathering'
    addNewRegion(game, template, file, textBoxes)
    '''
    '''
    while True:
        mainScreen(tk.Tk(), "Welcome to LabelGen!")
'''

    game = 'Magic the Gathering'
    textAndSymbols(game, 'theText.jpg')






