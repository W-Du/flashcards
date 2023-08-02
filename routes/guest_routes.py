from flask import Blueprint, render_template, redirect, url_for, request, session
from models import User, Word, List
from forms import AddFlashcardForm, AddListForm, ChangeDailyGoalForm, UpdateWordForm, UpdateListForm
from app import db
from data import guestData, GuestList
from markupsafe import escape


guest_bp = Blueprint('guests', __name__)

@guest_bp.before_request
def saveGuestData():
    session['guest'] = guestData

@guest_bp.route('/guest')
def profileG():
    guest = session.get('guest', None)
    if not guest:
        print('no guest is found')
    return render_template('profile.html', user=guest)

@guest_bp.route('/guest/setting', methods=['GET', 'POST'])
def settingG():
    formList = AddListForm()
    guest = session.get('guest', None)
    if formList.validate_on_submit():
        new_list = GuestList(listname=escape(formList.listname.data))
        try:
            guest.addList(new_list)
        except Exception as e:
            msg = str(e)
            return render_template('setting.html', user=guest, formList = formList, message=msg)
        formList.listname.data = None
        return render_template('setting.html', user=guest, formList = formList)
    return render_template('setting.html', user=guest, formList = formList)

@guest_bp.route('/guest/lists/<listname>', methods=['GET','POST'])
def updateListG(listname):
    guest = session.get('guest', None)
    lst = guest.getList(listname)
    if not guest or not lst:
        raise Exception('no guest or no list found')
    words = lst.words
    form = UpdateListForm()
    formCard = AddFlashcardForm()
    if form.validate_on_submit():
        new_name = escape(form.listname.data)
        if new_name != lst.listname:
            lst.listname = new_name
    return render_template('list.html', lst=lst, words=words, user=guest, form=form, formCard=formCard)


