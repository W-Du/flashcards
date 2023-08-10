from flask import Blueprint, render_template, redirect, url_for, request, session
from models import User, Word, List
from forms import AddFlashcardForm, AddListForm, ChangeDailyGoalForm, UpdateWordForm, UpdateListForm
from app import db
from data import guestData, GuestList, GuestWord, arrangeByPriority
from markupsafe import escape
from functions import getColorByPriority
# from routes/user_routes import processform


guest_bp = Blueprint('guests', __name__)

@guest_bp.before_request
def saveGuestData():
    guest = session.get('guest', None)
    if not guest:
        session['guest'] = guestData

@guest_bp.route('/guest')
def profile():
    guest = retrieveGuest()
    return render_template('profile.html', user=guest)

@guest_bp.route('/guest/setting', methods=['GET', 'POST'])
def setting():
    formList = AddListForm()
    guest = retrieveGuest()
    if formList.validate_on_submit():
        for l in guest.lists:
            if l.listname == formList.listname.data:
                msg=f'There is already a list called {formList.listname.data}, try with another listname'
                return render_template('setting.html', user=guest, formList=formList, message=msg)
        new_list = GuestList(listname=escape(formList.listname.data))
        try:
            guest.addList(new_list)
        except Exception as e:
            msg = str(e)
            return render_template('setting.html', user=guest, formList=formList, message=msg)
        formList.listname.data = None
        return render_template('setting.html', user=guest, formList = formList)
    return render_template('setting.html', user=guest, formList = formList)


### lists
@guest_bp.route('/guest/lists/<id>', methods=['GET','POST'])
def updateList(id):
    guest = retrieveGuest()
    lst = guest.getListById(int(id))
    if not guest or not lst:
        raise Exception('no guest or no list found')
    msg1 = request.args.get('message')
    words = lst.words
    form = UpdateListForm()
    formCard = AddFlashcardForm(addToList=[int(id)])
    if form.validate_on_submit():
        new_name = escape(form.listname.data)
        if new_name != lst.listname:
            lst.listname = new_name
    if msg1:
        msg = 'you already have this word in flashcards'
        return render_template('list.html', lst=lst, words=words, user=guest, form=form, formCard=formCard, message=msg)
    return render_template('list.html', lst=lst, words=words, user=guest, form=form, formCard=formCard)

@guest_bp.route('/guest/lists/delete/<id>', methods=['POST'])
def deleteList(id):
    guest = retrieveGuest()
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


## flashcards
@guest_bp.route('/guest/flashcards', methods=['GET', 'POST'])
def flashcardsG():
    guest = retrieveGuest()
    lst_idx = request.form.get('lst_id')
    form = AddFlashcardForm(addToList=[0])
    display = request.args.get('display')
    if form.validate_on_submit():
        try:
            for w in guest.words:
                if w.word == escape(form.word.data):
                    if lst_idx:
                        return redirect(url_for('guests.updateList', id=lst_idx, message='exist'))
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
    guest = retrieveGuest()
    wordObj = guest.getWord(word)
    lst_idx = request.form.get('lst_id') or request.args.get('list')
    word_inlists_idx = []
    for l in wordObj.lists:
        word_inlists_idx.append(l.id)
    form = UpdateWordForm(Inlists=word_inlists_idx, description = wordObj.description)
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
    guest = retrieveGuest()
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


### practice
@guest_bp.route('/guest/practice', methods=['GET', 'POST'])
def practice(cur_word_idx=0):
    guest = retrieveGuest()
    words = session.get('words_practice', [])
    words_again = session.get('words_again', [])
    goal = session.get('goal', None)
    words_review_7 = session.get('words_review_7', set())
    length = len(words)
    
    if cur_word_idx == 0:
        cur_word_idx = request.args.get('index', default=0, type=int)

    if cur_word_idx >= length:
        if goal and goal > length:
            session['goal'] = goal - length
            return redirect(url_for('guests.practice_cont'))
        elif len(words_again) == 0 and len(words_review_7) > 0:
            return redirect(url_for('guests.practice_review', index=cur_word_idx))           
        elif len(words_again) > 0:
            cur_word = words_again.pop(0)
        else:
            return redirect(url_for('guests.completeGoal'))
    elif len(words_review_7) == 7:
        return redirect(url_for('guests.practice_review', index=cur_word_idx))
    else:
        cur_word = words[cur_word_idx]
    words_review_7.add(cur_word)
    color = getColorByPriority(cur_word.priority)
    # print(color)
    return render_template('practice.html', user=guest, cur_word_idx=cur_word_idx, cur_word=cur_word, color=color)

@guest_bp.route('/guest/practice/start', methods=['POST'])
def startPractice():
    lst = request.form.get('list')      
    guest = retrieveGuest()
    goal = request.form.get('goal') or session.get('goal', None)
    if goal:
        goal = int(goal)
        if lst == 'all':
            words_practice = arrangeByPriority(guest.words)[:goal]
        else:
            list_id = int(lst) 
            if session.get('list_in_practice_id') is not None:
                session['list_in_practice_id'].append(list_id)
            else:
                session['list_in_practice_id'] = [list_id]
            listObj= guest.getListById(list_id)
            lst_length = len(listObj.words)
            if goal >= lst_length:
                words_practice = listObj.words
            else:
                words_practice = arrangeByPriority(listObj.words)[:goal]
    else:
        list_id = int(lst)
        listObj= guest.getListById(list_id)
        words_practice = listObj.words
        
    session['words_practice'] = words_practice
    session['goal'] = goal
    session['words_review_7'] = set()
    if session.get('words_again') is None:
        session['words_again'] = []
    return redirect(url_for('guests.practice'))

@guest_bp.route('/guest/practice/continue', methods=['GET','POST'])
def practice_cont():
    guest = retrieveGuest()    
    return render_template('practice-continue.html', user=guest)

@guest_bp.route('/guest/practice/review/<index>', methods=['GET', 'POST'])
def practice_review(index):
    guest = session.get('guest', None)
    if not guest:
        raise Exception("no guest found")
    if request.method == 'POST':
        session['words_review_7'] = set()
        return redirect(url_for('guests.practice', index=index))
    return render_template('practice_review.html', user=guest, cur_word_idx=index)

@guest_bp.route('/guest/word-priority', methods=['POST'])
def word_priority():
    guest = retrieveGuest()
    words_again = session.get('words_again', [])
    try:
        w = request.form.get('word_id')
        word = guest.getWord(w)
        action = request.form.get('action')
        cur_index = int(request.form.get('cur_index'))
        if action == 'not_remember':
            word.priority += 1
            guest.updateWords()
            words_again.append(word)
            # print(words_again)
            return redirect(url_for('guests.practice', index=cur_index+1))
        elif action=='remember':
            word.priority -= 1  
            guest.updateWords()
    except Exception as e:
        print(str(e))
    return redirect(url_for('guests.practice', index=cur_index+1))

@guest_bp.route('/guest/practice/goal')
def completeGoal():
    guest = retrieveGuest()
    session.pop('words_practice', None)
    session.pop('words_again', None)
    session.pop('list_in_practice_id', None)
    session.pop('goal', None)
    session.pop('words_review_7', None)
    return render_template('goalComplete.html', user=guest)   


## bulk edit
@guest_bp.route('/guest/flashcards/bulk/<listId>', methods=['GET','POST'])
def bulkEdit(listId):
    guest = retrieveGuest()
    lst = guest.getListById(int(listId))
    action = request.form.get('action')
    words_dict = {}
    if action == 'add to':
        words = [w for w in guest.words if lst not in w.lists]
        if len(words) > 0:
            list_names = [lst.listname for lst in guest.lists if lst.id is not int(listId)]
            for name in list_names:
                words_dict[name] = []
            for i in range(len(words)):
                for l in words[i].lists:
                    words_dict[l.listname].append(words[i])
    elif action == 'remove from':
        words_dict[f'words in {lst.listname}'] = lst.words

    if request.method == 'POST':  
        selected_words = request.form.getlist('word_id')
        databaseAction = request.form.get('databaseAction')
        if databaseAction == 'add to':
            try:
                for w in selected_words:
                    word = guest.getWord(w)
                    lst.addWord(word)
                    guest.updateWords()
                return redirect(url_for('guests.updateList', id=listId))
            except Exception as e:
                print('add to list:', str(e))
        elif databaseAction == 'remove from':
            try:
                for w in selected_words:
                    word = lst.getWord(w)
                    word.removeFromList(lst)
                    lst.removeWord(word)
                    guest.updateWords()
            except Exception as e:
                print('remove from list:', str(e))
            return redirect(url_for('guests.updateList', id=listId))
    return render_template('flashcards-bulk.html', words_dict=words_dict, lst=lst, user=guest, action=action)




@guest_bp.route('/guest/clear')
def clear():
    session.pop('guest', None)
    session.clear()
    return redirect(url_for('guests.profile'))


# helper method
def processform(form):
    for field in form:
        field.data = None

def retrieveGuest():
    guest = session.get('guest', None)
    if not guest:
        print('cannot find guest')
        return redirect(url_for('login.home', message='NoGuest'))
    return guest