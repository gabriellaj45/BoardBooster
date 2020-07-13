from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

engine = create_engine('sqlite:///cardGames.db', echo=True)
Base = declarative_base()


class CardGame(Base):
    __tablename__ = "cardGames"

    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __init__(self, name):
        """"""
        self.name = name

    def __repr__(self):
        return "<Card Game: {}>".format(self.name)


class CardInformation(Base):
    __tablename__ = "cardInfo"

    id = Column(Integer, primary_key=True)
    cardPart = Column(String)
    coordinates = Column(String)
    text = Column(String)
    symbols = Column(String)
    color = Column(String)
    templateFile = Column(String)

    cardID = Column(Integer, ForeignKey("cardGames.id"))
    cardGame = relationship("CardGame", backref=backref(
        "cardInfo", order_by=id), lazy=True)

    def __init__(self, cardPart, coordinates, text, symbols, color, templateFile):
        self.cardPart = cardPart
        self.coordinates = coordinates
        self.text = text
        self.symbols = symbols
        self.color = color
        self.templateFile = templateFile


# create tables
Base.metadata.create_all(engine)
