'''
https://dzone.com/articles/flask-101-adding-a-database
https://dzone.com/articles/flask-101-adding-editing-and-displaying-data
https://www.blog.pythonlibrary.org/2017/12/13/flask-101-how-to-add-a-search-form/
'''
from dbSetup import init_db, db_session
from app import app
from forms import *
from flask import flash, render_template, request, redirect
from models import CardInformation, CardGame

init_db()


@app.route('/', methods=['GET', 'POST'])
def index():
    search = CardSearchForm(request.form)
    if request.method == 'POST':
        return searchResults(search)
    return render_template('cardTable.html', form=search)


@app.route('/results')
def searchResults(search):
    results = []
    search_string = search.data['search']
    if search.data['search'] == '':
        qry = db_session.query(CardInformation)
        results = qry.all()

    if not results:
        flash('No results found!')
        return redirect('/')
    else:
        # display results
        return render_template('results.html', table=results)


@app.route('/newGame', methods=['GET', 'POST'])
def newGame():
    form = CardForm(request.form)
    if request.method == 'POST' and form.validate():
        # save the album
        cardInfo = CardInformation('', '', '', '', '', '')
        saveChanges(cardInfo, form, new=True)
        flash('Card information saved successfully!')
        return redirect('/')
    return render_template('newGame.html', form=form)


@app.route('/item/<int:id>', methods=['GET', 'POST'])
def editTemplates(id):
    qry = db_session.query(CardInformation).filter(
        CardInformation.id == id)
    album = qry.first()

    if album:
        form = CardSearchForm(formdata=request.form, obj=album)
        if request.method == 'POST' and form.validate():
            # save edits
            saveChanges(album, form)
            flash('Album updated successfully!')
            return redirect('/')
        return render_template('edit_album.html', form=form)
    else:
        return 'Error loading #{id}'.format(id=id)


def saveChanges(cardInfo, form, new=False):

    cardGame = CardGame('')
    cardGame.name = form.cardGame.data

    cardInfo.cardGame = cardGame
    cardInfo.cardPart = form.cardPart.data
    cardInfo.coordinates = form.coors.data
    cardInfo.text = form.text.data
    cardInfo.symbols = form.symbol.data
    cardInfo.color = form.color.data
    cardInfo.templateFile = form.templateFile.data

    if new:
        # Add the new album to the database
        db_session.add(cardInfo)

    # commit the data to the database
    db_session.commit()


if __name__ == '__main__':

    app.run()
