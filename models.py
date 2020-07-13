from app import db


class CardGame(db.Model):
    __tablename__ = "cardGames"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    def __init__(self, name):
        """"""
        self.name = name

    def __repr__(self):
        return "{}".format(self.name)


class CardInformation(db.Model):
    __tablename__ = "cardInfo"

    id = db.Column(db.Integer, primary_key=True)
    cardPart = db.Column(db.String)
    coordinates = db.Column(db.String)
    text = db.Column(db.String)
    symbols = db.Column(db.String)
    color = db.Column(db.String)
    templateFile = db.Column(db.String)

    cardID = db.Column(db.Integer, db.ForeignKey("cardGames.id"))
    cardGame = db.relationship("CardGame", backref=db.backref(
        "cardInfo", order_by=id), lazy=True)

    def __init__(self, cardPart, coordinates, text, symbols, color, templateFile):
        self.cardPart = cardPart
        self.coordinates = coordinates
        self.text = text
        self.symbols = symbols
        self.color = color
        self.templateFile = templateFile


