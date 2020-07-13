from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["BOARD_UPLOADS"] = "/Users/superhuman/PycharmProjects/LabelGenWebv3/static/uploads/board"
app.config["SYMBOL_UPLOADS"] = "/Users/superhuman/PycharmProjects/LabelGenWebv3/static/uploads/symbols"
app.config["CARD_UPLOADS"] = "/Users/superhuman/PycharmProjects/LabelGenWebv3/static/newCards"
app.config["FINAL_UPLOADS"] = "/Users/superhuman/PycharmProjects/LabelGenWebv3/static"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cardGames.db'
app.secret_key = "flask rocks!"

db = SQLAlchemy(app)
