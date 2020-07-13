from wtforms import Form, StringField, SelectField


class CardForm(Form):
    cardGame = StringField('Card Game')
    cardPart = StringField('Part of the Card')
    coors = StringField('Coordinates')
    text = StringField('Text')
    symbol = StringField('Symbol')
    color = StringField('Color')
    templateFile = StringField('Template File')


class CardSearchForm(Form):
    choices = [('Region', 'Region'),
               ('Card Game', 'Card Game'),
               ('Coordinates', 'Coordinates')]
    select = SelectField('Search for cards:', choices=choices)
    search = StringField('')
