from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, SelectMultipleField, TextAreaField, IntegerField, RadioField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from flask_login import current_user
from models import List
from flask import session

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

class AddFlashcardForm(FlaskForm):
    word = StringField('New Word', validators=[DataRequired()])
    description = TextAreaField('Meanings & Sample Sentences', validators=[DataRequired()])
    # addToList = SelectMultipleField('Add to List', coerce=int)
    submit = SubmitField('Add new word')

    # def __init__(self, *args, **kwargs):
    #     super(AddFlashcardForm, self).__init__(*args, **kwargs)
    #     if current_user.is_authenticated:
    #         self.addToList.choices = [(l.id, l.listname) for l in current_user.lists]            
    #     else:
    #         guest = session.get('guest', None)
    #         if guest:
    #             self.addToList.choices = [(l.id, l.listname) for l in guest.lists]
    #             self.addToList.validators =[DataRequired()]

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
    description = TextAreaField('Meaning', validators=[DataRequired()])
    # Inlists = SelectMultipleField('In lists', coerce=int)
    submit = SubmitField('Update')

    # def __init__(self, *args, **kwargs):
    #     super(UpdateWordForm, self).__init__(*args, **kwargs)
    #     if current_user.is_authenticated:
    #         self.Inlists.choices = [(l.id, l.listname) for l in current_user.lists]
    #     else:
    #         guest = session.get('guest', None)
    #         if guest:
    #             self.Inlists.choices = [(l.id, l.listname) for l in guest.lists]
        

# class BulkEditForm(FlaskForm):
#     flashcards = set()
#     inList = SelectMultipleField('Change List', coerce=int)
#     add = SubmitField("Add")
#     remove = SubmitField('Remove')

#     def __init__(self, *args, **kwargs):
#         super(BulkEditForm, self).__init__(*args, **kwargs)
#         if current_user.is_authenticated:
#             self.inList.choices = [(l.id, l.listname) for l in current_user.lists]

#     def addFlashCards(self, wordList):
#         for w in wordList:
#             wordId = f'flashcard_{w.id}'
#             checkbox = BooleanField(w.word)
#             setattr(BulkEditForm, wordId, checkbox)
#             self.flashcards.add(wordId)
    
#     def clearFlashcards(self):
#         self.flashcards = None
        

   
