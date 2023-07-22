from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy.sql import func
from models import User, Word, List
from forms import AddFlashcardForm, AddListForm, ChangeDailyGoalForm, UpdateWordForm, UpdateListForm
from app import db, login_manager
from functools import wraps

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
    return render_template('profile.html', user=current_user)


# practice
@user_bp.route('/user/<username>/practice', methods=['GET', 'POST'])
@login_required
@check_username_match
def practice(username, cur_word_idx = 0):
    words_today = None
    if current_user.daily_goal and len(list(current_user.words)) >= current_user.daily_goal:
        words_today = Word.query.order_by(Word.priority.desc(), func.random()).limit(current_user.daily_goal)          
    else:
        words_today = Word.query.order_by(Word.priority.desc(), func.random()).all()
    length = len(list(words_today))
    cur_word_idx = request.args.get('index', default=0, type=int)
    if cur_word_idx >= length:
        return redirect(url_for('user.completeGoal', username=username))
    cur_word = words_today[cur_word_idx]
    return render_template('practice.html', user=current_user, cur_word_idx=cur_word_idx, cur_word=cur_word, length=length)

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
        elif action=='remember':
            word.priority -= 1
        db.session.commit()
    except Exception as e:
        print(str(e))
    return redirect(url_for('user.practice', username=username, index=cur_index+1))

@user_bp.route('/user/<username>/goal')
@login_required
@check_username_match
def completeGoal(username):
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
    # formBulk = BulkEditForm()
    # formBulk.addFlashCards(words)
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
    print(lst_idx)
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
    words = None
    if action == 'add to':
        words = [w for w in current_user.words if lst not in w.lists]
    elif action == 'remove from':
        words = lst.words

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
    return render_template('flashcards-bulk.html', words=words, lst=lst, user=current_user, action=action)


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