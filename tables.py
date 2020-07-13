from flask_table import Table, Col, LinkCol


class Results(Table):
    id = Col('Id', show=False)
    cardGame = Col('Card Game')
    cardPart = Col('Part of the Card')
    coordinates = Col('Coordinates')
    text = Col('Text')
    symbol = Col('Symbol')
    color = Col('Color')
    templateFile = Col('Template File')
    edit = LinkCol('Edit', 'edit', url_kwargs=dict(id='id'))
