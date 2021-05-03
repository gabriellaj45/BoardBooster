import os
if os.path.exists("static/extractedRegion.jpg"):
    os.remove("static/extractedRegion.jpg")

filelist = [f for f in os.listdir('static/userData')]
for f in filelist:
    os.remove(os.path.join('static/userData', f))
filelist = [f for f in os.listdir('static/uploads')]
for f in filelist:
    os.remove(os.path.join('static/uploads', f))
filelist = [f for f in os.listdir('static/cardSymbols')]
for f in filelist:
    os.remove(os.path.join('static/cardSymbols', f))
filelist = [f for f in os.listdir('static/cardTemplates')]
for f in filelist:
    os.remove(os.path.join('static/cardTemplates', f))
filelist = [f for f in os.listdir('static/newCards')]
for f in filelist:
    os.remove(os.path.join('static/newCards', f))
filelist = [f for f in os.listdir('static/finalFiles')]
for f in filelist:
    os.remove(os.path.join('static/finalFiles', f))