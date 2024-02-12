from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_cors import CORS
import os

# Create the flask app
app = Flask(__name__)
cors = CORS(app)

# Instantiate SQLAlchemy to handle db process
db = SQLAlchemy()

# Instantiate Bcrypt to handle password hashing
bcrypt = Bcrypt()

# Instantiate LoginManager to handle user login
login_manager = LoginManager()

# Load configuration from config.cfg
app.config.from_pyfile('config.cfg')

try:
    if os.environ['FLASK_ENV'] == 'testing':
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_database.db'
except:
    print("Defaulting to production environment")
    
app.config['SECRET_KEY']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']

with app.app_context():
    db.init_app(app)
    from .models import PredEntry, User
    db.create_all()
    db.session.commit()
    print("Database created")

if __name__ == '__main__':
    # Run the app
    app.run(debug=True)

# Run the files routes.py
from application import routes