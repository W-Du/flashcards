from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, SelectMultipleField, TextAreaField, IntegerField, RadioField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from flask_login import current_user
from models import List

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Password-confirm', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField("Remember me")
    submit = SubmitField('Login')

class AddVocabularyForm(FlaskForm):
    word = StringField('New Word', validators=[DataRequired()])
    description = TextAreaField('Meanings & Sample Sentences', validators=[DataRequired()])
    addToList = SelectMultipleField('Add to List', coerce=int)
    submit = SubmitField('Add new word')

    def __init__(self, *args, **kwargs):
        super(AddVocabularyForm, self).__init__(*args, **kwargs)
        if current_user.is_authenticated:
            self.addToList.choices = [(l.id, l.listname) for l in current_user.lists]

class AddListForm(FlaskForm):
    listname = StringField('Name of list', validators=[DataRequired()])
    submit = SubmitField('Add New List')

class ChangeDailyGoalForm(FlaskForm):
    goal = IntegerField('Daily Goal', validators=[DataRequired()])
    submit = SubmitField('Update')

# class WordPriorityForm(FlaskForm):
#     remember = SubmitField('I got this')
#     not_remember = SubmitField('Do not have a clue')

class UpdateListForm(FlaskForm):
    listname = StringField('Name of List', validators=[DataRequired()])
    submit = SubmitField('Update')

class UpdateWordForm(FlaskForm):
    word= StringField('Word', validators=[DataRequired()])
    description = StringField('Meaning', validators=[DataRequired()])
    submit = SubmitField('Update')





   
