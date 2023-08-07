from flask import Blueprint, render_template, redirect, url_for, request, session
from flask_login import current_user, login_user, logout_user, login_required
from models import User, Word, List
from forms import RegistrationForm, LoginForm
from app import db, login_manager
from markupsafe import escape



login_bp = Blueprint('login', __name__)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@login_bp.route('/')
def home():
    message = request.args.get('message')
    if message:
        msg = 'please try again'
        return render_template('home.html', message=msg)
    return render_template('home.html')

@login_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        emailInput = form.email.data
        emailExists = User.query.filter_by(email = emailInput).first()
        usernameInput = form.username.data
        usernameExists = User.query.filter_by(username=usernameInput).first()
        if(emailExists or usernameExists):
            if(emailExists):
                msg = "Email already registered"
                form.username.data = None
            else:
                msg = 'Username is taken'
                form.username.data = None
            return render_template('register.html', form=form, message=msg)
        new_user = User(username = escape(form.username.data), email = escape(form.email.data))
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        defaultLst = List(listname='default')
        db.session.add(defaultLst)
        defaultLst.users.append(new_user)
        new_user.lists.append(defaultLst)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('user.profile', username=new_user.username))
    return render_template('register.html', form = form)

@login_bp.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()
        if not user or not user.check_password(form.password.data):
            msg = 'Wrong Credentials'
            form.username.data = None
            form.password.data = None
            return render_template('login.html', form=form, message=msg)
        else:
            login_user(user)
            return redirect(url_for('user.profile', username=user.username))
    return render_template('login.html', form=form)


@login_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('login.home'))

