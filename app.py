from flask import Flask

app = Flask(__name__)
app.config["BOARD_UPLOADS"] = "/Users/superhuman/PycharmProjects/BoardBooster/static/uploads"
# app.config["SYMBOL_UPLOADS"] = "/Users/superhuman/PycharmProjects/BoardBooster/static/uploads"
app.config["CARD_UPLOADS"] = "/Users/superhuman/PycharmProjects/BoardBooster/static/newCards"
app.config["FINAL_UPLOADS"] = "/Users/superhuman/PycharmProjects/BoardBooster/static/finalFiles"
app.secret_key = "flask rocks!"