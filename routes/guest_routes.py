from flask import Blueprint, render_template, redirect, url_for, request, session
from models import User, Word, List
from forms import AddFlashcardForm, AddListForm, ChangeDailyGoalForm, UpdateWordForm, UpdateListForm
from app import db
from data import guestData, GuestList, GuestWord
from markupsafe import escape
# from routes/user_routes import processform


guest_bp = Blueprint('guests', __name__)

@guest_bp.before_request
def saveGuestData():
    guest = session.get('guest', None)
    if not guest:
        session['guest'] = guestData

@guest_bp.route('/guest')
def profile():
    guest = session.get('guest', None)
    if not guest:
        print('no guest is found')
    return render_template('profile.html', user=guest)

@guest_bp.route('/guest/setting', methods=['GET', 'POST'])
def setting():
    formList = AddListForm()
    guest = session.get('guest', None)
    if formList.validate_on_submit():
        new_list = GuestList(listname=escape(formList.listname.data))
        try:
            guest.addList(new_list)
            print(new_list.id)
        except Exception as e:
            msg = str(e)
            return render_template('setting.html', user=guest, formList = formList, message=msg)
        formList.listname.data = None
        return render_template('setting.html', user=guest, formList = formList)
    return render_template('setting.html', user=guest, formList = formList)

@guest_bp.route('/guest/lists/<id>', methods=['GET','POST'])
def updateList(id):
    guest = session.get('guest', None)
    lst = guest.getListById(int(id))
    if not guest or not lst:
        raise Exception('no guest or no list found')
    words = lst.words
    form = UpdateListForm()
    formCard = AddFlashcardForm(addToList=[int(id)])
    if form.validate_on_submit():
        new_name = escape(form.listname.data)
        if new_name != lst.listname:
            lst.listname = new_name
    return render_template('list.html', lst=lst, words=words, user=guest, form=form, formCard=formCard)

@guest_bp.route('/guest/lists/delete/<id>', methods=['POST'])
def deleteList(id):
    guest = session.get('guest', None)
    if not guest:
        return redirect('login.home')
    lst_to_delete = guest.getListById(int(id))
    keep = request.form.get('delete-all')
    lst_idx = request.form.get('lst_id')
    try:
        if not keep:
            defaultLst = guest.getListByName('default')
            defaultLst.addWords(lst_to_delete.words)
            guest.removeList(lst_to_delete)
        else:
            guest.removeList(lst_to_delete)
            guest.updateWords()
    except Exception as e:
        print(str(e))
    if lst_idx:
        return redirect(url_for('guests.updateList', id=int(lst_idx)))
    return redirect(url_for('guests.setting'))

@guest_bp.route('/guest/flashcards', methods=['GET', 'POST'])
def flashcardsG():
    guest = session.get('guest', None)
    if not guest:
        raise Exception("no guest found")
        return
    lst_idx = request.form.get('lst_id')
    # print('lst_idx', lst_idx)
    form = AddFlashcardForm(addToList=[0])
    display = request.args.get('display')
    if form.validate_on_submit():
        try:
            for w in guest.words:
                if w.word == escape(form.word.data):
                    msg = 'you already have this word in flashcards'
                    return render_template('flashcards.html', words=guest.words, form=form, user=guest, display=True, message=msg)
            new_word = GuestWord(word=escape(form.word.data), description=escape(form.description.data))
            selected_lists = form.addToList.data    
            if not isinstance(selected_lists, list):
                selected_lists = [selected_lists]
            for lstId in selected_lists:
                lst = guest.getListById(int(lstId))
                new_word.addToList(lst)
                guest.updateWords()
            form.word.data = None
            form.description.data = None
            # print(len(guest.words))
            if lst_idx:
                return redirect(url_for('guests.updateList', id=int(lst_idx)))
            return render_template('flashcards.html', words=guest.words, form=form, user=guest)
        except Exception as e:
            msg = 'something went wrong: \n' + str(e)
            return render_template('flashcards.html', words=guest.words, form=form, user=guest, message=msg)
    if lst_idx is not None:
        return redirect(url_for('guests.updateList', id=int(lst_idx)))
    if display is not None:
        return render_template('flashcards.html', words=guest.words, form=form, user=guest, display=display)
    return render_template('flashcards.html', words=guest.words, form=form, user=guest)

@guest_bp.route('/guest/flashcards/<word>', methods=['GET','POST'])
def updateFlashcardG(word):
    guest = session.get('guest', None)
    if not guest:
        raise Exception('no guest found')
        return
    wordObj = guest.getWord(word)
    lst_idx = request.form.get('lst_id') or request.args.get('list')
    word_inlists_idx = []
    for l in wordObj.lists:
        word_inlists_idx.append(l.id)
    form = UpdateWordForm(Inlists=word_inlists_idx)
    if form.validate_on_submit():
        new_description = escape(form.description.data)
        new_word = escape(form.word.data)
        new_lists_idx = form.Inlists.data
        if not isinstance(new_lists_idx, list):
            new_lists_idx = [new_lists_idx]
        if new_description != wordObj.description or new_word != wordObj.word or word_inlists_idx != new_lists_idx:
            wordObj.word = new_word
            wordObj.description = new_description
            try:
                if word_inlists_idx != new_lists_idx:
                    idx_remove = []
                    idx_add = []
                    for idx in set().union(*[word_inlists_idx, new_lists_idx]):
                        if idx not in word_inlists_idx:
                            l = guest.getListById(int(idx))
                            wordObj.addToList(l)
                        elif idx not in new_lists_idx:
                            l = guest.getListById(int(idx))
                            l.removeWord(wordObj)
                            wordObj.removeFromList(l)
            except Exception as e:
                print(str(e))
    if lst_idx is not None:
        return render_template('word.html', word=wordObj, user=guest, form=form, lst_idx=int(lst_idx))
    return render_template('word.html', word=wordObj, user=guest, form=form)

@guest_bp.route('/guest/flashcards/delete/<word>', methods=['POST'])
def deleteFlashcardG(word):
    guest = session.get('guest', None)
    if not guest:
        return redirect(url_for('guests.flashcardsG'))
    wordObj = guest.getWord(word)
    lst_id = request.form.get('lst_id')
    try:
        for l in wordObj.lists:
            l.removeWord(wordObj)
        guest.updateWords()
    except Exception as e:
        print(str(e))
    if lst_id is not None:
        return redirect(url_for('guests.updateList', id=int(lst_id)))
    return redirect(url_for('guests.flashcardsG'))






@guest_bp.route('/guest/clear', methods=['POST'])
def clear():
    session.pop('guest', None)
    return redirect(url_for('guests.profileG'))


# helper method
def processform(form):
    for field in form:
        field.data = None