from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import LoginManager
from flask_session import Session
from datetime import timedelta




app = Flask(__name__)
app.config['SECRET_KEY'] = 'guesswhat'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False 

app.config['SESSION_TYPE'] = 'filesystem'  
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

root_folder = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(root_folder, 'DB_flashcards.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)



import models
from routes.login_routes import login_bp
from routes.user_routes import user_bp
from routes.guest_routes import guest_bp
app.register_blueprint(login_bp)
app.register_blueprint(user_bp)
app.register_blueprint(guest_bp)

Session(app)



# with app.app_context():
#     db.create_all()