from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, session
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy.sql import func
from models import User, Word, List, word_list
from forms import AddFlashcardForm, AddListForm, ChangeDailyGoalForm, UpdateWordForm, UpdateListForm
from app import db, login_manager
from functools import wraps
from datetime import datetime
from functions import elaspedTime

user_bp = Blueprint('user', __name__)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

def check_username_match(func):
    @wraps(func)
    def wrapper(username, *args, **kwargs):
        if username != current_user.username:
            return redirect(url_for('login.login'))
        return func(username, *args, **kwargs)
    return wrapper


@user_bp.route('/user/<username>')
@login_required
@check_username_match
def profile(username):
    if not current_user:
        return redirect(url_for('login.login'))
    # update word.priority automatically
    if 'last_visit_app' not in session or elaspedTime(session['last_visit_app'], datetime.today()) > 3:
        session['last_visit_app'] = datetime.today()
        for w in current_user.words:
            w.updatePriorityTime()
        db.session.commit()
    return render_template('profile.html', user=current_user)


# practice
@user_bp.route('/user/<username>/practice', methods=['GET', 'POST'])
@login_required
@check_username_match
def practice(username, cur_word_idx=0, again=-1):
    words = session.get('words_practice', [])
    id_review = session.get('id_review', [])
    goal = session.get('goal', None)
    words_review_7 = session.get('words_review_7', [])
    
    if cur_word_idx == 0:
        cur_word_idx = request.args.get('index', default=0, type=int)
    again = request.args.get('again', default=-1, type=int)
    if again != -1:
        id_review.append(int(again))
    length = len(words)
    
    if cur_word_idx >= length + len(id_review):
        if goal > length:
            session['goal'] = goal - cur_word_idx
            return redirect(url_for('user.practice_cont', username=username))
        if len(words_review_7) > 0:
            return redirect(url_for('user.practice_review', username=username, index=cur_word_idx))
        return redirect(url_for('user.completeGoal', username=username))
    elif len(words_review_7) == 7:
        return redirect(url_for('user.practice_review', username=username, index=cur_word_idx))
    elif cur_word_idx >= length and cur_word_idx < length + len(id_review):
        cur_word = words[id_review[cur_word_idx-len(words)]]
    else:
        cur_word = words[cur_word_idx]
    words_review_7.append(cur_word)
    return render_template('practice.html', user=current_user, cur_word_idx=cur_word_idx, cur_word=cur_word)


@user_bp.route('/user/<username>/practice/start', methods=['POST'])
@login_required
@check_username_match
def startPractice(username):
    goal = request.form.get('goal') or session.get('goal', None)
    if goal:
        goal = int(goal)
    lst = request.form.get('list')      
    if lst == 'all':
        words_practice = Word.query.order_by(Word.priority.desc(), func.random()).limit(goal).all()
    else:
        list_id = int(lst) 
        if session.get('list_in_practice_id') is not None:
            session['list_in_practice_id'].append(list_id)
        else:
            session['list_in_practice_id'] = []
            session['list_in_practice_id'].append(list_id)
        list_query = List.query.get(list_id)
        lst_length = len(list(list_query.words))
        if goal > lst_length:
            words_practice = Word.query.join(word_list).filter(word_list.c.list_id == list_id).order_by(Word.priority.desc(), func.random()).all()
        else:
            words_practice = Word.query.join(word_list).filter(word_list.c.list_id == list_id).order_by(Word.priority.desc(), func.random()).limit(goal).all()

    session['words_practice'] = words_practice
    session['id_review'] = []
    session['goal'] = goal
    session['words_review_7'] = []
    return redirect(url_for('user.practice', username=username))


@user_bp.route('/user/<username>/practice/continue', methods=['GET','POST'])
@login_required
@check_username_match
def practice_cont(username):
    return render_template('practice-continue.html', user=current_user)

@user_bp.route('/user/<username>/practice/review/<index>', methods=['GET', 'POST'])
@login_required
@check_username_match
def practice_review(username, index):
    if request.method == 'POST':
        for w in session['words_review_7']:
            w.updateLastVisit()
        db.session.commit()
        session['words_review_7'] = []
        return redirect(url_for('user.practice', username=username, index=index))
    return render_template('practice_review.html', user=current_user, cur_word_idx=index)

@user_bp.route('/user/<username>/word-priority', methods=['POST'])
@login_required
@check_username_match
def word_priority(username):
    try:
        id = int(request.form.get('word_id'))
        word = Word.query.get(id)
        action = request.form.get('action')
        cur_index = int(request.form.get('cur_index'))
        if action == 'not_remember':
            word.priority += 1
            db.session.commit()
            return redirect(url_for('user.practice', username=username, index=cur_index+1, again=cur_index))
        elif action=='remember':
            word.priority -= 1
            db.session.commit()            
    except Exception as e:
        print(str(e))
    return redirect(url_for('user.practice', username=username, index=cur_index+1))

@user_bp.route('/user/<username>/practice/goal')
@login_required
@check_username_match
def completeGoal(username):
    session.pop('words_practice', None)
    session.pop('id_review', None)
    session.pop('list_in_practice_id', None)
    session.pop('goal', None)
    session.pop('words_review_7', None)
    return render_template('goalComplete.html', user=current_user)    

@user_bp.route('/user/<username>/setting', methods=['GET','POST'])
@login_required
@check_username_match
def setting(username):
    formList = AddListForm()
    formGoal = ChangeDailyGoalForm()
    form_id = request.form.get('form_id')

    if form_id == 'list':
        if formList.validate_on_submit():
            new_list = List(listname=formList.listname.data)
            if new_list:
                db.session.add(new_list)
                new_list.users.append(current_user)
                current_user.lists.append(new_list)
                db.session.commit()
                formList.listname.data = None
                return render_template('setting.html', user = current_user, formList = formList, formGoal = formGoal)
            else:
                msg = 'Could not create a new list'
                return render_template('setting.html', user=current_user, formList=formList, formGoal = formGoal, message=msg)
    elif form_id =='goal':
        if formGoal.validate_on_submit():
            current_user.daily_goal = int(formGoal.goal.data)
            db.session.commit()
            if current_user.daily_goal == int(formGoal.goal.data):
                print('correct')
                formGoal = ChangeDailyGoalForm(formdata=None)
                return render_template('setting.html', user=current_user, formList = formList, formGoal = formGoal)
            else:
                msg = 'something went wrong, daily goal not updated'
                return render_template('setting.html', user=user, formList=formList, formGoal = formGoal, message=msg)
    return render_template('setting.html', user=current_user, formList = formList, formGoal = formGoal)

@user_bp.route('/user/<username>/lists/<id>',methods=['GET','POST'])
@login_required
@check_username_match
def updateList(username, id):
    lst = List.query.get(int(id))
    words = lst.words
    form = UpdateListForm()
    formCard = AddFlashcardForm(addToList=[lst.id])
    if form.validate_on_submit():
        new_name = form.listname.data
        if new_name != lst.listname:
            lst.listname = new_name
            db.session.commit()
    return render_template('list.html', lst=lst, words=words, user=current_user, form=form, formCard=formCard)

@user_bp.route('/user/<username>/lists/delete/<id>', methods=['POST'])
@login_required
@check_username_match
def deleteList(username, id):
    lst_to_delete = List.query.get(int(id))
    keep = request.form.get('delete-all')
    print(keep)
    try:
        if not keep:
            current_user.lists.remove(lst_to_delete)
        else:
            for w in lst_to_delete.words:
                db.session.delete(w)
            db.session.delete(lst_to_delete)
        db.session.commit()
    except Exception as e:
        print(str(e))
    return redirect(url_for('user.setting', username=username))


@user_bp.route('/user/<username>/flashcards', methods=['GET', 'POST'])
@login_required
@check_username_match
def flashcards(username):
    form = AddFlashcardForm()
    lst_idx = request.form.get('lst_id')
    if form.validate_on_submit():
        try:
            for w in current_user.words:
                if w.word == form.word.data:
                    msg = 'you already have this word in flashcards'
                    return render_template('addCard.html', form=form, message=msg, user=current_user)
            new_word = Word(word=form.word.data, description=form.description.data)
            selected_lists = form.addToList.data
            if new_word:
                db.session.add(new_word)
                db.session.commit()
                current_user.words.append(new_word)
                new_word.users.append(current_user)
                if selected_lists:
                    if not isinstance(selected_lists, list):
                        selected_lists = [selected_lists]
                    lists = List.query.filter(List.id.in_(selected_lists)).all()
                    new_word.lists.extend(lists)
                    for lst in lists:
                        lst.words.append(new_word)
                db.session.commit()
            processform(form)
            if lst_idx is not None:
                return redirect(url_for('user.updateList', username=username, id=int(lst_idx)))
            return render_template('flashcards.html', words=current_user.words, form=form, user=current_user)
        except Exception as e:
            msg = 'something went wrong: \n' + str(e)
            return render_template('flashcards.html', words=current_user.words, form=form, user=current_user, message=msg)
    if lst_idx is not None:
        return redirect(url_for('user.updateList', username=username, id=int(lst_idx)))
    return render_template('flashcards.html', words=current_user.words, form=form, user=current_user)


@user_bp.route('/user/<username>/flashcards/bulk/<listId>', methods=['GET','POST'])
@login_required
@check_username_match
def bulkEdit(username, listId):
    lst = List.query.get(int(listId))
    action = request.form.get('action')
    words_dict = {}
    if action == 'add to':
        words = [w for w in current_user.words if lst not in w.lists]
        if len(words) > 0:
            list_names = [lst.listname for lst in current_user.lists if lst.id is not int(listId)]
            if list_names:
                words_dict['words not in any list'] = []
                for name in list_names:
                    words_dict[name] = []
                for i in range(len(words)):
                    if len(words[i].lists) == 0:
                        words_dict['words not in any list'].append(words[i])
                    else:
                        for l in words[i].lists:
                            words_dict[l.listname].append(words[i])
            else:
                words_dict['words not in any list'] = words
            
    elif action == 'remove from':
        words_dict[f'words in {lst.listname}'] = lst.words

    if request.method == 'POST':  
        selected_ids = request.form.getlist('word_id')
        databaseAction = request.form.get('databaseAction')
        if databaseAction == 'add to':
            try:
                for id in selected_ids:
                    word = Word.query.get(int(id))
                    lst.words.append(word)
                    word.lists.append(lst)
                    db.session.commit()
                return redirect(url_for('user.updateList', username=username, id=listId))
            except Exception as e:
                print(str(e))
        elif databaseAction == 'remove from':
            try:
                for id in selected_ids:
                    word = Word.query.get(int(id))
                    if word in lst.words:
                        lst.words.remove(word)
                    if lst in word.lists:
                        word.lists.remove(lst)
                    db.session.commit()
            except Exception as e:
                print(str(e))
            return redirect(url_for('user.updateList', username=username, id=listId))
    return render_template('flashcards-bulk.html', words_dict=words_dict, lst=lst, user=current_user, action=action)


@user_bp.route('/user/<username>/flashcards/<id>', methods=['GET','POST'])
@login_required
@check_username_match
def updateFlashcard(username, id):
    word = Word.query.get(int(id))
    lst_idx = request.form.get('lst_id') or request.args.get('list')
    word_inlists_idx = []
    for l in word.lists:
        word_inlists_idx.append(l.id)
    form = UpdateWordForm(Inlists=word_inlists_idx)
    if form.validate_on_submit():
        new_description = form.description.data
        new_word = form.word.data
        new_lists_idx = form.Inlists.data
        if not isinstance(new_lists_idx, list):
            new_lists_idx = [new_lists_idx]
        if new_description != word.description or new_word != word.word or word_inlists_idx != new_lists_idx:
            word.word = new_word
            word.description = new_description
            try:
                if word_inlists_idx != new_lists_idx:
                    idx_remove = []
                    idx_add = []
                    for idx in set().union(*[word_inlists_idx, new_lists_idx]):
                        if idx not in word_inlists_idx:
                            l = List.query.get(int(idx))
                            word.lists.append(l)
                        elif idx not in new_lists_idx:
                            l = List.query.get(int(idx))
                            word.lists.remove(l)
                db.session.commit()
            except Exception as e:
                print(str(e))
    if lst_idx is not None:
        return render_template('word.html', word=word, user=current_user, form=form, lst_idx=int(lst_idx))
    return render_template('word.html', word=word, user=current_user, form=form)


@user_bp.route('/user/<username>/flashcards/delete/<id>', methods=['POST'])
@login_required
@check_username_match
def deleteFlashcard(username, id):
    word = Word.query.get(int(id))
    lst_id = request.form.get('lst_id')
    try:
        for l in word.lists:
            l.words.remove(word)
        db.session.delete(word)
        db.session.commit()
    except Exception as e:
        print(str(e))
    if lst_id is not None:
        return redirect(url_for('user.updateList', username=username, id=int(lst_id)))
    return redirect(url_for('user.flashcards', username=username))
    



# helper method
def processform(form):
    for field in form:
        field.data = None