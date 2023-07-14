from flask import Blueprint, render_template, redirect, url_for, request
from models import User, Word, List
from forms import AddVocabularyForm, AddListForm
from app import db


guest_bp = Blueprint('guest', __name__)

